# -*- coding: utf-8 -*-
"""git helpers

gitr provides a collection of subcommands that I find useful in managing git
repositories.

Commands:
    gitr dunn - will suggest what the next step to be done probably is based on
        the state of the repo.

    gitr depth - will report how far back a commitish is (number of commits
        between the one in question and the present as well as the age of the
        target committish)

    gitr hook - will list available hooks (--list), install and link a hook
        (--add), show a list of installed hooks (--show), and remove hooks
        (--rm)

    gitr bv - will bump the version of the current repo as set in <path>
        (default = version.py). Options --major, --minor, --patch, --build
        (default) determine which component of the version value is bumped

    gitr flix - will find and report conflicts

    gitr nodoc - will find and report any functions in the current tree in .py
        files that have no docstring

    gitr dupl - will find and report any duplicate functions in the current
        tree in .py files

Usage:
    gitr dunn [(-d|--debug)]
    gitr depth [(-d|--debug)] <commitish>
    gitr hook [(-d|--debug)] (--list|--show)
    gitr hook [(-d|--debug)] (--add|--rm) <hookname>
    gitr bv [(-d|--debug)] [(--major|--minor|--patch|--build)] [<path>]
    gitr flix [(-d|--debug)] [<target>]
    gitr nodoc [(-d|--debug)]
    gitr dupl [(-d|--debug)]
    gitr (-h|--help|--version)

Options:
    -h --help        Provide help info (display this document)
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

import docopt
import git
import os
import pdb
import re
import sys

import tbx
import version

__author__ = 'Tom Barron'
__email__ = 'tusculum@gmail.com'
__version__ = version.__version__

# -----------------------------------------------------------------------------
def main():
    """Entrypoint
    """
    o = docopt.docopt(sys.modules[__name__].__doc__)
    if o['--debug'] or o['-d']:
        pdb.set_trace()

    if o['--version']:
        sys.exit(version.__version__)

    for k in (_ for _ in o.keys() if _[0] not in ('-', '<') and o[_]):
        f = getattr(sys.modules[__name__], "_".join(['gitr', k]))
        f(o)


# -----------------------------------------------------------------------------
def gitr_dunn(opts):
    """temporary entrypoint
    """
    print("Git'r Dunn: I dunno, maybe do a commit?")
    print("This is a temporary test entrypoint. It will become a plugin")


# -----------------------------------------------------------------------------
def gitr_bv(opts):
    """bv - bump version

    If multiple matches are found, only the first is updated
    """
    tl = []
    target = opts.get('<path>', 'version.py') or 'version.py'
    try:
        repo = git.Repo()
        s = repo.git.status(target, porc=True)
        if re.findall('M\s+{}'.format(target), s):
            sys.exit('{0} is already bumped'.format(target))
    except git.InvalidGitRepositoryError:
        sys.exit('{0} is not in a git repo'.format(target))
    if not os.path.exists(target):
        if '/' in target:
            td = tbx.dirname(target)
            if not os.path.exists(td):
                os.makedirs(td)
            version_update(target, ['0', '0', '0'])
            sys.exit("{0} is not in git -- no diff available".format(target))
        else:
            for r,d,f in os.walk('.'):
                if target in f:
                    tl.append(os.path.join(r, target))
            if tl == []:
                sys.exit('{} not found'.format(target))
            target = tl[0]

    with open(target, 'r') as f:
        content = f.read()
    q = re.findall('(.*?\W+)?(\d+\.\d+\.\d+\.?(\w+)?)(.*)?', content)
    try:
        v = q[0][1]
    except NameError:
        sys.exit("No version found in {} ['{}']".format(target,
                                                        content))
    except IndexError:
        sys.exit("No version found in {} ['{}']".format(target,
                                                        content))

    iv = v.split('.')
    ov = version_increment(iv, opts)
    version_update(target, ov, iv)
    version_diff(repo, target)


# -----------------------------------------------------------------------------
def version_diff(repo, target):
    """
    Get the diff of target and write it to stdout
    """
    txt = repo.git.diff(target)
    print(txt)


# -----------------------------------------------------------------------------
def version_increment(iv, opts):
    """
    Given a version array in *p*, return the incremented value.
    """
    def strinc(sn):
        """
        Increment a numeric string or blow up
        """
        return str(int(sn) + 1)

    ov = []
    if opts.get('--major', False):
        ov = [strinc(iv[0]), '0', '0']
        ov_final = '.'.join(ov)
    elif opts.get('--minor', False):
        ov = [iv[0], strinc(iv[1]), '0']
    elif opts.get('--patch', False):
        ov = [iv[0], iv[1], strinc(iv[2])]
    else:
        ov = iv[:]
        if 3 == len(ov):
            ov.append('1')
        elif 4 == len(ov):
            ov = iv[0:3] + [strinc(iv[3])]
        else:
            sys.exit("'{}' is not a recognized version format".format(ov))
    return ov


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
    c = tbx.contents(target, default='')
    with open(target, 'w') as f:
        if not old:
            if not c:
                f.write("__version__ = '{}'\n".format(news))
            else:
                sys.exit("Don't know where to put '{}' in '{}'".format(news, c))
        else:
            olds = '.'.join(old)
            if not c:
                sys.exit("Can't update '{}' in an empty file".format(olds))
            elif olds in c:
                f.write(c.replace(olds, news))
            else:
                sys.exit("'{}' not found in '{}'".format(olds, c))
