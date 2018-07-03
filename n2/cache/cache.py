
import n2.log
logger = n2.log.get_logger(__name__)

import os
import io
import shutil
import hashlib


open_ = open

CACHE_DIR = '.n2cache'


def make_cache_dir():
    if not os.path.exists(CACHE_DIR):
        logger.debug('(cache.make_cache_dir)'.format(**locals()))
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
        logger.info('(cache.open) {target}'.format(**locals()))
        io_ = io.BytesIO(f.read())
        pass
    io_.seek(0)
    return io_


def save(key, io_):
    target = getpath(key)
    
    if os.path.exists(target):
        return
    
    make_cache_dir()
    logger.info('(cache.save) {target}'.format(**locals()))
    with open_(target, 'wb') as f:
        io_.seek(0)
        f.write(io_.read())
        pass
    return



__all__ = ['CACHE_DIR', 'clean', 'hash', 'open', 'save']
