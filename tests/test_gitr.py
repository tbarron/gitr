#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_gitr
----------------------------------

Tests for `gitr` module.
"""
import docopt
import pexpect
import pytest
import shlex
import subprocess
import unittest

import gitr
from gitr import gitr as app
from gitr import tbx


# -----------------------------------------------------------------------------
    """


# -----------------------------------------------------------------------------
def test_docopt_help(capsys):
    """
    Calling docopt.docopt() with '--help' in the arg list
    """
    pytest.dbgfunc()
    exp = docopt_exp(help=True)
    with pytest.raises(SystemExit):
        r = docopt.docopt(gitr.__doc__, ['--help'])
    o, e = capsys.readouterr()
    for k in exp:
        assert k in o


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("argd", ({"--version": True, "flix": True}, 
                                  {"--debug": True},
                                  {"dunn": True,
                                   "<hookname>": 'pre-commit.ver'},
                                  {"depth": True,},
                                  {"hook": True,
                                   "--list": True,
                                   "<filename>": 'froobob'},
                                  {"hook": True,
                                   "--show": True,
                                   "<filename>": 'froobob'},
                                  {"hook": True, "--add": True,},
                                  {"hook": True, "--rm": True,},
                                  {"bv": True, "--version": True},
                                  {"flix": True, "<hookname>": 'summer'},
                                  {"nodoc": True, "--version": True},
                                  {"dupl": True, "--version": True},
                                  ))
def test_docopt_raises(argd, capsys):
    """
    Test calls to docopt.docopt() that should be successful
    """
    pytest.dbgfunc()
    exp = docopt_exp(**argd)
    with pytest.raises(docopt.DocoptExit) as e:
        r = docopt.docopt(gitr.__doc__, argd.keys())
    assert 'Usage:' in str(e)


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("argd", ({"--version": True}, 
                                  {'dunn': True, "--debug": True},
                                  {'dunn': True,},
                                  {'depth': True, "--debug": True,
                                   '<commitish>': 'HEAD~7',},
                                  {'hook': True, '--list': True},
                                  {'hook': True, '--show': True},
                                  {'hook': True, '--add': True,
                                   '<hookname>': 'bobble-dee-boop'},
                                  {'hook': True, '--rm': True,
                                   '<hookname>': 'bobble-dee-boop'},
                                  {'bv': True, '-d': True,
                                   '<part>': 'patch'},
                                  {'bv': True, '-d': True,},
                                  {'flix': True, '-d': True,
                                   '<filename>': 'foobar'},
                                  {'flix': True, '-d': True,},
                                  {'nodoc': True, "--debug": True},
                                  {'nodoc': True,},
                                  {'dupl': True, "--debug": True},
                                  {'dupl': True,},
                                  ))
def test_docopt(argd, capsys):
    """
    Test calls to docopt.docopt() that should be successful
    """
    pytest.dbgfunc()
    exp = docopt_exp(**argd)
    argl = []
    for k in argd:
        if argd[k] == True:
            argl.append(k)
        elif argd[k] is not None:
            argl.append(argd[k])
    r = docopt.docopt(gitr.__doc__, argl)
    assert r == exp


# -----------------------------------------------------------------------------
def test_pydoc_gitr():
    """
    Verify the behavior of running 'pydoc gitr'
    """
    pytest.dbgfunc()
    r = run("pydoc gitr")
    z = docopt_exp()
    for k in z:
        assert k in r


# -----------------------------------------------------------------------------
def docopt_exp(**kw):
    """Default dict expected back from docopt
    """
    rv = {'--debug': False,
          '--help': False,
          '--version': False,
          '-d': False,
          'flix': False,
          '<filename>': None,
          'nodoc': False,
          'dunn': False,
          'depth': False,
          '<commitish>': None,
          'bv': False,    # bump version
          '<part>': None,
          'hook': False,
          '--add': False,
          '<hookname>': None,
          '--list': False,
          '--show': False,
          '--rm': False,
          'dupl': False
          }
    for k in kw:
        if k in rv:
            rv[k] = kw[k]
    return rv


# -----------------------------------------------------------------------------
if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
