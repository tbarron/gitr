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
import pydoc
import pytest
import setuptools
import shlex
import subprocess
import unittest

import gitr
from gitr import gitr as app
from gitr import tbx


# -----------------------------------------------------------------------------
def test_bv_norepo(tmpdir):
    """
    pre: nothing
    gitr bv
    post: exception('version.py not found')
    """
    pytest.dbgfunc()
    with tbx.chdir(tmpdir.strpath):
        with pytest.raises(SystemExit) as e:
            gitr.gitr_bv({'bv': True})
    assert 'version.py is not in a git repo' in str(e)


# -----------------------------------------------------------------------------
def test_bv_nofile_noarg(tmpdir):
    """
    pre: nothing
    gitr bv
    post: exception('version.py not found')
    """
    pytest.dbgfunc()
    with tbx.chdir(tmpdir.strpath):
        r = git.Repo.init(tmpdir.strpath)
        with pytest.raises(SystemExit) as e:
            gitr.gitr_bv({'bv': True})
    assert 'version.py not found' in str(e)


# -----------------------------------------------------------------------------
def bv_verify_diff(fmt, pre, post, oe):
    """
    verify that we see a diff
    """
    o, e = oe
    pre_exp = '-' + fmt.format(pre)
    post_exp = '+' + fmt.format(post)
    assert pre_exp in o
    assert post_exp in o


# -----------------------------------------------------------------------------
def test_bv_file_noarg_3(tmpdir, capsys):
    """
    pre: 2.7.3 in version.py
    gitr bv
    post: 2.7.3.1 in version.py
    """
    pytest.dbgfunc()
    pre, post = ('2.7.3', '2.7.3.1')
    vpath = tmpdir.join('version.py')
    vpath.write("__version__ = '{0}'\n".format(pre))
    r = git.Repo.init(tmpdir.strpath)
    with tbx.chdir(tmpdir.strpath):
        r.git.add(vpath.basename)
        r.git.commit(m='inception')
        gitr.gitr_bv({'bv': True})
        bv_verify_diff("__version__ = '{}'", pre, post, capsys.readouterr())
    assert post in vpath.read()


# -----------------------------------------------------------------------------
def test_bv_dir_nofile(tmpdir):
    """
    pre: '/' in target; dirname(target) exists; target does not
    gitr bv <target-path>
    post: no traceback
    """
    pytest.dbgfunc()
    (sub, trg) = ('sub', 'trg')
    sub_lp = tmpdir.join(sub).ensure(dir=True)
    trg_lp = sub_lp.join(trg)
    rel = '{0}/{1}'.format(sub, trg)
    exp = "{0} is not in git -- no diff available"
    r = git.Repo.init(tmpdir.strpath)
    with tbx.chdir(tmpdir.strpath):
        with pytest.raises(SystemExit) as e:
            gitr.gitr_bv({'bv': True, '<path>': rel})
            assert exp.format(rel) in str(e)
    assert "'0.0.0'" in trg_lp.read()


# -----------------------------------------------------------------------------
def test_bv_file_noarg_4(tmpdir, capsys):
    """
    pre: 2.7.3.8 in version.py
    gitr bv
    post: 2.7.3.9 in version.py
    """
    pytest.dbgfunc()
    pre, post = ('2.7.3.8', '2.7.3.9')
    vpath = tmpdir.join('version.py')
    vpath.write("__version__ = '{0}'\n".format(pre))
    r = git.Repo.init(tmpdir.strpath)
    with tbx.chdir(tmpdir.strpath):
        r.git.add(vpath.basename)
        r.git.commit(m='inception')
        gitr.gitr_bv({'bv': True})
        bv_verify_diff("__version__ = '{}'", pre, post, capsys.readouterr())
    assert post in vpath.read()


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
    assert not bvpath.exists()
    r = git.Repo.init(tmpdir.strpath)
    with tbx.chdir(tmpdir.strpath):
        rpath = bvpath.relto(tmpdir)
        with pytest.raises(SystemExit) as e:
            gitr.gitr_bv({'bv': True, '<path>': rpath})
        assert '{0} is not in git -- no diff available'.format(rpath) in str(e)
    assert bvpath.exists()
    assert "'0.0.0'" in bvpath.read()


# -----------------------------------------------------------------------------
def test_bv_nofile_major(tmpdir):
    """
    pre: nothing
    gitr bv --major
    post: exception('version.py not found')
    """
    pytest.dbgfunc()
    vname = 'version.py'
    with tbx.chdir(tmpdir.strpath):
        r = git.Repo.init(tmpdir.strpath)
        with pytest.raises(SystemExit) as e:
            gitr.gitr_bv({'bv': True, '--major': True})
        assert '{} not found'.format(vname) in str(e)


# -----------------------------------------------------------------------------
def test_bv_nofile_major_fn(tmpdir):
    """
    pre: nothing
    gitr bv --major frooble
    post: exception('frooble not found')
    """
    pytest.dbgfunc()
    vname = 'frooble'
    with tbx.chdir(tmpdir.strpath):
        r = git.Repo.init(tmpdir.strpath)
        with pytest.raises(SystemExit) as e:
            gitr.gitr_bv({'bv': True, '--major': True, '<path>': vname})
        assert '{0} not found'.format(vname) in str(e)


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
        # update target and (maybe) stage the update
        t.write('__version__ = "0.0.0.1"\n')
        if 'staged' in rname:
            r.git.add(target)


# -----------------------------------------------------------------------------
@pytest.mark.skipif(os.getenv('TRAVIS') == "true", reason="bleah")
def test_bv_already_bumped_default(tmpdir, already_setup):
    """
    If 'version.py' is already bumped, don't update it
    """
    pytest.dbgfunc()
    os.system("ls -l /usr/bin/git")
    os.system("echo $PATH")
    v = pytest.this['target']
    with tbx.chdir(tmpdir.strpath):
        pre = tbx.contents(v)
        with pytest.raises(SystemExit) as e:
            gitr.gitr_bv({'bv': True, '<path>': None})
        post = tbx.contents(v)
    assert '{} is already bumped'.format(v) in str(e)
    assert pre == post


# -----------------------------------------------------------------------------
@pytest.mark.skipif(os.getenv('TRAVIS') == "true", reason="bleah")
def test_bv_already_bumped_explicit(tmpdir, already_setup):
    """
    If an explicit target is already bumped, don't update it
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
@pytest.mark.skipif(os.getenv('TRAVIS') == "true", reason="bleah")
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
@pytest.mark.skipif(os.getenv('TRAVIS') == "true", reason="bleah")
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
@pytest.fixture
def repo_setup(tmpdir):
    pytest.dbgfunc()
    pytest.this = {}
    # the git repo
    r = pytest.this['repo'] = git.Repo.init(tmpdir.strpath)

    # a git-tracked file with the default name ('version.py')
    v = pytest.this['vname'] = tmpdir.join('version.py').ensure()

    # a git-tracked file with an alternate name
    o = pytest.this['other'] = tmpdir.join('other_name').ensure()

    # a file not tracked by git
    u = pytest.this['untracked'] = tmpdir.join('untracked').ensure()

    # a file that does not exist
    n = pytest.this['nosuch'] = tmpdir.join('nosuch')

    # __version__ template
    pytest.this['template'] = "__version__ = '{0}'\n"

    # files in a subdirectory
    q = {'foo/bar/version.py': {'def': True, 'gt': True, 'exists': True},
         'foo/bar/other_name': {'def': False, 'gt': True, 'exists': True},
         'foo/bar/untracked': {'def': False, 'gt': False, 'exists': True},
         'foo/bar/nosuch': {'def': False, 'gt': False, 'exists': False},}
    pytest.this['q'] = q
    for p in q:
        d = tmpdir.join(os.path.dirname(p))
        if not d.exists():
            d.ensure(dir=True)
        q[p]['locpath'] = d.join(os.path.basename(p))
        if q[p]['exists']:
            q[p]['locpath'].ensure()
        if q[p]['gt']:
            r.git.add(q[p]['locpath'].strpath)

    r.git.add(v.strpath, o.strpath)
    r.git.commit(m='start')


# -----------------------------------------------------------------------------
@pytest.mark.skipif(os.getenv('TRAVIS') == "true", reason="bleah")
def test_bv_file_major_3(tmpdir, capsys, repo_setup):
    """
    pre: '7.4.3' in version.py
    gitr bv --major --quiet
    post: '8.0.0' in version.py, nothing on stdout
    """
    pytest.dbgfunc()
    pre, post = '7.4.3', '8.0.0'
    r = pytest.this['repo']
    v = pytest.this['vname']
    v.write(pre)
    r.git.commit(a=True, m='set version')
    with tbx.chdir(tmpdir.strpath):
        gitr.gitr_bv({'bv': True, '--major': True, '--quiet': True})
    assert post in v.read()
    assert 'M version.py' in r.git.status(porc=True)
    o, e = capsys.readouterr()
    assert o.strip() == ""


# -----------------------------------------------------------------------------
@pytest.mark.skipif(os.getenv('TRAVIS') == "true", reason="bleah")
def test_bv_file_major_3_fn(tmpdir, capsys, repo_setup):
    """
    pre: '7.4.3' in splack
    gitr bv --major splack
    post: '8.0.0' in splack
    """
    pytest.dbgfunc()
    r = pytest.this['repo']
    o = pytest.this['other']
    pre, post = "7.4.3", "8.0.0"
    o.write("__version__ = '{0}'\n".format(pre))
    r.git.commit(a=True, m='set a version')
    with tbx.chdir(tmpdir.strpath):
        gitr.gitr_bv({'bv': True, '--major': True,
                      '<path>': o.basename})
    assert "__version__ = '{0}'".format(post) in o.read()
    bv_verify_diff("__version__ = '{0}'", pre, post, capsys.readouterr())


# -----------------------------------------------------------------------------
@pytest.mark.skipif(os.getenv('TRAVIS') == "true", reason="bleah")
def test_bv_nofile_major_3_fn(tmpdir, repo_setup):
    """
    pre: '7.4.3' in splack
    gitr bv --major flump
    post: exception('flump not found')
    """
    pytest.dbgfunc()
    pre = post = '7.4.3'
    r = pytest.this['repo']
    n = pytest.this['nosuch']
    o = pytest.this['other']
    o.write("__version__ = '{0}'".format(pre))
    r.git.commit(a=True, m='set version')
    with tbx.chdir(tmpdir.strpath):
        with pytest.raises(SystemExit) as e:
            gitr.gitr_bv({'bv': True, '--major': True,
                          '<path>': n.basename})
        assert '{0} not found'.format(n.basename) in str(e)
    assert "__version__ = '{0}'".format(post) in o.read()


# -----------------------------------------------------------------------------
@pytest.mark.skipif(os.getenv('TRAVIS') == "true", reason="bleah")
def test_bv_file_major_4(tmpdir, capsys, repo_setup):
    """
    pre: '1.0.0.17' in version.py
    gitr bv --major
    post: '2.0.0' in version.py
    """
    pytest.dbgfunc()
    r = pytest.this['repo']
    v = pytest.this['vname']
    pre, post = '1.0.0.17', '2.0.0'
    v.write("__version__ = '{0}'".format(pre))
    r.git.commit(a=True, m='set version')
    with tbx.chdir(tmpdir.strpath):
        gitr.gitr_bv({'bv': True, '--major': True,
                      '<path>': v.basename})
        bv_verify_diff("__version__ = '{}'", pre, post, capsys.readouterr())
    assert "__version__ = '{0}'".format(post) in v.read()


# -----------------------------------------------------------------------------
@pytest.mark.skipif(os.getenv('TRAVIS') == "true", reason="bleah")
def test_bv_nofile_minor(tmpdir, repo_setup):
    """
    pre: nothing
    gitr bv --minor
    post: exception('version.py not found')
    """
    pytest.dbgfunc()
    v = pytest.this['vname']
    v.remove()
    q = pytest.this['q']
    q['foo/bar/version.py']['locpath'].remove()
    with tbx.chdir(tmpdir.strpath):
        with pytest.raises(SystemExit) as e:
            gitr.gitr_bv({'bv': True, '--minor': True})
        assert 'version.py not found' in str(e)


# -----------------------------------------------------------------------------
@pytest.mark.skipif(os.getenv('TRAVIS') == "true", reason="bleah")
def test_bv_file_minor_3(tmpdir, capsys, repo_setup):
    """
    pre: '3.3.2' in version.py
    gitr bv --minor
    post: '3.4.0' in version.py
    """
    pytest.dbgfunc()
    pre, post = '3.3.2', '3.4.0'
    r = pytest.this['repo']
    v = pytest.this['vname']
    v.write("__version__ = '{0}'\n".format(pre))
    r.git.commit(a=True, m='first version')
    with tbx.chdir(tmpdir.strpath):
        gitr.gitr_bv({'bv': True, '--minor': True, '-q': True})
        o, e = capsys.readouterr()
        assert o.strip() == ""
    assert "__version__ = '{0}'".format(post) in v.read()


# -----------------------------------------------------------------------------
@pytest.mark.skipif(os.getenv('TRAVIS') == "true", reason="bleah")
def test_bv_file_minor_4(tmpdir, capsys, repo_setup):
    """
    pre: '3.3.2.7' in version.py
    gitr bv --minor
    post: '3.4.0' in version.py
    """
    pytest.dbgfunc()
    r = pytest.this['repo']
    v = pytest.this['vname']
    pre, post = "3.3.2.7", "3.4.0"
    v.write("__version__ = '{0}'\n".format(pre))
    r.git.commit(a=True, m='first version')
    with tbx.chdir(tmpdir.strpath):
        gitr.gitr_bv({'bv': True, '--minor': True})
        bv_verify_diff("__version__ = '{}'", pre, post,
                       capsys.readouterr())
    assert "__version__ = '{0}'".format(post) in v.read()


# -----------------------------------------------------------------------------
@pytest.mark.skipif(os.getenv('TRAVIS') == "true", reason="bleah")
def test_bv_file_minor_3_fn(tmpdir, capsys, repo_setup):
    """
    pre: '3.3.2' in foo/bar/setup.py
    gitr bv --minor foo/bar/setup.py
    post: '3.4.0' in foo/bar/setup.py
    """
    pytest.dbgfunc()
    r = pytest.this['repo']
    v = pytest.this['vname']
    d = tmpdir.join('foo/bar').ensure(dir=True)
    s = d.join('setup.py')
    pre, post = "3.3.2", "3.4.0"
    s.write("__version__ = '{0}'\n".format(pre))
    r.git.add(s.strpath)
    r.git.commit(a=True, m='first version')
    with tbx.chdir(tmpdir.strpath):
        gitr.gitr_bv({'bv': True, '--minor': True,
                      '<path>': s.relto(tmpdir)})
        bv_verify_diff("__version__ = '{}'", pre, post,
                       capsys.readouterr())
    assert "__version__ = '{0}'".format(post) in s.read()


# -----------------------------------------------------------------------------
@pytest.mark.skipif(os.getenv('TRAVIS') == "true", reason="bleah")
def test_bv_file_minor_4_fn(tmpdir, repo_setup):
    """
    pre: '3.3.2.7' in version.py
    gitr bv --minor frockle
    post: '3.3.2.7' in version.py, exception('frockle not found')
    """
    pytest.dbgfunc()
    r = pytest.this['repo']
    v = pytest.this['vname']
    pre, post = "3.3.2.7", "3.4.0"
    v.write("__version__ = '{0}'\n".format(pre))
    r.git.commit(a=True, m='first version')
    with tbx.chdir(tmpdir.strpath):
        with pytest.raises(SystemExit) as e:
            gitr.gitr_bv({'bv': True, '--minor': True,
                          '<path>': 'frockle'})
        assert 'frockle not found' in str(e)


# -----------------------------------------------------------------------------
@pytest.mark.skipif(os.getenv('TRAVIS') == "true", reason="bleah")
def test_bv_nofile_patch(tmpdir, repo_setup):
    """
    pre: nothing
    gitr bv --patch
    post: exception('version.py not found')
    """
    pytest.dbgfunc()
    v = pytest.this['vname']
    v.remove()
    q = pytest.this['q']
    q['foo/bar/version.py']['locpath'].remove()
    with tbx.chdir(tmpdir.strpath):
        with pytest.raises(SystemExit) as e:
            gitr.gitr_bv({'--patch': True})
        assert '{} not found'.format(v.basename) in str(e)


# -----------------------------------------------------------------------------
@pytest.mark.skipif(os.getenv('TRAVIS') == "true", reason="bleah")
def test_bv_file_patch_3(tmpdir, repo_setup, capsys):
    """
    pre: '1.3.2' in version.py
    gitr bv --patch
    post: '1.3.3' in version.py
    """
    pytest.dbgfunc()
    pre, post = '1.3.2', '1.3.3'
    r = pytest.this['repo']
    v = pytest.this['vname']
    v.write("__version__ = '{0}'\n".format(pre))
    r.git.commit(a=True, m='first version')
    with tbx.chdir(tmpdir.strpath):
        gitr.gitr_bv({'bv': True, '--patch': True, '-q': True})
        o, e = capsys.readouterr()
        assert o.strip() == ""
    assert "__version__ = '{0}'".format(post) in v.read()



# -----------------------------------------------------------------------------
@pytest.mark.skipif(os.getenv('TRAVIS') == "true", reason="bleah")
def test_bv_file_patch_4(tmpdir, capsys, repo_setup):
    """
    pre: '1.3.2.7' in version.py
    gitr bv --patch
    post: '1.3.3' in version.py
    """
    pytest.dbgfunc()
    r = pytest.this['repo']
    v = pytest.this['vname']
    pre, post = "1.3.2.7", "1.3.3"
    v.write("__version__ = '{0}'\n".format(pre))
    r.git.commit(a=True, m='first version')
    with tbx.chdir(tmpdir.strpath):
        gitr.gitr_bv({'bv': True, '--patch': True})
        bv_verify_diff("__version__ = '{}'", pre, post,
                       capsys.readouterr())
    assert "__version__ = '{0}'".format(post) in v.read()


# -----------------------------------------------------------------------------
@pytest.mark.skipif(os.getenv('TRAVIS') == "true", reason="bleah")
def test_bv_nofile_build(tmpdir, repo_setup):
    """
    Should raise exception
    pre: nothing
    gitr bv --build
    post: exception('version.py not found')
    """
    pytest.dbgfunc()
    v = pytest.this['vname']
    v.remove()
    q = pytest.this['q']
    q['foo/bar/version.py']['locpath'].remove()
    with tbx.chdir(tmpdir.strpath):
        with pytest.raises(SystemExit) as e:
            gitr.gitr_bv({'--build': True})
        assert '{} not found'.format(v.basename) in str(e)


# -----------------------------------------------------------------------------
@pytest.mark.skipif(os.getenv('TRAVIS') == "true", reason="bleah")
def test_bv_file_build_3_fn(tmpdir, repo_setup):
    """
    pre: '7.8.9' in ./pkg/foobar
    gitr bv --build ./pkg/foobar
    post: '7.8.9.1' in ./pkg/foobar
    """
    pytest.dbgfunc()
    r = pytest.this['repo']
    pre, post = '7.8.9', '7.8.9.1'
    t = pytest.this['template']
    op = 'foo/bar/other_name'
    o = pytest.this['q'][op]
    o['locpath'].write(t.format(pre))
    r.git.commit(a=True, m='version')
    with tbx.chdir(tmpdir.strpath):
        gitr.gitr_bv({'--build': True,
                      '<path>': op})
    assert t.format(post) in o['locpath'].read()


# -----------------------------------------------------------------------------
@pytest.mark.skipif(os.getenv('TRAVIS') == "true", reason="bleah")
def test_bv_file_build_4(tmpdir, capsys, repo_setup):
    """
    pre: '1.2.3.4' in foo/bar/version.py
    gitr bv --build
    post: '1.2.3.5' in foo/bar/version.py
    """
    pytest.dbgfunc()
    r = pytest.this['repo']
    pytest.this['vname'].remove()
    vp = 'foo/bar/version.py'
    v = pytest.this['q'][vp]
    pre, post = "1.2.3.4", "1.2.3.5"
    t = pytest.this['template']
    v['locpath'].write(t.format(pre))
    r.git.commit(a=True, m='first version')
    with tbx.chdir(tmpdir.strpath):
        gitr.gitr_bv({'bv': True, '--build': True})
        bv_verify_diff(t, pre, post,
                       capsys.readouterr())


# -----------------------------------------------------------------------------
@pytest.mark.skipif(os.getenv('TRAVIS') == "true", reason="bleah")
def test_bv_major_minor(tmpdir, repo_setup):
    """
    pre: nothing
    gitr bv --major --minor
    post: exception('--major and --minor are mutually exclusive')
    """
    pytest.dbgfunc()
    mx_opt1, mx_opt2 = '--major', '--minor'
    exp = '{0} and {1} are mutually exclusive'.format(mx_opt1, mx_opt2)
    with tbx.chdir(tmpdir.strpath):
        with pytest.raises(SystemExit) as e:
            gitr.gitr_bv({mx_opt1: True, mx_opt2: True})
        assert exp in str(e)


# -----------------------------------------------------------------------------
def test_bv_major_patch(tmpdir):
    """
    pre: nothing
    gitr bv --major --patch
    post: exception('--major and --patch are mutually exclusive')
    """
    pytest.dbgfunc()
    mx_opt1, mx_opt2 = '--major', '--patch'
    exp = '{0} and {1} are mutually exclusive'.format(mx_opt1, mx_opt2)
    with tbx.chdir(tmpdir.strpath):
        with pytest.raises(SystemExit) as e:
            gitr.gitr_bv({mx_opt1: True, mx_opt2: True})
        assert exp in str(e)


# -----------------------------------------------------------------------------
def test_bv_major_build(tmpdir):
    """
    pre: nothing
    gitr bv --major --build
    post: exception('--major and --build are mutually exclusive')
    """
    pytest.dbgfunc()
    mx_opt1, mx_opt2 = '--major', '--build'
    exp = '{0} and {1} are mutually exclusive'.format(mx_opt1, mx_opt2)
    with tbx.chdir(tmpdir.strpath):
        with pytest.raises(SystemExit) as e:
            gitr.gitr_bv({mx_opt1: True, mx_opt2: True})
        assert exp in str(e)


# -----------------------------------------------------------------------------
def test_bv_minor_patch(tmpdir):
    """
    pre: nothing
    gitr bv --minor --patch
    post: exception('--minor and --patch are mutually exclusive')
    """
    pytest.dbgfunc()
    mx_opt1, mx_opt2 = '--minor', '--patch'
    exp = '{0} and {1} are mutually exclusive'.format(mx_opt1, mx_opt2)
    with tbx.chdir(tmpdir.strpath):
        with pytest.raises(SystemExit) as e:
            gitr.gitr_bv({mx_opt1: True, mx_opt2: True})
        assert exp in str(e)


# -----------------------------------------------------------------------------
def test_bv_minor_build(tmpdir):
    """
    pre: nothing
    gitr bv --minor --build
    post: exception('--minor and --build are mutually exclusive')
    """
    pytest.dbgfunc()
    mx_opt1, mx_opt2 = '--minor', '--build'
    exp = '{0} and {1} are mutually exclusive'.format(mx_opt1, mx_opt2)
    with tbx.chdir(tmpdir.strpath):
        with pytest.raises(SystemExit) as e:
            gitr.gitr_bv({mx_opt1: True, mx_opt2: True})
        assert exp in str(e)


# -----------------------------------------------------------------------------
def test_bv_patch_build(tmpdir):
    """
    pre: nothing
    gitr bv --patch --build
    post: exception('--patch and --build are mutually exclusive')
    """
    pytest.dbgfunc()
    mx_opt1, mx_opt2 = '--patch', '--build'
    exp = '{0} and {1} are mutually exclusive'.format(mx_opt1, mx_opt2)
    with tbx.chdir(tmpdir.strpath):
        with pytest.raises(SystemExit) as e:
            gitr.gitr_bv({mx_opt1: True, mx_opt2: True})
        assert exp in str(e)


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
                                  {"flix": True, "--minor": True,
                                   "<hookname>": 'summer'},
                                  {"nodoc": True, "--version": True},
                                  {"dupl": True, "--version": True},
                                  ))
def test_docopt_raises(argd, capsys):
    """
    Test calls to docopt.docopt() that should be successful
    """
    pytest.dbgfunc()
    exp = docopt_exp(**argd)
    argl = docopt_cmdl(argd)
    with pytest.raises(docopt.DocoptExit) as e:
        r = docopt.docopt(gitr.__doc__, argl)
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
                                   '<path>': 'patch'},
                                  {'bv': True, '--debug': True,},
                                  {'flix': True, '-d': True,
                                   '<target>': 'foobar'},
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
    argl = docopt_cmdl(argd)
    r = docopt.docopt(gitr.__doc__, argl)
    assert r == exp


# -----------------------------------------------------------------------------
@pytest.mark.parametrize('subc', ['dunn',
                                  'depth',
                                  'dupl',
                                  'flix',
                                  'hook',
                                  'nodoc',
                                  ])
def test_gitr_unimpl(subc, capsys):
    """
    gitr <subc> -> 'coming soon'
    """
    pytest.dbgfunc()
    func = getattr(gitr, 'gitr_' + subc)
    func({subc: True})
    o, e = capsys.readouterr()
    assert 'Coming soon' in o


# -----------------------------------------------------------------------------
def test_pydoc_gitr(capsys):
    """
    Verify the behavior of running 'pydoc gitr'
    """
    pytest.dbgfunc()
    pydoc.help(gitr)
    o, e = capsys.readouterr()
    z = docopt_exp()
    for k in z:
        assert k in o


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
    inp = ['7', '19']
    exp = "'{0}' is not a recognized version format".format('.'.join(inp))
    with pytest.raises(SystemExit) as e:
        res = gitr.version_increment(inp, {'bv': True})
    assert exp in str(e)


# -----------------------------------------------------------------------------
def test_vi_long(tmpdir):
    """
    iv = ['7', '19', 'foo', 'sample', 'wokka']
    opts = {'--build': True}
    sys.exit('7.19.foo.sample.wokka' is not a recognized version format)
    """
    pytest.dbgfunc()
    inp = ['7', '19', 'foo', 'sample', 'wokka']
    exp = "'{0}' is not a recognized version format".format('.'.join(inp))
    with pytest.raises(SystemExit) as e:
        res = gitr.version_increment(inp, {'bv': True})
    assert exp in str(e)


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
        assert ' '.join(["Can't update",
                        "'{}'".format('.'.join(oldv)),
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
def docopt_subcl():
    """
    Compute the list of sub-commands from the output of docopt_exp
    """
    exp = docopt_exp()
    rv = [z for z in exp.keys() if '-' not in z and '<' not in z]
    return rv


# -----------------------------------------------------------------------------
def docopt_cmdl(argd):
    """
    Given a set of arguments, construct a command line
    """
    argl = []
    subcl = docopt_subcl()
    for k in argd:
        if argd[k] == True:
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
    rv = {'--debug': False,
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
          'nodoc': False,
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
          'dupl': False
          }
    for k in kw:
        kp = '--debug' if k == '-d' else k
        if kp in rv:
            rv[kp] = kw[k]
    return rv


# -----------------------------------------------------------------------------
if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
