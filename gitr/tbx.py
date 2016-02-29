"""
Toolbox utilities
"""
import contextlib
import copy
import os
import shlex
import subprocess


# -----------------------------------------------------------------------------
@contextlib.contextmanager
def chdir(target):
    """
    This allows for doing things like
        orig = os.getcwd()
        with chdir('/somewhere/else'):
            ... do stuff ...
        assert orig == os.getcwd()
    """
    try:
        start = os.getcwd()
        os.chdir(target)
        yield

    finally:
        os.chdir(start)


# -----------------------------------------------------------------------------
@contextlib.contextmanager
def tmpenv(**kw):
    """
    Set one or more environment variables that will return to their previous
    setting when the context goes out of scope.
    """
    prev = {}
    try:
        for k in kw:
            if k in os.environ:
                prev[k] = os.environ[k]
            if kw[k] is None:
                del os.environ[k]
            else:
                os.environ[k] = kw[k]
        yield
    finally:
        for k in kw:
            if k in prev:
                os.environ[k] = prev[k]
            elif k in os.environ:
                del os.environ[k]


# -----------------------------------------------------------------------------
def contents(path, rtype=None, default=None):
    """
    Return the contents of file *path* as *rtype* (string [default], or list)
    """
    try:
        with open(path, 'r') as rable:
            if rtype == 'list':
                rval = rable.readlines()
            else:
                rval = rable.read()
    except IOError:
        if default is not None:
            rval = default
        else:
            raise
    return rval


# -----------------------------------------------------------------------------
def dirname(path):
    """
    Convenience wrapper for os.path.dirname()
    """
    return os.path.dirname(path)


# -----------------------------------------------------------------------------
def revnumerate(seq):
    """
    Enumerate a copy of a sequence in reverse as a generator

    Often this will be used to scan a list backwards so that we can add things
    to the list without disturbing the indices of earlier elements. We don't
    want the list changing out from under us as we work on it, so we scan a
    copy rather than the origin sequence.
    """
    j = len(seq) - 1
    seqcopy = copy.deepcopy(seq)
    for elem in reversed(seqcopy):
        yield j, elem
        j -= 1


# -----------------------------------------------------------------------------
def run(cmd, inps=None):
    """
    Run *cmd*, optionally passing string *input* to it on stdin, and return
    what the process writes to stdout
    """
    try:
        proc = subprocess.Popen(shlex.split(cmd),
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        if inps:
            proc.stdin.write(inps)
        (stdo, stde) = proc.communicate()
        if proc.returncode == 0:
            rval = stdo
        else:
            rval = 'ERR:' + stde
    except OSError as err:
        if 'No such file or directory' in str(err):
            rval = 'ERR:' + str(err)
        else:
            raise

    return rval


