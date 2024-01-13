# Thanks to ChatGPT and @obgnaw (https://stackoverflow.com/a/52960835/21127400) :-)
# TODO: Develop, find better solutions and implement and use this on data managers (like SessionManager)

import os
import sys
if sys.platform == "linux" or sys.platform == "linux2":
    import fcntl
    class LockDirectory(object):
        def __init__(self, directory):
            assert os.path.exists(directory)
            self.directory = directory

        def __enter__(self):
            self.dir_fd = os.open(self.directory, os.O_RDONLY)
            try:
                fcntl.flock(self.dir_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except IOError as ex:             
                raise Exception('Somebody else is locking %r.' % self.directory)
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            # fcntl.flock(self.dir_fd,fcntl.LOCK_UN)
            os.close(self.dir_fd)
elif sys.platform == "win32":
    import portalocker
    class LockDirectory(object):
        def __init__(self, directory):
            assert os.path.exists(directory)
            self.directory = directory

        def __enter__(self):
            lock_file_path = os.path.join(self.directory, ".lock")

            try:
                self.lock_file = open(lock_file_path, "w")
                portalocker.lock(self.lock_file, portalocker.LOCK_EX | portalocker.LOCK_NB)
            except portalocker.LockException:
                self.lock_file.close()
                raise Exception(f"Somebody else is locking {self.directory}.")

            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            portalocker.unlock(self.lock_file)
            self.lock_file.close()
else:
    raise Exception("Unsupported Operating System!")
import time