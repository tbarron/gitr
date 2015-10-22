import os

from gitr import tbx

def test_chdir(tmpdir):
    """
    Test the chdir contextmanager
    """
    here = os.getcwd()
    with tbx.chdir(tmpdir.strpath):
        assert os.getcwd() == tmpdir.strpath
    assert os.getcwd() == here
