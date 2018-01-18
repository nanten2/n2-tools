
import unittest

import os
import cache

class TestCache(unittest.TestCase):
    def setUp(self):
        cache.clean()
        return
        
    def tearDown(self):
        cache.clean()
        return
    
    def test_make_cache_dir(self):
        cache.make_cache_dir()
        cache_dir_path = cache.get_cache_dir_path()
        ret = os.path.exists(cache_dir_path)
        self.assertTrue(ret)
        return
        
    def test_clean(self):
        cache.clean()
        cache_dir_path = cache.get_cache_dir_path()
        ret = os.path.exists(cache_dir_path)
        self.assertFalse(ret)
        return
        
    def test_hash(self):
        d1 = '1234567890'
        h1 = '01b307acba4f54f55aafc33bb06bbbf6ca803e9a'
        ret1 = cache.hash(d1)
        self.assertEqual(ret1, h1)
        
        d2 = b'\x00' * 4096
        h2 = '1ceaf73df40e531df3bfb26b4fb7cd95fb7bff1d'
        ret2 = cache.hash(d2)
        self.assertEqual(ret2, h2)        
        return
        
    def test_get_path(self):
        key1 = 'test_get_path_1'
        path1 = cache.get_path(key1)
        with open(path1, 'w') as f:
            f.write(key1)
            pass
        ret1 = os.path.exists(path1)
        self.assertTrue(ret1)
        
        key2 = 'test_get_path_2'
        ext2 = '.fits'
        path2 = cache.get_path(key2, ext2)
        with open(path2, 'w') as f:
            f.write(key2+ext2)
            pass
        ret2 = os.path.exists(path2)
        self.assertTrue(ret2)
        return
        
    def test_exists(self):
        key1 = 'test_exists_1'
        path1 = cache.get_path(key1)
        with open(path1, 'w') as f:
            f.write(key1)
            pass
        ret1 = cache.exists(key1)
        self.assertTrue(ret1)
        
        key2 = 'test_exists_2'
        ext2 = '.fits'
        path2 = cache.get_path(key2, ext2)
        with open(path2, 'w') as f:
            f.write(key2+ext2)
            pass
        ret2 = cache.exists(key2, ext2)
        self.assertTrue(ret2)
        return


if __name__=='__main__':
    unittest.main()

