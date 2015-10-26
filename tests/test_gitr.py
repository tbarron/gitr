#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_gitr
----------------------------------

Tests for `gitr` module.
"""
import docopt
import git
import os
import pexpect
import pytest
import setuptools
import shlex
import subprocess
import unittest

import gitr
from gitr import gitr as app
from gitr import tbx


# -----------------------------------------------------------------------------
def test_vu_on_tmt(tmpdir):
    """
    old is None, target exists, but is empty
    exp: write standard version expression to target
    """
    pytest.dbgfunc()
    trg = tmpdir.join('version.py')
    trg.write('')
    with tbx.chdir(tmpdir.strpath):
        gitr.version_update(trg.strpath, ['9', '8', '7'])
    assert tbx.contents(trg.strpath) == "__version__ = '9.8.7'\n"


# -----------------------------------------------------------------------------
def test_vu_on_tns(tmpdir):
    """
    old is None, target does not exist
    exp: write standard version expression to target
    """
    pytest.dbgfunc()
    trg = tmpdir.join('version.py')
    with tbx.chdir(tmpdir.strpath):
        gitr.version_update(trg.strpath, ['9', '8', '7'])
    assert tbx.contents(trg.strpath) == "__version__ = '9.8.7'\n"


# -----------------------------------------------------------------------------
def test_vu_on_tfl(tmpdir):
    """
    old is None, target is not empty
    exp: 'Don't know where to put '<news>' in '<c>''
    """
    pytest.dbgfunc()
    trg = tmpdir.join('version.py')
    nov = 'The quick brown fox and all that'
    trg.write(nov)
    with tbx.chdir(tmpdir.strpath):
        with pytest.raises(SystemExit) as e:
            gitr.version_update(trg.strpath, ['9', '8', '7'])
        assert ''.join(["Don't know where to put ",
                        "'9.8.7' in '{}'".format(nov)]) in str(e)


# -----------------------------------------------------------------------------
def test_vu_os_tmt(tmpdir):
    """
    old is not None, target is empty
    exp: 'Can't update '<olds>' in an empty file'
    """
    pytest.dbgfunc()
    trg = tmpdir.join('version.py')
    oldv = ['9', '8', '6']
    newv = oldv[0:2] + ['7']
    trg.write('')
    with tbx.chdir(tmpdir.strpath):
        with pytest.raises(SystemExit) as e:
            gitr.version_update(trg.strpath, newv, oldv)
        assert ''.join(["Can't update ",
                        "'{}' ".format('.'.join(oldv)),
                        "in an empty file"]) in str(e)


# -----------------------------------------------------------------------------
def test_vu_os_tfl_op(tmpdir):
    """
    old is not None, target is not empty, old IS in target, non-standard
    exp: <olds> replaced with <news> in non-standard expression
    """
    pytest.dbgfunc()
    oldv = ['7', '3', '2', '32']
    newv = oldv[0:-1] + [str(int(oldv[-1])+1)]
    (os, ns) = ('.'.join(_) for _ in [oldv, newv])
    trg = tmpdir.join('fooble-de-bar')

    t = '"{}" is the version\n'
    (pre, post) = (t.format(_) for _ in [os, ns])
    trg.write(pre)
    with tbx.chdir(tmpdir.strpath):
        gitr.version_update(trg.basename, newv, oldv)
        assert post in tbx.contents(trg.basename)


# -----------------------------------------------------------------------------
def test_vu_os_tfl_onp(tmpdir):
    """
    old is not None, target is not empty, old is not in target
    exp: '<olds>' not found in '<c>'
    """
    pytest.dbgfunc()
    oldv = ['7', '3', '2', '32']
    newv = oldv[0:-1] + [str(int(oldv[-1])+1)]
    (os, ns) = ('.'.join(_) for _ in [oldv, newv])
    trg = tmpdir.join('fooble-de-bar')

    t = '"sizzle" is the version'
    (pre, post) = (t.format(_) for _ in [os, ns])
    trg.write(pre)
    exp = "'{}' not found in '{}'".format(os, pre)
    with tbx.chdir(tmpdir.strpath):
        with pytest.raises(SystemExit) as e:
            gitr.version_update(trg.basename, newv, oldv)
        assert exp in str(e)


# -----------------------------------------------------------------------------
def test_vi_major():
    """
    iv = ['7', '19', '23']
    opts = {'--major': True}
    rv = ['8', '0', '0']
    """
    pytest.dbgfunc()
    exp = ['8', '0', '0']
    assert exp == gitr.version_increment(['7', '19', '23'],
                                         {'--major': True})


# -----------------------------------------------------------------------------
def test_vi_minor():
    """
    iv = ['7', '19', '23']
    opts = {'--minor': True}
    rv = ['7', '20', '0']
    """
    pytest.dbgfunc()
    exp = ['7', '20', '0']
    assert exp == gitr.version_increment(['7', '19', '23'],
                                         {'--minor': True})


# -----------------------------------------------------------------------------
def test_vi_patch():
    """
    iv = ['7', '19', '23']
    opts = {'--patch': True}
    rv = ['7', '19', '24']
    """
    pytest.dbgfunc()
    exp = ['7', '19', '24']
    assert exp == gitr.version_increment(['7', '19', '23'],
                                         {'--patch': True})


# -----------------------------------------------------------------------------
def test_vi_xbuild():
    """
    iv = ['7', '19', '23']
    opts = {'--build': True}
    rv = ['7', '19', '23', '1']
    """
    pytest.dbgfunc()
    exp = ['7', '19', '23', '1']
    assert exp == gitr.version_increment(['7', '19', '23'],
                                         {'--build': True})


# -----------------------------------------------------------------------------
def test_vi_ibuild(tmpdir):
    """
    iv = ['7', '19', '23', '4']
    opts = {'--build': True}
    rv = ['7', '19', '23', '5']
    """
    pytest.dbgfunc()
    exp = ['7', '19', '23', '5']
    assert exp == gitr.version_increment(['7', '19', '23', '4'],
                                         {'bv': True})


# -----------------------------------------------------------------------------
def test_vi_short(tmpdir):
    """
    iv = ['7', '19']
    opts = {'--build': True}
    sys.exit('7.19' is not a recognized version format)
    """
    pytest.dbgfunc()
    exp = "'7.19' is not a recognized version format"
    with pytest.raises(SystemExit) as e:
        res = gitr.version_increment(['7', '19'], {'bv': True})
        assert exp in str(e)


# -----------------------------------------------------------------------------
def test_vi_long(tmpdir):
    """
    iv = ['7', '19', 'foo', 'sample', 'wokka']
    opts = {'--build': True}
    sys.exit('7.19.foo.sample.wokka' is not a recognized version format)
    """
    pytest.dbgfunc()
    exp = "'7.19.foo.sample.wokka' is not a recognized version format"
    with pytest.raises(SystemExit) as e:
        res = gitr.version_increment(['7', '19'], {'bv': True})
        assert exp in str(e)


# -----------------------------------------------------------------------------
def test_bv_nofile_noarg(tmpdir):
    """
    pre: nothing
    gitr bv
    post: exception('version.py not found')
    """
    pytest.dbgfunc()
    with tbx.chdir(tmpdir.strpath):
        with pytest.raises(SystemExit) as e:
            gitr.gitr_bv({'bv': True})
    assert 'version.py not found' in str(e)


# -----------------------------------------------------------------------------
def test_bv_file_noarg_3(tmpdir):
    """
    pre: 2.7.3 in version.py
    gitr bv
    post: 2.7.3.1 in version.py
    """
    pytest.dbgfunc()
    vpath = tmpdir.join('version.py')
    vpath.write('__version__ = "2.7.3"\n')
    with tbx.chdir(tmpdir.strpath):
        gitr.gitr_bv({'bv': True})
    r = vpath.read()
    assert '2.7.3.1' in r


# -----------------------------------------------------------------------------
def test_bv_file_noarg_4(tmpdir):
    """
    pre: 2.7.3.8 in version.py
    gitr bv
    post: 2.7.3.9 in version.py
    """
    pytest.dbgfunc()
    vpath = tmpdir.join('version.py')
    vpath.write('__version__ = "2.7.3.8"\n')
    with tbx.chdir(tmpdir.strpath):
        gitr.gitr_bv({'bv': True})
    r = vpath.read()
    assert '2.7.3.9' in r


# -----------------------------------------------------------------------------
def test_bv_nofile_fnarg(tmpdir):
    """
    pre: nothing
    gitr bv a/b/flotsam
    post: '0.0.0' in a/b/flotsam
    """
    pytest.dbgfunc()
    dpath = tmpdir.join('a/b')
    bvpath = dpath.join('flotsam')
    assert not os.path.exists(bvpath.strpath)
    with tbx.chdir(tmpdir.strpath):
        gitr.gitr_bv({'bv': True, '<path>': bvpath.strpath})
    assert os.path.exists(bvpath.strpath)
    assert '0.0.0' in tbx.contents(bvpath.strpath)


# -----------------------------------------------------------------------------
def test_bv_nofile_major(tmpdir):
    """
    pre: nothing
    gitr bv --major
    post: exception('version.py not found')
    """
    pytest.fail('construction')


# -----------------------------------------------------------------------------
def test_bv_nofile_major_fn(tmpdir):
    """
    pre: nothing
    gitr bv --major frooble
    post: exception('frooble not found')
    """
    pytest.fail('construction')


# -----------------------------------------------------------------------------
@pytest.fixture
def already_setup(tmpdir, request):
    """
    Setup for 'already_staged' tests
    """
    pytest.this = {}
    rname = request.function.__name__
    target = {'test_bv_already_staged_default': 'version.py',
              'test_bv_already_staged_explicit': 'boodle',
              'test_bv_already_bumped_default': 'version.py',
              'test_bv_already_bumped_explicit': 'frobnicate'}[rname]
    pytest.this['target'] = target
    t = tmpdir.join(target)
    with tbx.chdir(tmpdir.strpath):
        # init the repo
        r = git.Repo.init(tmpdir.strpath)
        # create the first target and commit it
        t.write('__version__ = "0.0.0"\n')
        r.git.add(target)
        r.git.commit(a=True, m='First commit')
        # update target and stage the update
        t.write('__version__ = "0.0.0.1"\n')
        if 'staged' in rname:
            r.git.add(target)


# -----------------------------------------------------------------------------
def test_bv_already_bumped_default(tmpdir, already_setup):
    """
    If 'version.py' is already staged, don't update it
    """
    pytest.dbgfunc()
    v = pytest.this['target']
    with tbx.chdir(tmpdir.strpath):
        pre = tbx.contents(v)
        with pytest.raises(SystemExit) as e:
            gitr.gitr_bv({'bv': True, '<path>': None})
        post = tbx.contents(v)
    assert '{} is already bumped'.format(v) in str(e)
    assert pre == post


# -----------------------------------------------------------------------------
def test_bv_already_bumped_explicit(tmpdir, already_setup):
    """
    If an explicit target is already staged, don't update it
    """
    pytest.dbgfunc()
    v = pytest.this['target']
    with tbx.chdir(tmpdir.strpath):
        pre = tbx.contents(v)
        with pytest.raises(SystemExit) as e:
            gitr.gitr_bv({'bv': True, '<path>': v})
        post = tbx.contents(v)
    assert '{} is already bumped'.format(v) in str(e)
    assert pre == post


# -----------------------------------------------------------------------------
def test_bv_already_staged_default(tmpdir, already_setup):
    """
    If 'version.py' is already staged, don't update it
    """
    pytest.dbgfunc()
    v = pytest.this['target']
    with tbx.chdir(tmpdir.strpath):
        pre = tbx.contents(v)
        with pytest.raises(SystemExit) as e:
            gitr.gitr_bv({'bv': True, '<path>': None})
        post = tbx.contents(v)
    assert '{} is already bumped'.format(v) in str(e)
    assert pre == post


# -----------------------------------------------------------------------------
def test_bv_already_staged_explicit(tmpdir, already_setup):
    """
    If an explicit target is already staged, don't update it
    """
    pytest.dbgfunc()
    v = pytest.this['target']
    with tbx.chdir(tmpdir.strpath):
        pre = tbx.contents(v)
        with pytest.raises(SystemExit) as e:
            gitr.gitr_bv({'bv': True, '<path>': v})
        post = tbx.contents(v)
    assert '{} is already bumped'.format(v) in str(e)
    assert pre == post


# -----------------------------------------------------------------------------
def test_bv_file_major_3(tmpdir):
    """
    pre: '7.4.3' in version.py
    gitr bv --major
    post: '8.0.0' in version.py
    """
    pytest.fail('construction')


# -----------------------------------------------------------------------------
def test_bv_file_major_3_fn(tmpdir):
    """
    pre: '7.4.3' in splack
    gitr bv --major splack
    post: '8.0.0' in splack
    """
    pytest.fail('construction')


# -----------------------------------------------------------------------------
def test_bv_nofile_major_3_fn(tmpdir):
    """
    pre: '7.4.3' in splack
    gitr bv --major flump
    post: exception('flump not found')
    """
    pytest.fail('construction')


# -----------------------------------------------------------------------------
def test_bv_file_major_4(tmpdir):
    """
    pre: '1.0.0.17' in version.py
    gitr bv --major
    post: '2.0.0' in version.py
    """
    pytest.fail('construction')


# -----------------------------------------------------------------------------
def test_bv_nofile_minor(tmpdir):
    """
    pre: nothing
    gitr bv --minor
    post: exception('version.py not found')
    """
    pytest.fail('construction')


# -----------------------------------------------------------------------------
def test_bv_file_minor_3(tmpdir):
    """
    pre: '3.3.2' in version.py
    gitr bv --minor
    post: '3.4.0' in version.py
    """
    pytest.fail('construction')


# -----------------------------------------------------------------------------
def test_bv_file_minor_4(tmpdir):
    """
    pre: '3.3.2.7' in version.py
    gitr bv --minor
    post: '3.4.0' in version.py
    """
    pytest.fail('construction')


# -----------------------------------------------------------------------------
def test_bv_file_minor_3_fn(tmpdir):
    """
    pre: '3.3.2' in foo/bar/setup.py
    gitr bv --minor foo/bar/setup.py
    post: '3.4.0' in foo/bar/setup.py
    """
    pytest.fail('construction')


# -----------------------------------------------------------------------------
def test_bv_file_minor_4_fn(tmpdir):
    """
    pre: '3.3.2.7' in version.py
    gitr bv --minor frockle
    post: '3.3.2.7' in version.py, exception('frockle not found')
    """
    pytest.fail('construction')

# -----------------------------------------------------------------------------
def test_bv_nofile_patch(tmpdir):
    """
    pre: nothing
    gitr bv --patch
    post: exception('version.py not found')
    """
    pytest.fail('construction')

# -----------------------------------------------------------------------------
def test_bv_file_patch_3(tmpdir):
    """
    pre: '1.3.2' in version.py
    gitr bv --patch
    post: '1.3.3' in version.py
    """
    pytest.fail('construction')


# -----------------------------------------------------------------------------
def test_bv_file_patch_4(tmpdir):
    """
    pre: '1.3.2.7' in version.py
    gitr bv --patch
    post: '1.3.3' in version.py
    """
    pytest.fail('construction')


# -----------------------------------------------------------------------------
def test_bv_nofile_build(tmpdir):
    """
    Should raise exception
    pre: nothing
    gitr bv --build
    post: exception('version.py not found')
    """
    pytest.fail('construction')

# -----------------------------------------------------------------------------
def test_bv_file_build_3_fn(tmpdir):
    """
    pre: '7.8.9' in ./pkg/foobar
    gitr bv --build ./pkg/foobar
    post: '7.8.9.1' in ./pkg/foobar
    """
    pytest.fail('construction')

# -----------------------------------------------------------------------------
def test_bv_file_build_4(tmpdir):
    """
    pre: '1.2.3.4' in foo/bar/version.py
    gitr bv --build
    post: '1.2.3.5' in foo/bar/version.py
    """
    pytest.fail('construction')


# -----------------------------------------------------------------------------
def test_bv_nofile_set_fn(tmpdir):
    """
    pre: nothing
    gitr bv --set 4.3.2 frisbee
    post: "__version__ = '4.3.2'" in frisbee
    """
    pytest.fail('construction')


# -----------------------------------------------------------------------------
def test_bv_nofile_set_nofn(tmpdir):
    """
    pre: nothing
    gitr bv --set 1.0.19
    post: exception('version.py not found; need a file path argument')
    """
    pytest.fail('construction')


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
