
import unittest
import os
import astropy.io.fits
import astropy.units

import n2.data
import n2.data.image.funcs as funcs

deg = astropy.units.deg


class TestDataImageFunc(unittest.TestCase):
    def setUp(self):
        self.datadir = os.path.join(n2.data.__path__[0], 'image', 'tests')
        return
    
    def test_cut_pix_2d(self):
        f = 'fk5_tan_large.fits.gz'
        p = os.path.join(self.datadir, f)
        hdu = astropy.io.fits.open(p)[0]
        
        hdu2 = funcs.cut_pix(hdu)
        self.assertEqual((hdu2.data - hdu.data).sum(), 0)
        
        hdu3_ = funcs.cut_pix(hdu, [20, 110], [30, 65])
        try:
            hdu3_.writeto(p+'.cutp2.fits.gz', overwrite=True)
        except OSError:
            pass
        f3 = 'fk5_tan_large.fits.gz.cutp2.fits.gz'
        p3 = os.path.join(self.datadir, f3)
        hdu3 = astropy.io.fits.open(p3)[0]        
        self.assertEqual((hdu3_.data - hdu3.data).sum(), 0)
            
        hdu4 = funcs.cut_pix(hdu, [20, 110], [30, -35])
        self.assertEqual((hdu3_.data - hdu4.data).sum(), 0)
        
        hdu5 = funcs.cut_pix(hdu, [20, -30], [20, -30])
        self.assertRaises(ValueError, (lambda:hdu3_.data - hdu5.data))
        return
        
    def test_cut_world_2d(self):
        f = 'fk5_tan_large.fits.gz'
        p = os.path.join(self.datadir, f)
        hdu = astropy.io.fits.open(p)[0]
        
        hdu2 = funcs.cut_world(hdu, [84.3, 83.35]*deg, [-5.2, -4.5]*deg)
        self.assertNotEqual(hdu2.data.sum(), hdu.data.sum())
        try:
            hdu2.writeto(p+'.cutw2.fits.gz', overwrite=True)
        except OSError:
            pass
        f2 = 'fk5_tan_large.fits.gz.cutw2.fits.gz'
        p2 = os.path.join(self.datadir, f2)
        hdu2_ = astropy.io.fits.open(p2)[0]        
        self.assertEqual((hdu2.data - hdu2_.data).sum(), 0)

        hdu3 = funcs.cut_world(hdu, [84.3, 82.5]*deg, [-5.2, -4.5]*deg)
        self.assertRaises(ValueError, (lambda:hdu3.data - hdu.data))
        return
        
        

if __name__=='__main__':
    unittest.main()

