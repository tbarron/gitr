# -*- coding: utf-8 -*-
"""git helpers

gitr provides a collection of subcommands that I find useful in managing git
repositories.

Commands:
    gitr bv - will bump the version of the current repo as set in <path>
        (default = version.py). Options --major, --minor, --patch, --build
        (default) determine which component of the version value is bumped

    gitr dunn - will suggest what the next step to be done probably is based on
        the state of the repo.

    gitr depth - will report how far back a commitish is (number of commits
        between the one in question and the present as well as the age of the
        target committish)

    gitr flix - will find and report conflicts

    gitr hook - will list available hooks (--list), install and link a hook
        (--add), show a list of installed hooks (--show), and remove hooks
        (--rm)

Usage:
    gitr (-h|--help|--version)
    gitr bv [(-d|--debug)] [(-q|--quiet)] [(--major|--minor|--patch|--build)] [<path>]
    gitr depth [(-d|--debug)] <commitish>
    gitr dunn [(-d|--debug)]
    gitr flix [(-d|--debug)] [<target>]
    gitr hook [(-d|--debug)] (--list|--show)
    gitr hook [(-d|--debug)] (--add|--rm) <hookname>

Options:
    -h --help        Provide help info (display this document)
    -d --debug       Run under the debugger
    --version        Show version
    --list           List git hooks available to install
    --show           List installed git hooks
    --add            Add a hook by name
    --rm             Remove a hook by name

Arguments
    <commitish>      which object in the commit chain to check
    <hookname>       which hook to add or remove
    <path>           path for version info
    <target>         which file to examine for conflicts
"""

import os
import pdb
import re
import sys

import docopt
import git

import tbx
import version

__author__ = 'Tom Barron'
__email__ = 'tusculum@gmail.com'
__version__ = version.__version__

# -----------------------------------------------------------------------------
def main():
    """Entrypoint
    """
    opts = docopt.docopt(sys.modules[__name__].__doc__)
    if opts['--debug']:
        pdb.set_trace()

    if opts['--version']:
        sys.exit(version.__version__)

    dispatch(opts)


# -----------------------------------------------------------------------------
def dispatch(opts):
    """
    Based on the contents of *opts*, figure out what to do, introspect the
    module, and call the appropriate function.
    """
    targl = [_ for _ in opts if _[0] not in ['-', '<'] and opts[_]]
    funcname = '_'.join(['gitr', targl[0]])
    func = getattr(sys.modules[__name__], funcname)
    func(opts)


# -----------------------------------------------------------------------------
def gitr_bv(opts):
    """bv - bump version

    If multiple matches are found, only the first is updated
    """
    for a, b in [('--major', '--minor'),
                 ('--major', '--patch'),
                 ('--major', '--build'),
                 ('--minor', '--patch'),
                 ('--minor', '--build'),
                 ('--patch', '--build'),
                 ]:
        if opts.get(a, False) and opts.get(b, False):
            sys.exit('{0} and {1} are mutually exclusive'.format(a, b))

    tl = []
    target = opts.get('<path>', 'version.py') or 'version.py'
    if not os.path.exists(target):
        if '/' in target:
            tdir = tbx.dirname(target)
            if not os.path.exists(tdir):
                os.makedirs(tdir)
            version_update(target, ['0', '0', '0'])
            if opts.get('-q', False) or opts.get('--quiet', False):
                msg = ""
            else:
                msg = "{0} is not in git -- no diff available".format(target)
            sys.exit(msg)
        else:
            for r,d,f in os.walk('.'):
                if target in f:
                    tl.append(os.path.join(r, target))
            if tl == []:
                sys.exit('{0} not found'.format(target))
            target = tl[0]

    try:
        repo_root = find_repo_root()
        repo = git.Repo(repo_root)
        # compute the target path relative to the repo root
        repo_rel_target = os.path.relpath(os.path.abspath(target), repo_root)
        s = repo.git.status(repo_rel_target, porc=True)
        if s.strip() != '':
            sys.exit('{0} is already bumped'.format(repo_rel_target))
    except git.InvalidGitRepositoryError:
        sys.exit('{0} is not in a git repo'.format(target))

    with open(target, 'r') as f:
        content = f.read()
    q = re.findall(r'(\d+\.\d+\.\d+\.?\w*)', content)
    try:
        v = q[0]
    except NameError:
        sys.exit("No version found in {0} ['{1}']".format(target,
                                                        content))
    except IndexError:
        sys.exit("No version found in {0} ['{1}']".format(target,
                                                        content))

    iv = v.split('.')
    ov = version_increment(iv, opts)
    version_update(target, ov, iv)
    if not opts.get('-q', False) and not opts.get('--quiet', False):
        version_diff(repo, repo_rel_target)


# -----------------------------------------------------------------------------
def gitr_depth(opts):
    """Report the number of commits back to a given one and its age
    """
    print("Coming soon: report the number steps back to a given commit")


# -----------------------------------------------------------------------------
def gitr_dunn(opts):
    """Suggest the next step based on the state of the repository
    """
    print("Git'r Dunn: I dunno, maybe do a commit?")
    print("This is a temporary test entrypoint. It will become a plugin")
    print("Coming soon - an oracle to suggest the next step given the state")
    print("of the repository")


# -----------------------------------------------------------------------------
def gitr_flix(opts):
    """Report conflicts
    """
    print("Coming soon: conflict reporter")


# -----------------------------------------------------------------------------
def gitr_hook(opts):
    """Manage git hooks
    """
    print("Coming soon: hook management")


# -----------------------------------------------------------------------------
def find_repo_root():
    """
    Starting from '.', step up until we find a git repo. Return a git.Repo
    object initialized from it
    """
    loc = os.getcwd()
    clue = os.path.join(loc, '.git')
    while not os.path.isdir(clue) and 1 < len(loc):
        loc = os.path.dirname(loc)
        clue = os.path.join(loc, '.git')

    if os.path.isdir(clue):
        return(loc)
    else:
        raise git.InvalidGitRepositoryError(clue)


# -----------------------------------------------------------------------------
def version_diff(repo, target):
    """
    Get the diff of target and write it to stdout
    """
    txt = repo.git.diff(target)
    print(txt)


# -----------------------------------------------------------------------------
def version_increment(prev_l, opts):
    """
    Given a version array in *prev_l*, return the incremented value.
    """
    def strinc(num_s):
        """
        Increment a numeric string or blow up
        """
        return str(int(num_s) + 1)

    post_l = []
    if opts.get('--major', False):
        post_l = [strinc(prev_l[0]), '0', '0']
    elif opts.get('--minor', False):
        post_l = [prev_l[0], strinc(prev_l[1]), '0']
    elif opts.get('--patch', False):
        post_l = [prev_l[0], prev_l[1], strinc(prev_l[2])]
    else:
        post_l = prev_l[:]
        if 3 == len(post_l):
            post_l.append('1')
        elif 4 == len(post_l):
            post_l = prev_l[0:3] + [strinc(prev_l[3])]
        else:
            vers = '.'.join(post_l)
            sys.exit("'{0}' is not a recognized version format".format(vers))
    return post_l


# -----------------------------------------------------------------------------
def version_update(target, new, old=None):
    """
    Given a target path and new version array, write out the new version.

    If target is empty, write one line: '__version__ = '<new>''

    If old is not None, format and find it in target's contents and replace it
    with the new version.

    If target is not empty and old and is not found, fail and complain.
    """
    news = '.'.join(new)
    res = tbx.contents(target, default='')
    with open(target, 'w') as wable:
        if not old:
            if not res:
                wable.writelines(['"""\n',
                                  'Version\n',
                                  '"""\n',
                                  "__version__ = '{0}'\n".format(news)])
            else:
                sys.exit("Don't know where to put '{0}' in '{1}'".format(news,
                                                                         res))
        else:
            olds = '.'.join(old)
            if not res:
                sys.exit("Can't update '{0}' in an empty file".format(olds))
            elif olds in res:
                wable.write(res.replace(olds, news))
            else:
                sys.exit("'{0}' not found in '{1}'".format(olds, res))
