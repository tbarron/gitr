#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_gitr
----------------------------------

Tests for `gitr` module.
"""
# pylint: disable=locally-disabled,too-many-lines,redefined-outer-name
# pylint: disable=locally-disabled,unused-argument
import os
import pydoc
import sys
import unittest

import docopt
import git
import pytest

import gitr
from gitr import tbx


# -----------------------------------------------------------------------------
def test_bv_norepo(cb_basic_fixture, tmpdir):
    """
    pre: nothing
    gitr bv
    post: exception('version.py is not in a git repo')
    """
    bfm = pytest.basic_fx
    vfile = tmpdir.join(bfm['defname'])
    with tbx.chdir(tmpdir.strpath):
        vfile.write(bfm['template'].format('0.0.0'))
        with pytest.raises(SystemExit) as err:
            gitr.gitr_bv({'bv': True})
    assert bfm['notrepo'].format(bfm['defname']) in str(err)


# -----------------------------------------------------------------------------
def test_bv_nofile_noarg(cb_basic_fixture, tmpdir):
    """
    pre: nothing
    gitr bv
    post: exception('version.py not found')
    """
    bfm = pytest.basic_fx
    with tbx.chdir(tmpdir.strpath):
        git.Repo.init(tmpdir.strpath)
        with pytest.raises(SystemExit) as err:
            gitr.gitr_bv({'bv': True})
    assert bfm['notfound'].format(bfm['defname']) in str(err)


# -----------------------------------------------------------------------------
def test_bv_file_noarg_3(cb_basic_fixture, tmpdir, capsys):
    """
    pre: 2.7.3 in version.py
    gitr bv
    post: 2.7.3.1 in version.py
    """
    bfm = pytest.basic_fx
    pre, post = ('2.7.3', '2.7.3.1')
    vpath = tmpdir.join(bfm['defname'])
    vpath.write(bfm['template'].format(pre))
    repo = git.Repo.init(tmpdir.strpath)
    with tbx.chdir(tmpdir.strpath):
        repo.git.add(vpath.basename)
        repo.git.commit(m='inception')
        gitr.gitr_bv({'bv': True})
        bv_verify_diff(bfm['template'], pre, post, capsys.readouterr())
    assert post in vpath.read()


# -----------------------------------------------------------------------------
def test_bv_dir_nofile(cb_basic_fixture, tmpdir):
    """
    pre: '/' in target; dirname(target) exists; target does not
    gitr bv <target-path>
    post: no traceback
    """
    bfm = pytest.basic_fx
    (sub, trg) = ('sub', 'trg')
    sub_lp = tmpdir.join(sub).ensure(dir=True)
    trg_lp = sub_lp.join(trg)
    rel = '{0}/{1}'.format(sub, trg)
    git.Repo.init(tmpdir.strpath)
    with tbx.chdir(tmpdir.strpath):
        with pytest.raises(SystemExit) as err:
            gitr.gitr_bv({'bv': True, '<path>': rel})
            assert bfm['nodiff'].format(rel) in str(err)
    assert "'0.0.0'" in trg_lp.read()


# -----------------------------------------------------------------------------
def test_bv_file_noarg_4(cb_basic_fixture, tmpdir, capsys):
    """
    pre: 2.7.3.8 in version.py
    gitr bv
    post: 2.7.3.9 in version.py
    """
    bfm = pytest.basic_fx
    pre, post = ('2.7.3.8', '2.7.3.9')
    vpath = tmpdir.join(bfm['defname'])
    vpath.write(bfm['template'].format(pre))
    repo = git.Repo.init(tmpdir.strpath)
    with tbx.chdir(tmpdir.strpath):
        repo.git.add(vpath.basename)
        repo.git.commit(m='inception')
        gitr.gitr_bv({'bv': True})
        bv_verify_diff(bfm['template'], pre, post, capsys.readouterr())
    assert post in vpath.read()


# -----------------------------------------------------------------------------
def test_bv_nofile_fnarg(cb_basic_fixture, tmpdir):
    """
    pre: nothing
    gitr bv a/b/flotsam
    post: '0.0.0' in a/b/flotsam
    """
    bfm = pytest.basic_fx
    dpath = tmpdir.join('a/b')
    bvpath = dpath.join('flotsam')
    assert not bvpath.exists()
    git.Repo.init(tmpdir.strpath)
    with tbx.chdir(tmpdir.strpath):
        rpath = bvpath.relto(tmpdir)
        with pytest.raises(SystemExit) as err:
            gitr.gitr_bv({'bv': True, '<path>': rpath})
        assert bfm['nodiff'].format(rpath) in str(err)
    assert bvpath.exists()
    assert "'0.0.0'" in bvpath.read()


# -----------------------------------------------------------------------------
def test_bv_nofile_major(cb_basic_fixture, tmpdir):
    """
    pre: nothing
    gitr bv --major
    post: exception('version.py not found')
    """
    bfm = pytest.basic_fx
    with tbx.chdir(tmpdir.strpath):
        git.Repo.init(tmpdir.strpath)
        with pytest.raises(SystemExit) as err:
            gitr.gitr_bv({'bv': True, '--major': True})
        assert bfm['notfound'].format(bfm['defname']) in str(err)


# -----------------------------------------------------------------------------
def test_bv_nofile_major_fn(cb_basic_fixture, tmpdir):
    """
    pre: nothing
    gitr bv --major frooble
    post: exception('frooble not found')
    """
    bfm = pytest.basic_fx
    vname = 'frooble'
    with tbx.chdir(tmpdir.strpath):
        git.Repo.init(tmpdir.strpath)
        with pytest.raises(SystemExit) as err:
            gitr.gitr_bv({'bv': True, '--major': True, '<path>': vname})
        assert bfm['notfound'].format(vname) in str(err)


# -----------------------------------------------------------------------------
def test_bv_already_bumped_default(cb_basic_fixture, tmpdir, already_setup):
    """
    If 'version.py' is already bumped, don't update it
    """
    bfm = pytest.basic_fx
    vfile = pytest.this['target']
    with tbx.chdir(tmpdir.strpath):
        pre = tbx.contents(vfile)
        with pytest.raises(SystemExit) as err:
            gitr.gitr_bv({'bv': True, '<path>': None})
        post = tbx.contents(vfile)
    assert bfm['already'].format(vfile) in str(err)
    assert pre == post


# -----------------------------------------------------------------------------
def test_bv_already_bumped_deep(cb_basic_fixture, tmpdir, already_setup):
    """
    If 'version.py' is already bumped, don't update it
    """
    pytest.dbgfunc()
    bfm = pytest.basic_fx
    vfile = pytest.this['target']
    with tbx.chdir(tmpdir.strpath):
        pre = tbx.contents(vfile)
        with pytest.raises(SystemExit) as err:
            gitr.gitr_bv({'bv': True, '<path>': None})
        post = tbx.contents(vfile)
    assert bfm['already'].format(vfile) in str(err)
    assert pre == post


# -----------------------------------------------------------------------------
def test_bv_already_bumped_deep2(cb_basic_fixture, tmpdir, already_setup):
    """
    If 'version.py' is already bumped, don't update it
    """
    pytest.dbgfunc()
    bfm = pytest.basic_fx
    vfile = tmpdir.join(pytest.this['target'])
    with tbx.chdir(vfile.dirname):
        pre = tbx.contents(vfile.basename)
        with pytest.raises(SystemExit) as err:
            gitr.gitr_bv({'bv': True, '<path>': None})
        post = tbx.contents(vfile.basename)
    assert bfm['already'].format(pytest.this['target']) in str(err)
    assert pre == post


# -----------------------------------------------------------------------------
def test_bv_already_bumped_explicit(cb_basic_fixture, tmpdir, already_setup):
    """
    If an explicit target is already bumped, don't update it
    """
    bfm = pytest.basic_fx
    vfile = pytest.this['target']
    with tbx.chdir(tmpdir.strpath):
        pre = tbx.contents(vfile)
        with pytest.raises(SystemExit) as err:
            gitr.gitr_bv({'bv': True, '<path>': vfile})
        post = tbx.contents(vfile)
    assert bfm['already'].format(vfile) in str(err)
    assert pre == post


# -----------------------------------------------------------------------------
def test_bv_already_staged_default(cb_basic_fixture, tmpdir, already_setup):
    """
    If 'version.py' is already staged, don't update it
    """
    bfm = pytest.basic_fx
    vfile = pytest.this['target']
    with tbx.chdir(tmpdir.strpath):
        pre = tbx.contents(vfile)
        with pytest.raises(SystemExit) as err:
            gitr.gitr_bv({'bv': True, '<path>': None})
        post = tbx.contents(vfile)
    assert bfm['already'].format(vfile) in str(err)
    assert pre == post


# -----------------------------------------------------------------------------
def test_bv_already_staged_deep(cb_basic_fixture, tmpdir, already_setup):
    """
    If 'version.py' is already staged, don't update it
    """
    bfm = pytest.basic_fx
    vfile = pytest.this['target']
    with tbx.chdir(tmpdir.strpath):
        pre = tbx.contents(vfile)
        with pytest.raises(SystemExit) as err:
            gitr.gitr_bv({'bv': True, '<path>': None})
        post = tbx.contents(vfile)
    assert bfm['already'].format(vfile) in str(err)
    assert pre == post


# -----------------------------------------------------------------------------
def test_bv_already_staged_explicit(cb_basic_fixture, tmpdir, already_setup):
    """
    If an explicit target is already staged, don't update it
    """
    bfm = pytest.basic_fx
    vfile = pytest.this['target']
    with tbx.chdir(tmpdir.strpath):
        pre = tbx.contents(vfile)
        with pytest.raises(SystemExit) as err:
            gitr.gitr_bv({'bv': True, '<path>': vfile})
        post = tbx.contents(vfile)
    assert bfm['already'].format(vfile) in str(err)
    assert pre == post


# -----------------------------------------------------------------------------
def test_bv_file_major_3(cb_basic_fixture, tmpdir, capsys, repo_setup):
    """
    pre: '7.4.3' in version.py
    gitr bv --major --quiet
    post: '8.0.0' in version.py, nothing on stdout
    """
    # bfm = pytest.basic_fx
    pre, post = '7.4.3', '8.0.0'
    repo = pytest.this['repo']
    vfile = pytest.this['vname']
    vfile.write(pre)
    repo.git.commit(a=True, m='set version')
    with tbx.chdir(tmpdir.strpath):
        gitr.gitr_bv({'bv': True, '--major': True, '--quiet': True})
    assert post in vfile.read()
    assert 'M version.py' in repo.git.status(porc=True)
    stdo, _ = capsys.readouterr()
    assert stdo.strip() == ""


# -----------------------------------------------------------------------------
def test_bv_file_major_3_fn(cb_basic_fixture, tmpdir, capsys, repo_setup):
    """
    pre: '7.4.3' in splack
    gitr bv --major splack
    post: '8.0.0' in splack
    """
    bfm = pytest.basic_fx
    repo = pytest.this['repo']
    oth = pytest.this['other']
    pre, post = "7.4.3", "8.0.0"
    oth.write("__version__ = '{0}'\n".format(pre))
    repo.git.commit(a=True, m='set a version')
    with tbx.chdir(tmpdir.strpath):
        gitr.gitr_bv({'bv': True, '--major': True,
                      '<path>': oth.basename})
    assert bfm['template'].format(post) in oth.read()
    bv_verify_diff(bfm['template'], pre, post, capsys.readouterr())


# -----------------------------------------------------------------------------
def test_bv_nofile_major_3_fn(cb_basic_fixture, tmpdir, repo_setup):
    """
    pre: '7.4.3' in splack
    gitr bv --major flump
    post: exception('flump not found')
    """
    bfm = pytest.basic_fx
    pre = post = '7.4.3'
    repo = pytest.this['repo']
    nosuch = pytest.this['nosuch']
    oth = pytest.this['other']
    oth.write(bfm['template'].format(pre))
    repo.git.commit(a=True, m='set version')
    with tbx.chdir(tmpdir.strpath):
        with pytest.raises(SystemExit) as err:
            gitr.gitr_bv({'bv': True, '--major': True,
                          '<path>': nosuch.basename})
        assert bfm['notfound'].format(nosuch.basename) in str(err)
    assert bfm['template'].format(post) in oth.read()


# -----------------------------------------------------------------------------
def test_bv_file_major_4(cb_basic_fixture, tmpdir, capsys, repo_setup):
    """
    pre: '1.0.0.17' in version.py
    gitr bv --major
    post: '2.0.0' in version.py
    """
    bfm = pytest.basic_fx
    repo = pytest.this['repo']
    vfile = pytest.this['vname']
    pre, post = '1.0.0.17', '2.0.0'
    vfile.write(bfm['template'].format(pre))
    repo.git.commit(a=True, m='set version')
    with tbx.chdir(tmpdir.strpath):
        gitr.gitr_bv({'bv': True, '--major': True,
                      '<path>': vfile.basename})
        bv_verify_diff(bfm['template'], pre, post, capsys.readouterr())
    assert bfm['template'].format(post) in vfile.read()


# -----------------------------------------------------------------------------
def test_bv_nofile_minor(cb_basic_fixture, tmpdir, repo_setup):
    """
    pre: nothing
    gitr bv --minor
    post: exception('version.py not found')
    """
    bfm = pytest.basic_fx
    vfile = pytest.this['vname']
    vfile.remove()
    stash = pytest.this['q']
    stash['foo/bar/version.py']['locpath'].remove()
    with tbx.chdir(tmpdir.strpath):
        with pytest.raises(SystemExit) as err:
            gitr.gitr_bv({'bv': True, '--minor': True})
        assert bfm['notfound'].format(bfm['defname']) in str(err)


# -----------------------------------------------------------------------------
def test_bv_file_minor_3(cb_basic_fixture, tmpdir, capsys, repo_setup):
    """
    pre: '3.3.2' in version.py
    gitr bv --minor
    post: '3.4.0' in version.py
    """
    bfm = pytest.basic_fx
    pre, post = '3.3.2', '3.4.0'
    repo = pytest.this['repo']
    vfile = pytest.this['vname']
    vfile.write(bfm['template'].format(pre))
    repo.git.commit(a=True, m='first version')
    with tbx.chdir(tmpdir.strpath):
        gitr.gitr_bv({'bv': True, '--minor': True, '-q': True})
        stdo, _ = capsys.readouterr()
        assert stdo.strip() == ""
    assert bfm['template'].format(post) in vfile.read()


# -----------------------------------------------------------------------------
def test_bv_file_minor_4(cb_basic_fixture, tmpdir, capsys, repo_setup):
    """
    pre: '3.3.2.7' in version.py
    gitr bv --minor
    post: '3.4.0' in version.py
    """
    bfm = pytest.basic_fx
    repo = pytest.this['repo']
    vfile = pytest.this['vname']
    pre, post = "3.3.2.7", "3.4.0"
    vfile.write(bfm['template'].format(pre))
    repo.git.commit(a=True, m='first version')
    with tbx.chdir(tmpdir.strpath):
        gitr.gitr_bv({'bv': True, '--minor': True})
        bv_verify_diff("__version__ = '{0}'", pre, post,
                       capsys.readouterr())
    assert bfm['template'].format(post) in vfile.read()


# -----------------------------------------------------------------------------
def test_bv_file_minor_3_fn(cb_basic_fixture, tmpdir, capsys, repo_setup):
    """
    pre: '3.3.2' in foo/bar/setup.py
    gitr bv --minor foo/bar/setup.py
    post: '3.4.0' in foo/bar/setup.py
    """
    bfm = pytest.basic_fx
    repo = pytest.this['repo']
    # vfile = pytest.this['vname']
    dname = tmpdir.join('foo/bar').ensure(dir=True)
    setup = dname.join('setup.py')
    pre, post = "3.3.2", "3.4.0"
    setup.write(bfm['template'].format(pre))
    repo.git.add(setup.strpath)
    repo.git.commit(a=True, m='first version')
    with tbx.chdir(tmpdir.strpath):
        gitr.gitr_bv({'bv': True, '--minor': True,
                      '<path>': setup.relto(tmpdir)})
        bv_verify_diff(bfm['template'], pre, post, capsys.readouterr())
    assert bfm['template'].format(post) in setup.read()


# -----------------------------------------------------------------------------
def test_bv_file_minor_4_fn(cb_basic_fixture, tmpdir, repo_setup):
    """
    pre: '3.3.2.7' in version.py
    gitr bv --minor frockle
    post: '3.3.2.7' in version.py, exception('frockle not found')
    """
    bfm = pytest.basic_fx
    repo = pytest.this['repo']
    vfile = pytest.this['vname']
    fname = 'frockle'
    pre, _ = "3.3.2.7", "3.4.0"
    vfile.write(bfm['template'].format(pre))
    repo.git.commit(a=True, m='first version')
    with tbx.chdir(tmpdir.strpath):
        with pytest.raises(SystemExit) as err:
            gitr.gitr_bv({'bv': True, '--minor': True,
                          '<path>': fname})
        assert bfm['notfound'].format(fname) in str(err)


# -----------------------------------------------------------------------------
def test_bv_nofile_patch(cb_basic_fixture, tmpdir, repo_setup):
    """
    pre: nothing
    gitr bv --patch
    post: exception('version.py not found')
    """
    bfm = pytest.basic_fx
    vfile = pytest.this['vname']
    vfile.remove()
    stash = pytest.this['q']
    stash['foo/bar/version.py']['locpath'].remove()
    with tbx.chdir(tmpdir.strpath):
        with pytest.raises(SystemExit) as err:
            gitr.gitr_bv({'--patch': True})
        assert bfm['notfound'].format(vfile.basename) in str(err)


# -----------------------------------------------------------------------------
def test_bv_file_patch_3(cb_basic_fixture, tmpdir, repo_setup, capsys):
    """
    pre: '1.3.2' in version.py
    gitr bv --patch
    post: '1.3.3' in version.py
    """
    bfm = pytest.basic_fx
    pre, post = '1.3.2', '1.3.3'
    repo = pytest.this['repo']
    vfile = pytest.this['vname']
    vfile.write(bfm['template'].format(pre))
    repo.git.commit(a=True, m='first version')
    with tbx.chdir(tmpdir.strpath):
        gitr.gitr_bv({'bv': True, '--patch': True, '-q': True})
        stdo, _ = capsys.readouterr()
        assert stdo.strip() == ""
    assert bfm['template'].format(post) in vfile.read()



# -----------------------------------------------------------------------------
def test_bv_file_patch_4(cb_basic_fixture, tmpdir, capsys, repo_setup):
    """
    pre: '1.3.2.7' in version.py
    gitr bv --patch
    post: '1.3.3' in version.py
    """
    bfm = pytest.basic_fx
    repo = pytest.this['repo']
    vfile = pytest.this['vname']
    pre, post = "1.3.2.7", "1.3.3"
    vfile.write(bfm['template'].format(pre))
    repo.git.commit(a=True, m='first version')
    with tbx.chdir(tmpdir.strpath):
        gitr.gitr_bv({'bv': True, '--patch': True})
        bv_verify_diff(bfm['template'], pre, post, capsys.readouterr())
    assert bfm['template'].format(post) in vfile.read()


# -----------------------------------------------------------------------------
def test_bv_nofile_build(cb_basic_fixture, tmpdir, repo_setup):
    """
    Should raise exception
    pre: nothing
    gitr bv --build
    post: exception('version.py not found')
    """
    bfm = pytest.basic_fx
    vfile = pytest.this['vname']
    vfile.remove()
    stash = pytest.this['q']
    stash['foo/bar/version.py']['locpath'].remove()
    with tbx.chdir(tmpdir.strpath):
        with pytest.raises(SystemExit) as err:
            gitr.gitr_bv({'--build': True})
        assert bfm['notfound'].format(vfile.basename) in str(err)


# -----------------------------------------------------------------------------
def test_bv_file_build_3_fn(cb_basic_fixture, tmpdir, repo_setup):
    """
    pre: '7.8.9' in ./pkg/foobar
    gitr bv --build ./pkg/foobar
    post: '7.8.9.1' in ./pkg/foobar
    """
    # bfm = pytest.basic_fx
    repo = pytest.this['repo']
    pre, post = '7.8.9', '7.8.9.1'
    this = pytest.this['template']
    opn = 'foo/bar/other_name'
    oth = pytest.this['q'][opn]
    oth['locpath'].write(this.format(pre))
    repo.git.commit(a=True, m='version')
    with tbx.chdir(tmpdir.strpath):
        gitr.gitr_bv({'--build': True,
                      '<path>': opn})
    assert this.format(post) in oth['locpath'].read()


# -----------------------------------------------------------------------------
def test_bv_file_build_deep(cb_basic_fixture, tmpdir, repo_setup):
    """
    pre: '7.8.9' in ./pkg/foobar
    gitr bv --build ./pkg/foobar
    post: '7.8.9.1' in ./pkg/foobar
    """
    # bfm = pytest.basic_fx
    repo = pytest.this['repo']
    pre, post = '7.8.9', '7.8.9.1'
    this = pytest.this['template']
    opn = 'foo/bar/other_name'
    oth = pytest.this['q'][opn]
    oth['locpath'].write(this.format(pre))
    repo.git.commit(a=True, m='version')
    with tbx.chdir(oth['locpath'].dirname):
        gitr.gitr_bv({'--build': True,
                      '<path>': oth['locpath'].basename})
    assert this.format(post) in oth['locpath'].read()


# -----------------------------------------------------------------------------
def test_bv_file_build_4(cb_basic_fixture, tmpdir, capsys, repo_setup):
    """
    pre: '1.2.3.4' in foo/bar/version.py
    gitr bv --build
    post: '1.2.3.5' in foo/bar/version.py
    """
    # bfm = pytest.basic_fx
    repo = pytest.this['repo']
    pytest.this['vname'].remove()
    vpath = 'foo/bar/version.py'
    vfile = pytest.this['q'][vpath]
    pre, post = "1.2.3.4", "1.2.3.5"
    this = pytest.this['template']
    vfile['locpath'].write(this.format(pre))
    repo.git.commit(a=True, m='first version')
    with tbx.chdir(tmpdir.strpath):
        gitr.gitr_bv({'bv': True, '--build': True})
        bv_verify_diff(this, pre, post,
                       capsys.readouterr())


# -----------------------------------------------------------------------------
def test_bv_file_build_4_deep(cb_basic_fixture, tmpdir, capsys, repo_setup):
    """
    pre: '1.2.3.4' in foo/bar/version.py
    gitr bv --build
    post: '1.2.3.5' in foo/bar/version.py
    """
    pytest.dbgfunc()
    # bfm = pytest.basic_fx
    repo = pytest.this['repo']
    pytest.this['vname'].remove()
    vpath = 'foo/bar/version.py'
    vfile = pytest.this['q'][vpath]
    pre, post = "1.2.3.4", "1.2.3.5"
    this = pytest.this['template']
    vfile['locpath'].write(this.format(pre))
    repo.git.commit(a=True, m='first version')
    # with tbx.chdir(tmpdir.strpath):
    with tbx.chdir(vfile['locpath'].dirname):
        gitr.gitr_bv({'bv': True, '--build': True})
        bv_verify_diff(this, pre, post,
                       capsys.readouterr())


# -----------------------------------------------------------------------------
def test_bv_major_minor(cb_basic_fixture, tmpdir, repo_setup):
    """
    pre: nothing
    gitr bv --major --minor
    post: exception('--major and --minor are mutually exclusive')
    """
    bfm = pytest.basic_fx
    mx_opt1, mx_opt2 = '--major', '--minor'
    exp = bfm['mutex'].format(mx_opt1, mx_opt2)
    with tbx.chdir(tmpdir.strpath):
        with pytest.raises(SystemExit) as err:
            gitr.gitr_bv({mx_opt1: True, mx_opt2: True})
        assert exp in str(err)


# -----------------------------------------------------------------------------
def test_bv_major_patch(cb_basic_fixture, tmpdir):
    """
    pre: nothing
    gitr bv --major --patch
    post: exception('--major and --patch are mutually exclusive')
    """
    bfm = pytest.basic_fx
    mx_opt1, mx_opt2 = '--major', '--patch'
    exp = bfm['mutex'].format(mx_opt1, mx_opt2)
    with tbx.chdir(tmpdir.strpath):
        with pytest.raises(SystemExit) as err:
            gitr.gitr_bv({mx_opt1: True, mx_opt2: True})
        assert exp in str(err)


# -----------------------------------------------------------------------------
def test_bv_major_build(cb_basic_fixture, tmpdir):
    """
    pre: nothing
    gitr bv --major --build
    post: exception('--major and --build are mutually exclusive')
    """
    bfm = pytest.basic_fx
    mx_opt1, mx_opt2 = '--major', '--build'
    exp = bfm['mutex'].format(mx_opt1, mx_opt2)
    with tbx.chdir(tmpdir.strpath):
        with pytest.raises(SystemExit) as err:
            gitr.gitr_bv({mx_opt1: True, mx_opt2: True})
        assert exp in str(err)


# -----------------------------------------------------------------------------
def test_bv_minor_patch(cb_basic_fixture, tmpdir):
    """
    pre: nothing
    gitr bv --minor --patch
    post: exception('--minor and --patch are mutually exclusive')
    """
    bfm = pytest.basic_fx
    mx_opt1, mx_opt2 = '--minor', '--patch'
    exp = bfm['mutex'].format(mx_opt1, mx_opt2)
    with tbx.chdir(tmpdir.strpath):
        with pytest.raises(SystemExit) as err:
            gitr.gitr_bv({mx_opt1: True, mx_opt2: True})
        assert exp in str(err)


# -----------------------------------------------------------------------------
def test_bv_minor_build(cb_basic_fixture, tmpdir):
    """
    pre: nothing
    gitr bv --minor --build
    post: exception('--minor and --build are mutually exclusive')
    """
    bfm = pytest.basic_fx
    mx_opt1, mx_opt2 = '--minor', '--build'
    exp = bfm['mutex'].format(mx_opt1, mx_opt2)
    with tbx.chdir(tmpdir.strpath):
        with pytest.raises(SystemExit) as err:
            gitr.gitr_bv({mx_opt1: True, mx_opt2: True})
        assert exp in str(err)


# -----------------------------------------------------------------------------
def test_bv_patch_build(cb_basic_fixture, tmpdir):
    """
    pre: nothing
    gitr bv --patch --build
    post: exception('--patch and --build are mutually exclusive')
    """
    bfm = pytest.basic_fx
    mx_opt1, mx_opt2 = '--patch', '--build'
    exp = bfm['mutex'].format(mx_opt1, mx_opt2)
    with tbx.chdir(tmpdir.strpath):
        with pytest.raises(SystemExit) as err:
            gitr.gitr_bv({mx_opt1: True, mx_opt2: True})
        assert exp in str(err)


# -----------------------------------------------------------------------------
def test_docopt_help(capsys):
    """
    Calling docopt.docopt() with '--help' in the arg list
    """
    pytest.dbgfunc()
    exp = docopt_exp(help=True)
    with pytest.raises(SystemExit):
        docopt.docopt(gitr.__doc__, ['--help'])
    stdo, _ = capsys.readouterr()
    for k in exp:
        assert k in stdo


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
                                  {"flix": True, "--minor": True,
                                   "<hookname>": 'summer'},
                                 ))
def test_docopt_raises(argd, capsys):
    """
    Test calls to docopt.docopt() that should be successful
    """
    pytest.dbgfunc()
    argl = docopt_cmdl(argd)
    with pytest.raises(docopt.DocoptExit) as err:
        docopt.docopt(gitr.__doc__, argl)
    assert 'Usage:' in str(err)


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
                                   '<path>': 'patch'},
                                  {'bv': True, '--debug': True,},
                                  {'flix': True, '-d': True,
                                   '<target>': 'foobar'},
                                  {'flix': True, '-d': True,},
                                 ))
def test_docopt(argd, capsys):
    """
    Test calls to docopt.docopt() that should be successful
    """
    pytest.dbgfunc()
    exp = docopt_exp(**argd)
    argl = docopt_cmdl(argd)
    result = docopt.docopt(gitr.__doc__, argl)
    assert result == exp


# -----------------------------------------------------------------------------
def test_find_repo_root_deep(repo_setup, tmpdir):
    """
    repo is several levels up
    """
    sub = tmpdir.join('a/b/c').ensure(dir=True)
    with tbx.chdir(sub.strpath):
        assert tmpdir.strpath == gitr.find_repo_root()


# -----------------------------------------------------------------------------
def test_find_repo_root_not(tmpdir):
    """
    Not in a repo
    """
    with tbx.chdir(tmpdir.strpath):
        with pytest.raises(git.InvalidGitRepositoryError):
            gitr.find_repo_root()


# -----------------------------------------------------------------------------
def test_find_repo_root_shallow(repo_setup, tmpdir):
    """
    Current dir is the repo
    """
    with tbx.chdir(tmpdir.strpath):
        assert tmpdir.strpath == gitr.find_repo_root()


# -----------------------------------------------------------------------------
@pytest.mark.parametrize('subc', ['dunn',
                                  'depth',
                                  'flix',
                                  'hook',
                                 ])
def test_gitr_unimpl(subc, capsys):
    """
    gitr <subc> -> 'coming soon'
    """
    pytest.dbgfunc()
    func = getattr(gitr, 'gitr_' + subc)
    func({subc: True})
    stdo, _ = capsys.readouterr()
    assert 'Coming soon' in stdo


# -----------------------------------------------------------------------------
def test_pydoc_gitr(capsys):
    """
    Verify the behavior of running 'pydoc gitr'
    """
    pytest.dbgfunc()
    pydoc.help(gitr)
    stdo, _ = capsys.readouterr()
    exp = docopt_exp()
    for k in exp:
        assert k in stdo


# -----------------------------------------------------------------------------
def test_vi_major():
    """
    iv = ['7', '19', '23']
    opts = {'--major': True}
    rv = ['8', '0', '0']
    """
    pytest.dbgfunc()
    inp, exp = '7.19.23', '8.0.0'
    assert exp.split('.') == gitr.version_increment(inp.split('.'),
                                                    {'--major': True})


# -----------------------------------------------------------------------------
def test_vi_minor():
    """
    iv = ['7', '19', '23']
    opts = {'--minor': True}
    rv = ['7', '20', '0']
    """
    pytest.dbgfunc()
    inp, exp = '7.19.23', '7.20.0'
    assert exp.split('.') == gitr.version_increment(inp.split('.'),
                                                    {'--minor': True})


# -----------------------------------------------------------------------------
def test_vi_patch():
    """
    iv = ['7', '19', '23']
    opts = {'--patch': True}
    rv = ['7', '19', '24']
    """
    pytest.dbgfunc()
    inp, exp = '7.19.23', '7.19.24'
    assert exp.split('.') == gitr.version_increment(inp.split('.'),
                                                    {'--patch': True})


# -----------------------------------------------------------------------------
def test_vi_xbuild():
    """
    iv = ['7', '19', '23']
    opts = {'--build': True}
    rv = ['7', '19', '23', '1']
    """
    pytest.dbgfunc()
    inp, exp = '7.19.23', '7.19.23.1'
    assert exp.split('.') == gitr.version_increment(inp.split('.'),
                                                    {'--build': True})


# -----------------------------------------------------------------------------
def test_vi_ibuild(tmpdir):
    """
    iv = ['7', '19', '23', '4']
    opts = {'--build': True}
    rv = ['7', '19', '23', '5']
    """
    pytest.dbgfunc()
    inp, exp = '7.19.23.4', '7.19.23.5'
    assert exp.split('.') == gitr.version_increment(inp.split('.'),
                                                    {'bv': True})


# -----------------------------------------------------------------------------
def test_vi_short(cb_basic_fixture, tmpdir):
    """
    iv = ['7', '19']
    opts = {'--build': True}
    sys.exit('7.19' is not a recognized version format)
    """
    bfm = pytest.basic_fx
    inp = '7.19'
    exp = bfm['badform'].format(inp)
    with pytest.raises(SystemExit) as err:
        gitr.version_increment(inp.split('.'), {'bv': True})
    assert exp in str(err)


# -----------------------------------------------------------------------------
def test_vi_long(cb_basic_fixture, tmpdir):
    """
    iv = ['7', '19', 'foo', 'sample', 'wokka']
    opts = {'--build': True}
    sys.exit('7.19.foo.sample.wokka' is not a recognized version format)
    """
    bfm = pytest.basic_fx
    inp = '7.19.foo.sample.wokka'
    exp = bfm['badform'].format(inp)
    with pytest.raises(SystemExit) as err:
        gitr.version_increment(inp.split('.'), {'bv': True})
    assert exp in str(err)


# -----------------------------------------------------------------------------
def test_vu_on_tmt(tmpdir):
    """
    old is None, target exists, but is empty
    exp: write standard version expression to target
    """
    pytest.dbgfunc()
    trg = tmpdir.join('version.py')
    trg.write('')
    ver = '9.8.7'
    with tbx.chdir(tmpdir.strpath):
        gitr.version_update(trg.strpath, ver.split('.'))
    assert "__version__ = '{0}'\n".format(ver) in tbx.contents(trg.strpath)


# -----------------------------------------------------------------------------
def test_vu_on_tns(tmpdir):
    """
    old is None, target does not exist
    exp: write standard version expression to target
    """
    pytest.dbgfunc()
    trg = tmpdir.join('version.py')
    ver = '9.8.7'
    with tbx.chdir(tmpdir.strpath):
        gitr.version_update(trg.strpath, ver.split('.'))
    assert "__version__ = '{0}'\n".format(ver) in tbx.contents(trg.strpath)


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
    ver = '9.8.7'
    with tbx.chdir(tmpdir.strpath):
        with pytest.raises(SystemExit) as err:
            gitr.version_update(trg.strpath, ver.split('.'))
        assert ''.join(["Don't know where to put '",
                        ver,
                        "' in '",
                        nov,
                        "'"]) in str(err)


# -----------------------------------------------------------------------------
def test_vu_os_tmt(tmpdir):
    """
    old is not None, target is empty
    exp: 'Can't update '<olds>' in an empty file'
    """
    pytest.dbgfunc()
    trg = tmpdir.join('version.py')
    oldv, newv = '9.8.6', '9.8.7'
    trg.write('')
    with tbx.chdir(tmpdir.strpath):
        with pytest.raises(SystemExit) as err:
            gitr.version_update(trg.strpath, newv.split('.'), oldv.split('.'))
        assert ''.join(["Can't update '",
                        oldv,
                        "' in an empty file"]) in str(err)


# -----------------------------------------------------------------------------
def test_vu_os_tfl_op(tmpdir):
    """
    old is not None, target is not empty, old IS in target, non-standard
    exp: <olds> replaced with <news> in non-standard expression
    """
    pytest.dbgfunc()
    oldv, newv = '7.3.2.32', '7.3.2.33'
    trg = tmpdir.join('fooble-de-bar')

    tmpl = '"{0}" is the version\n'
    (pre, post) = (tmpl.format(_) for _ in [oldv, newv])
    trg.write(pre)
    with tbx.chdir(tmpdir.strpath):
        gitr.version_update(trg.basename, newv.split('.'), oldv.split('.'))
        assert post in tbx.contents(trg.basename)


# -----------------------------------------------------------------------------
def test_vu_os_tfl_onp(tmpdir):
    """
    old is not None, target is not empty, old is not in target
    exp: '<olds>' not found in '<c>'
    """
    pytest.dbgfunc()
    oldv, newv = '7.3.2.32', '7.3.2.33'
    trg = tmpdir.join('fooble-de-bar')

    tmpl = '"sizzle" is the version'
    (pre, _) = (tmpl.format(_) for _ in [oldv, newv])
    trg.write(pre)
    exp = "'{0}' not found in '{1}'".format(oldv, pre)
    with tbx.chdir(tmpdir.strpath):
        with pytest.raises(SystemExit) as err:
            gitr.version_update(trg.basename, newv.split('.'), oldv.split('.'))
        assert exp in str(err)


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
              'test_bv_already_staged_deep': 'sub1/sub2/version.py',
              'test_bv_already_bumped_default': 'version.py',
              'test_bv_already_bumped_explicit': 'frobnicate',
              'test_bv_already_bumped_deep': 'sub1/sub2/version.py',
              'test_bv_already_bumped_deep2': 'sub1/sub2/version.py',
             }[rname]
    pytest.this['target'] = target
    this = tmpdir.join(target)
    this.ensure()
    with tbx.chdir(tmpdir.strpath):
        # init the repo
        repo = git.Repo.init(tmpdir.strpath)
        # create the first target and commit it
        this.write('__version__ = "0.0.0"\n')
        repo.git.add(target)
        repo.git.commit(a=True, m='First commit')
        # update target and (maybe) stage the update
        this.write('__version__ = "0.0.0.1"\n')
        if 'staged' in rname:
            repo.git.add(target)


# -----------------------------------------------------------------------------
@pytest.fixture
def cb_basic_fixture(request):
    """
    stuff most tests can use
    """
    # pytest.dbgfunc()
    bfx = pytest.basic_fx = {}
    bfx['already'] = '{0} is already bumped'
    bfx['defname'] = 'version.py'
    bfx['template'] = "__version__ = '{0}'\n"
    bfx['notrepo'] = "{0} is not in a git repo"
    bfx['notfound'] = "{0} not found"
    bfx['nodiff'] = "{0} is not in git -- no diff available"
    bfx['mutex'] = "{0} and {1} are mutually exclusive"
    bfx['badform'] = "'{0}' is not a recognized version format"
    def rm_fixture():
        """
        Cleanup the fixture on the way out
        """
        del pytest.basic_fx
    request.addfinalizer(rm_fixture)


# -----------------------------------------------------------------------------
def bv_verify_diff(fmt, pre, post, oetup):
    """
    verify that we see a diff
    """
    stdo, _ = oetup
    pre_exp = '-' + fmt.format(pre)
    post_exp = '+' + fmt.format(post)
    assert pre_exp in stdo
    assert post_exp in stdo


# -----------------------------------------------------------------------------
def docopt_subcl():
    """
    Compute the list of sub-commands from the output of docopt_exp
    """
    exp = docopt_exp()
    rval = [_ for _ in exp.keys() if '-' not in _ and '<' not in _]
    return rval


# -----------------------------------------------------------------------------
def docopt_cmdl(argd):
    """
    Given a set of arguments, construct a command line

    If argd[k] is truish but not True, it's an option with an argument ('--foo
    <bar>') and we want to add that to the command line. If it's exactly True,
    we want to just add the option flag to the command line ('--foo').

    We could check isinstance(argd[k], bool) and argd[k] but it's simpler to
    just explicitly compare argd[k] to True.
    """
    argl = []
    subcl = docopt_subcl()
    for k in argd:
        if argd[k] is True:
            if k in subcl:
                argl.insert(0, k)
            else:
                argl.append(k)
        elif argd[k] is not None:
            argl.append(argd[k])
    return argl


# -----------------------------------------------------------------------------
def docopt_exp(**kw):
    """Default dict expected back from docopt
    """
    rval = {'--debug': False,
            '--help': False,
            '--build': False,
            '--major': False,
            '--minor': False,
            '--patch': False,
            '--quiet': False,
            '-q': False,
            '--version': False,
            'flix': False,
            '<path>': None,
            '<target>': None,
            'dunn': False,
            'depth': False,
            '<commitish>': None,
            'bv': False,
            'hook': False,
            '--add': False,
            '<hookname>': None,
            '--list': False,
            '--show': False,
            '--rm': False,
           }
    for k in kw:
        j = '--debug' if k == '-d' else k
        if j in rval:
            rval[j] = kw[k]
    return rval


# -----------------------------------------------------------------------------
@pytest.fixture
def repo_setup(tmpdir):
    """
    Set up a git repo for use in a test
    """
    # pytest.dbgfunc()
    pytest.this = {}
    # the git repo
    repo = pytest.this['repo'] = git.Repo.init(tmpdir.strpath)

    # a git-tracked file with the default name ('version.py')
    vfile = pytest.this['vname'] = tmpdir.join('version.py').ensure()

    # a git-tracked file with an alternate name
    oth = pytest.this['other'] = tmpdir.join('other_name').ensure()

    # a file not tracked by git
    pytest.this['untracked'] = tmpdir.join('untracked').ensure()

    # a file that does not exist
    pytest.this['nosuch'] = tmpdir.join('nosuch')

    # __version__ template
    pytest.this['template'] = "__version__ = '{0}'\n"

    # files in a subdirectory
    stash = {'foo/bar/version.py': {'def': True, 'gt': True, 'exists': True},
             'foo/bar/other_name': {'def': False, 'gt': True, 'exists': True},
             'foo/bar/untracked': {'def': False, 'gt': False, 'exists': True},
             'foo/bar/nosuch': {'def': False, 'gt': False, 'exists': False},}
    pytest.this['q'] = stash
    for path in stash:
        dname = tmpdir.join(os.path.dirname(path))
        if not dname.exists():
            dname.ensure(dir=True)
        stash[path]['locpath'] = dname.join(os.path.basename(path))
        if stash[path]['exists']:
            stash[path]['locpath'].ensure()
        if stash[path]['gt']:
            repo.git.add(stash[path]['locpath'].strpath)

    repo.git.add(vfile.strpath, oth.strpath)
    repo.git.commit(m='start')


# -----------------------------------------------------------------------------
if __name__ == '__main__':
    sys.exit(unittest.main())
