import os
import tempfile
import atexit
import sys

def temporaryFilename(prefix=None, suffix='tmp', dir=None, text=False, removeOnExit=True):
    """Returns a temporary filename that, like mkstemp(3), will be secure in
    its creation.  The file will be closed immediately after it's created, so
    you are expected to open it afterwards to do what you wish.  The file
    will be removed on exit unless you pass removeOnExit=False.  (You'd think
    that amongst the myriad of methods in the tempfile module, there'd be
    something like this, right?  Nope.)"""

    if prefix is None:
        prefix = "%s_%d_" % (os.path.basename(sys.argv[0]), os.getpid())

    (fileHandle, path) = tempfile.mkstemp(prefix=prefix, suffix=suffix, dir=dir, text=text)
    os.close(fileHandle)

    def removeFile(path):
        os.remove(path)

    if removeOnExit:
        atexit.register(removeFile, path)

    return path