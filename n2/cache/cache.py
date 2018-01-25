
import os
import io
import shutil
import hashlib

open_ = open

CACHE_DIR = '.n2cache'


def make_cache_dir():
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
        pass
    return


def clean():
    if os.path.exists(CACHE_DIR):
        shutil.rmtree(CACHE_DIR)
        pass
    return


def hash(key):
    if type(key) == str:
        key = key.encode('utf-8')
        pass
    
    hash_ = hashlib.sha1(key).hexdigest()
    return hash_


def getpath(key):
    hash_ = hash(key)
    target = os.path.join(CACHE_DIR, hash_)
    return target


def open(key):
    target = getpath(key)
    with open_(target, 'rb') as f:
        io_ = io.BytesIO(f.read())
        pass
    io_.seek(0)
    return io_


def save(key, io_):
    target = getpath(key)
    make_cache_dir()
    with open_(target, 'wb') as f:
        io_.seek(0)
        f.write(io_.read())
        pass
    return



__all__ = ['CACHE_DIR', 'clean', 'hash', 'open', 'save']
