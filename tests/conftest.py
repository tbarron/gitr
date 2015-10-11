import contextlib
import os
import pdb
import pytest
import sys


# -----------------------------------------------------------------------------
def pytest_addoption(parser):
    """
    Add options --nolog, --all to the command line
    """
    # pdb.set_trace()
    parser.addoption("--dbg", action="append", default=[],
                     help="start debugger on named test or all")
    sys.path.append(os.getcwd())


# -----------------------------------------------------------------------------
def pytest_runtest_setup(item):
    """
    Decide whether to skip a test before running it
    """
    if item.cls is None:
        fqn = '.'.join([item.module.__name__, item.name])
    else:
        fqn = '.'.join([item.module.__name__, item.cls.__name__, item.name])
    dbg_n = '..' + item.name
    dbg_l = item.config.getvalue('dbg')
    # skip_l = item.config.getvalue('skip')
    if dbg_n in dbg_l or '..all' in dbg_l:
        pdb.set_trace()

    if any([item.name in item.config.getoption('--dbg'),
            any([x in item.name for x in item.config.getoption('--dbg')]),
            'all' in item.config.getoption('--dbg')]):
        pytest.dbgfunc = pdb.set_trace
    else:
        pytest.dbgfunc = lambda: None


# -----------------------------------------------------------------------------
@contextlib.contextmanager
def chdir(target):
    start = os.getcwd()
    os.chdir(target)

    yield

    os.chdir(start)
