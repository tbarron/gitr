import pexpect

def test_pylint():
    """
    Run pylint on this code and check the output
    """
    result = pexpect.run('pylint gitr tests -rn')
    assert result == ''

