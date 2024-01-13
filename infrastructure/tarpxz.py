import json
import subprocess
import hashlib
import os
import tempfile
import atexit
import sys
import tarfile
import shutil
import threading
import time

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

def read_file(filename: str, tar_path: str) -> bytes:
    temp = temporaryFilename()
    status, out = subprocess.getstatusoutput(f"pixz -x {os.path.join('./', filename)} < {tar_path} | tar -xO {os.path.join('./', filename)} > {temp}")

    if status == 2 and out.startswith('/bin/sh: 1: cannot open '):
        raise FileNotFoundError(f'tarball ("{tar_path}") not found.')
    if status == 2:
        raise FileNotFoundError(f'"{filename}" not found in tarball.')

    with open(temp, 'rb') as f:
        return f.read()
    
def seconds_to_printable(seconds: int):
    secs = seconds%60
    seconds = int((seconds - secs)/60)
    mins = seconds%60
    seconds = int((seconds - mins)/60)
    hours = int(seconds)
    return f'{str(hours).rjust(3, "0")}:{str(mins).rjust(2, "0")}:{str(secs).rjust(2, "0")}'

def open_tpxz(tpxz_path: str, dir:str|None=None) -> str:
    temp_file = os.path.join(dir or 'data/temp', 'TRUP-application-data-'+hashlib.sha224(os.urandom(32)).hexdigest()+'.tar')
    with open(temp_file, 'wb') as _:
        pass
    command = ['pixz', '-d', os.path.abspath(tpxz_path),  temp_file]
    print(' '.join(command))
    blocks = [int(i.split('/')[1].strip()) for i in subprocess.getoutput('pixz -l -t ' + tpxz_path).split('\n')]
    filesize = sum(blocks)
    full = filesize/(1000*1000*1000)
    print(filesize/(1000*1000*1000))

    start = time.monotonic()

    with subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=1, universal_newlines=True) as p:
        while True:
            current = (os.stat(temp_file).st_size+1)/(1000*1000*1000)

            _elapsed = int((time.monotonic() - start) + 1)
            _estimated = int(_elapsed/current * full)

            print(f'\r{current:.2f}/{full:.2f}, {seconds_to_printable(_elapsed)}/{seconds_to_printable(_estimated)}', end='      ', flush=True)
            time.sleep(0.1)
            if p.poll() is not None:
                print('\nFinished                                       ', flush=True)
                break

    return temp_file

class tarball():
    def __init__(self, tar_path: str, destination=None, remove_on_exit=True):
        self.remove_on_exit = remove_on_exit
        self.destination = destination
        self.tar_path = tar_path

        self.path = os.path.abspath(self.destination) if self.destination is not None else tempfile.TemporaryDirectory().name
        tar = tarfile.open(self.tar_path)
        for member in tar.getmembers():
            f = tar.extractfile(member)
            if f is not None:
                print('\r' + member.name[:50], end=' '*(50 - len(member.name[:50])), flush=True)
                pth = os.path.join(self.path, member.name.removeprefix('./'))
                dir = ''
                for i in pth.split('/')[1:-1]:
                    dir += '/'+i
                    if not os.path.exists(dir):
                        os.mkdir(dir)
                with open(pth, 'wb') as o:
                    o.write(f.read())
        
        if remove_on_exit:
            os.remove(tar_path)

        #status, out = subprocess.getstatusoutput(f"pixz -x {os.path.join('./', filename)} < {tar_path} | tar -xO {os.path.join('./', filename)} > {temp}")
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, trace):
        if self.remove_on_exit:
            shutil.rmtree(self.path)

def get_hash(data:bytes)->str:
    return hashlib.sha512(data, usedforsecurity=False).hexdigest()

tree = {}

app = "Raft"
version = "1.0"

with tarball(open_tpxz('Raft.tpxz'), f'data/uploads/apps/{app}/versions/{version}/') as ball:
    list = subprocess.getoutput('pixz -l Raft.tpxz').split('\n')

    for path in list:
        path = path.removeprefix('./')
        loc = tree
        for i in path.split('/'):
            if i == '':
                continue
            if i in loc:
                loc = loc[i]
            elif path.endswith('/'):
                loc[i] = {}
                loc = loc[i]
            else:
                with open(os.path.join(ball.path, path), 'rb') as f:
                    loc[i] = get_hash(f.read())

    print(json.dumps(tree, indent=4))