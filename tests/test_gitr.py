#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_gitr
----------------------------------

Tests for `gitr` module.
"""
import docopt
import pytest
import unittest

from gitr import gitr


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
          }
    for k in kw:
        if k in rv:
            rv[k] = kw[k]
    return rv


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("argl", (["--help"],
                                  ["--version"],
                                  ["--debug"],
                                  ))
def test_docopt_help(argl):
    exp = docopt_exp()
    r = docopt.docopt(gitr.__doc__, argl)
    assert r == exp


if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
