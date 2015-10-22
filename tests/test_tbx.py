import os
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
@pytest.fixture
def contents_setup(tmpdir):
    """
    set up data for test
    """
    pytest.dbgfunc()
    pytest.this = {}
    td = pytest.this['td'] = ["one", "two", "three", "four", "five"]
    tfn = pytest.this['tfn'] = tmpdir.join("testthis")
    tfn.write(''.join([x+"\n" for x in td]))


# -----------------------------------------------------------------------------
def test_contents_list(tmpdir, contents_setup):
    """
    Test getting the contents of a file
    """
    pytest.dbgfunc()
    pt = pytest.this
    c = tbx.contents(pt['tfn'].strpath, type=list)
    assert c == [x + '\n' for x in pt['td']]


# -----------------------------------------------------------------------------
def test_contents_str(tmpdir):
    """
    Test getting the contents of a file
    """
    pytest.dbgfunc()
    pt = pytest.this
    c = tbx.contents(pt['tfn'].strpath)
    assert c == ''.join([x + '\n' for x in pt['td']])


# -----------------------------------------------------------------------------
def test_contents_fail(tmpdir):
    """
    Test getting the contents of a file
    """
    pytest.dbgfunc()
    pt = pytest.this
    with pytest.raises(IOError) as e:
        c = tbx.contents(pt['tfn'].strpath + "_nonesuch")
    assert "No such file or directory" in str(e)


# -----------------------------------------------------------------------------
def test_contents_default(tmpdir):
    """
    Test getting the contents of a file
    """
    pytest.dbgfunc()
    pt = pytest.this
    c = tbx.contents(pt['tfn'].strpath + "_nonesuch", default="take this instead")
    assert "take this instead" in c


# -----------------------------------------------------------------------------
def test_revnumerate():
    """
    Test reverse enumerating a list
    """
    pytest.dbgfunc()
    td = ['monday', 'tuesday', 'wednesday', 'thursday',
          'friday', 'saturday', 'sunday']
    tdr = td[:]
    tdr.reverse()
    for n, v in tbx.revnumerate(td):
        assert v == td[n]


# -----------------------------------------------------------------------------
def test_run_stdout():
    """
    Run a process and capture stdout
    """
    pytest.dbgfunc()
    r = tbx.run('python -c "import this"')
    assert "Zen of Python" in r
    assert "Namespaces" in r


# -----------------------------------------------------------------------------
def test_run_stderr():
    """
    Run a process and capture stdout
    """
    pytest.dbgfunc()
    r = tbx.run("ls -Q")
    assert "ERR:" in r
    assert "illegal option" in r


# -----------------------------------------------------------------------------
def test_run_fail():
    """
    Run a binary that doesn't exist
    """
    pytest.dbgfunc()
    r = tbx.run("nosuchbinary")
    assert "ERR:" in r
    assert "No such file or directory" in r
