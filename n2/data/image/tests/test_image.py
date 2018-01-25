
import unittest
import os

import n2.data
import n2.cache


class TestDataImage(unittest.TestCase):
    def setUp(self):
        self.datadir = os.path.join(n2.data.__path__[0], 'image', 'tests')
        return
    
    def tearDown(self):
        n2.cache.clean()
        return

    def test_open(self):
        f = 'fk5_tan_large.fits.gz'
        p = os.path.join(self.datadir, f)
        i = n2.data.image.open(p)
        return
        
    def test_open_cache_file(self):
        f = 'fk5_tan_large.fits.gz'
        p = os.path.join(self.datadir, f)
        i = n2.data.image.open(p)
        i2 = n2.data.image.open_cache_file(i.key)
        self.assertEqual(i, i2)
        return
    
    def test_create_history(self):
        a = ['a', 9.2, [1,2]]
        k = {'%s'%i: i for i in range(5)}
        h = n2.data.image.image.create_history('t', *a, **k)
        
        h0 = "t ('a', 9.2, [1, 2]) {'0': 0, '1': 1, '2': 2, '3': 3, '4': 4}\n"
        self.assertEqual(h, h0)
        return
    
    def test_testfunc_zero(self):
        f = 'fk5_tan_large.fits.gz'
        p = os.path.join(self.datadir, f)
        d = n2.data.image.open(p)
        d2 = d._testfunc_zero()
        self.assertNotEqual(d, d2)
        return
    



if __name__=='__main__':
    unittest.main()
