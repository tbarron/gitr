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

    gitr bv - will bump the version of the current repo, assumed to be in
        version.py

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
    gitr bv [(-d|--debug)] [<part>]
    gitr flix [(-d|--debug)] [<filename>]
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
"""

import docopt
import pdb
import sys

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
        f(sys.argv[2:])


# -----------------------------------------------------------------------------
def gitr_dunn(args):
    """temporary entrypoint
    """
    print("Git'r Dunn: I dunno, maybe do a commit?")
    print("This is a temporary test entrypoint. It will become a plugin")
