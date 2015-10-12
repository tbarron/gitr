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
@pytest.mark.parametrize("argd", (({"--version": True}), 
                                  ({"--debug": True, 'dunn': True}),
                                  ))
def test_docopt(argd, capsys):
    """
    Test calls to docopt.docopt() that should be successful
    """
    pytest.dbgfunc()
    exp = docopt_exp(**argd)
    r = docopt.docopt(gitr.__doc__, argd.keys())
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
def run(cmd, input=None):
    """
    Run *cmd*, optionally passing string *input* to it on stdin, and return
    what the process writes to stdout
    """
    try:
        p = subprocess.Popen(shlex.split(cmd),
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        if input:
            p.stdin.write(input)
        (o, e) = p.communicate()
        if p.returncode == 0:
            rval = o
        else:
            rval = 'ERR:' + e
    except OSError as e:
        if 'No such file or directory' in str(e):
            rval = 'ERR:' + str(e)
        else:
            raise

    return rval

# -----------------------------------------------------------------------------
if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
