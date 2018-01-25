
import unittest

import os
import io
import n2.cache

class TestCache(unittest.TestCase):
    def setUp(self):
        n2.cache.clean()
        return
        
    def tearDown(self):
        n2.cache.clean()
        return
    
    def test_clean(self):
        n2.cache.clean()
        ret = os.path.exists(n2.cache.CACHE_DIR)
        self.assertFalse(ret)
        return
        
    def test_hash(self):
        d1 = '1234567890'
        h1 = '01b307acba4f54f55aafc33bb06bbbf6ca803e9a'
        ret1 = n2.cache.hash(d1)
        self.assertEqual(ret1, h1)
        
        d2 = b'\x00' * 4096
        h2 = '1ceaf73df40e531df3bfb26b4fb7cd95fb7bff1d'
        ret2 = n2.cache.hash(d2)
        self.assertEqual(ret2, h2)        
        return
        
    def test_save(self):
        key1 = 'test_save_1'
        io1 = io.BytesIO(key1.encode('utf-8'))
        n2.cache.save(key1, io1)
        ret1 = os.path.exists(n2.cache.cache.getpath(key1))
        self.assertTrue(ret1)
        return
    
    def test_open(self):
        key1 = 'test_open_1'
        io1 = io.BytesIO(key1.encode('utf-8'))
        n2.cache.save(key1, io1)
        io1_2 = n2.cache.open(key1)
        io1.seek(0)
        self.assertTrue(io1.read(), io1_2.read())
        
        key2 = 'test_open_2'
        self.assertRaises(FileNotFoundError, n2.cache.open, key2)
        return


if __name__=='__main__':
    unittest.main()

