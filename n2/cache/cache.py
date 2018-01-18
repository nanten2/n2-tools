

import os
import shutil
import hashlib


CACHE_DIR = '.n2cache'


def get_cache_dir_path():
    cwd = os.getcwd()
    cache_dir = os.path.join(cwd, CACHE_DIR)
    return cache_dir


def make_cache_dir():
    target = get_cache_dir_path()
    
    if os.path.exists(target):
        return
    
    os.makedirs(target)
    return


def clean():
    target = get_cache_dir_path()
    
    if not os.path.exists(target):
        return
    
    shutil.rmtree(target)
    return


def hash(key):
    if type(key) == str:
        key = key.encode('utf-8')
        pass
    
    hash_ = hashlib.sha1(key).hexdigest()
    return hash_


def exists(key, ext=''):
    make_cache_dir()
    hash_ = hash(key)
    target_dir = get_cache_dir_path()
    target = os.path.join(target_dir, hash_) + ext
    return os.path.exists(target)


def get_path(key, ext=''):
    make_cache_dir()
    hash_ = hash(key)
    target_dir = get_cache_dir_path()
    target = os.path.join(target_dir, hash_) + ext
    return target


__all__ = ['CACHE_DIR', 'clean',
           'hash', 'exists', 'get_path']
