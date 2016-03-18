"""
Toolbox
"""
# pylint: disable=locally-disabled,unused-argument
import os
import re

import pytest

from gitr import tbx

# -----------------------------------------------------------------------------
def test_chdir(tmpdir):
    """
    Test the chdir contextmanager
    """
    pytest.dbgfunc()
    here = os.getcwd()
    with tbx.chdir(tmpdir.strpath):
        assert os.getcwd() == tmpdir.strpath
    assert os.getcwd() == here


# -----------------------------------------------------------------------------
def test_chdir_nosuch(tmpdir):
    """
    Test the chdir contextmanager when a non-existent directory is named
    """
    pytest.dbgfunc()
    here = os.getcwd()
    badtarg = tmpdir.join('nosuch')
    with pytest.raises(OSError) as err:
        with tbx.chdir(badtarg.strpath):
            assert os.getcwd() == tmpdir.strpath
    assert 'No such file or directory' in str(err)
    assert os.getcwd() == here


# -----------------------------------------------------------------------------
def test_chdir_isfile(tmpdir):
    """
    Test the chdir contextmanager when a file is named
    """
    pytest.dbgfunc()
    here = os.getcwd()
    thisfile = tmpdir.join('thisfile').ensure()
    with pytest.raises(OSError) as err:
        with tbx.chdir(thisfile.strpath):
            assert os.getcwd() == thisfile.strpath
    assert 'Not a directory' in str(err)
    assert os.getcwd() == here


# -----------------------------------------------------------------------------
def test_chdir_perm(tmpdir):
    """
    Test the chdir contextmanager when chdir is not allowed
    """
    pytest.dbgfunc()
    here = os.getcwd()
    thisdir = tmpdir.join('thisdir').ensure(dir=True)
    thisdir.chmod(0000)
    with pytest.raises(OSError) as err:
        with tbx.chdir(thisdir.strpath):
            assert os.getcwd() == thisdir.strpath
    assert 'Permission denied' in str(err)
    thisdir.chmod(0755)
    assert os.getcwd() == here


# -----------------------------------------------------------------------------
# pylint: disable=locally-disabled,redefined-outer-name
def test_contents_list(tmpdir, contents_fixture):
    """
    Test getting the contents of a file
    """
    pytest.dbgfunc()
    this = pytest.this
    result = tbx.contents(this['tfn'].strpath, rtype='list')
    assert result == [x + '\n' for x in this['td']]


# -----------------------------------------------------------------------------
def test_contents_str(tmpdir, contents_fixture):
    """
    Test getting the contents of a file
    """
    pytest.dbgfunc()
    this = pytest.this
    result = tbx.contents(this['tfn'].strpath)
    assert result == ''.join([x + '\n' for x in this['td']])


# -----------------------------------------------------------------------------
def test_contents_fail(tmpdir, contents_fixture):
    """
    Test getting the contents of a file
    """
    pytest.dbgfunc()
    this = pytest.this
    with pytest.raises(IOError) as err:
        dummy = tbx.contents(this['tfn'].strpath + "_nonesuch")
    assert "No such file or directory" in str(err)


# -----------------------------------------------------------------------------
def test_contents_default(tmpdir, contents_fixture):
    """
    Test getting the contents of a file
    """
    pytest.dbgfunc()
    this = pytest.this
    result = tbx.contents(this['tfn'].strpath + "_nonesuch",
                          default="take this instead")
    assert "take this instead" in result


# -----------------------------------------------------------------------------
def test_revnumerate():
    """
    Test reverse enumerating a list
    """
    pytest.dbgfunc()
    weekdays = ['monday', 'tuesday', 'wednesday', 'thursday',
                'friday', 'saturday', 'sunday']
    wd_copy = weekdays[:]
    wd_copy.reverse()
    for i, k in tbx.revnumerate(weekdays):
        assert k == weekdays[i]


# -----------------------------------------------------------------------------
def test_run_stdout():
    """
    Run a process and capture stdout
    """
    pytest.dbgfunc()
    result = tbx.run('python -c "import this"')
    assert "Zen of Python" in result
    assert "Namespaces" in result


# -----------------------------------------------------------------------------
def test_run_stderr():
    """
    Run a process and capture stdout
    """
    pytest.dbgfunc()
    result = tbx.run("ls --nosuch")
    assert "ERR:" in result
    assert re.findall("(illegal|unrecognized) option", result)


# -----------------------------------------------------------------------------
def test_run_fail():
    """
    Run a binary that doesn't exist
    """
    pytest.dbgfunc()
    result = tbx.run("nosuchbinary")
    assert "ERR:" in result
    assert "No such file or directory" in result


# -----------------------------------------------------------------------------
def test_tmpenv_present():
    """
    pre: $TMPENV == 'pre test value'
    with tmpenv(TMPENV='some other value'):
        assert os.getenv('TMPENV') == 'some other value'
    post: $TMPENV == 'pre test value'
    """
    pytest.dbgfunc()
    vname, pre, inside = 'TMPENV', 'pre test value', 'some other value'
    os.environ[vname] = pre
    with tbx.tmpenv(TMPENV=inside):
        assert inside == os.getenv(vname)
    assert pre == os.getenv(vname)
    del os.environ[vname]


# -----------------------------------------------------------------------------
def test_tmpenv_absent():
    """
    pre: 'TMPENV' not in os.environ
    with tmpenv(TMPENV='something'):
        assert os.getenv('TMPENV') == 'something'
    post: 'TMPENV' not in os.environ
    """
    pytest.dbgfunc()
    vname, inside = 'TMPENV', 'something'
    if vname in os.environ:
        del os.environ[vname]
    with tbx.tmpenv(TMPENV=inside):
        assert inside == os.getenv(vname)
    assert vname not in os.environ


# -----------------------------------------------------------------------------
def test_tmpenv_unset():
    """
    pre: $TMPENV == 'pre test value'
    with tmpenv(TMPENV=None):
        assert 'TMPENV' not in os.environ
    post: $TMPENV == 'pre test value'
    """
    pytest.dbgfunc()
    vname, pre = 'TMPENV', 'pre test value'
    os.environ[vname] = pre
    with tbx.tmpenv(TMPENV=None):
        assert vname not in os.environ
    assert pre == os.getenv(vname)
    del os.environ[vname]


# -----------------------------------------------------------------------------
def test_tmpenv_mult():
    """
    pre: $TMPENV undefined, TMPENV_OTHER == ''
    with tmpenv(TMPENV='foobar', OTHER='another value'):
        assert 'foobar' == os.getenv('TMPENV')
        assert 'another value' == os.getenv('OTHER')
    post: $TMPENV == 'pre test value', OTHER undefined
    """
    pytest.dbgfunc()
    vname, oth, pre, = 'TMPENV', 'TMPENV_OTHER', 'some value'
    tmp1, tmp2 = 'good', 'best'
    os.environ[oth] = pre
    if vname in os.environ:
        del os.environ[vname]
    with tbx.tmpenv(TMPENV=tmp1, TMPENV_OTHER=tmp2):
        assert tmp1 == os.getenv(vname)
        assert tmp2 == os.getenv(oth)
    assert pre == os.getenv(oth)
    assert vname not in os.environ


# -----------------------------------------------------------------------------
def test_tmpenv_exception():
    """
    pre: $TMPENV == 'some value'
    with tmpenv(TMPENV='foobar'):
        assert 'foobar' == os.getenv('TMPENV')
        raise StandardError('some random error')
    post: $TMPENV == 'some value'
    """
    pytest.dbgfunc()
    vname, pre, dur = 'TMPENV', 'some value', 'good'
    os.environ[vname] = pre
    with pytest.raises(StandardError):
        with tbx.tmpenv(TMPENV=dur):
            assert dur == os.getenv(vname)
            raise StandardError('some random exception')
    assert pre == os.getenv(vname)
    del os.environ[vname]


# -----------------------------------------------------------------------------
@pytest.fixture
def contents_fixture(tmpdir):
    """
    set up data for test
    """
    pytest.dbgfunc()
    pytest.this = {}
    testdata = pytest.this['td'] = ["one", "two", "three", "four", "five"]
    tfn = pytest.this['tfn'] = tmpdir.join("testthis")
    tfn.write(''.join([x+"\n" for x in testdata]))


