import contextlib
import copy
import os
import shlex
import subprocess


# -----------------------------------------------------------------------------
# This allows for doing things like
#      orig = os.getcwd()
#      with chdir('/somewhere/else'):
#           ... do stuff ...
#      assert orig == os.getcwd()
#
@contextlib.contextmanager
def chdir(target):
    try:
        start = os.getcwd()
        os.chdir(target)
        yield

    finally:
        os.chdir(start)


# -----------------------------------------------------------------------------
def contents(path, type=None, default=None):
    """
    Return the contents of file *path* as *type* (string [default], or list)
    """
    try:
        with open(path, 'r') as f:
            if type == list:
                rv = f.readlines()
            else:
                rv = f.read()
    except IOError as e:
        if default is not None:
            rv = default
        else:
            raise
    return rv


# -----------------------------------------------------------------------------
def revnumerate(seq):
    """
    Enumerate a copy of a sequence in reverse as a generator

    Often this will be used to scan a list backwards so that we can add things
    to the list without disturbing the indices of earlier elements. We don't
    want the list changing out from under us as we work on it, so we scan a
    copy rather than the origin sequence.
    """
    n = len(seq) - 1
    seqcopy = copy.deepcopy(seq)
    for elem in reversed(seqcopy):
        yield n, elem
        n -= 1


# -----------------------------------------------------------------------------
def run(cmd, input=None):
    """
    Run *cmd*, optionally passing string *input* to it on stdin, and return
    what the process writes to stdout
    """
    try:
        p = subprocess.Popen(shlex.split(cmd),
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        if input:
            p.stdin.write(input)
        (o, e) = p.communicate()
        if p.returncode == 0:
            rval = o
        else:
            rval = 'ERR:' + e
    except OSError as e:
        if 'No such file or directory' in str(e):
            rval = 'ERR:' + str(e)
        else:
            raise

    return rval


