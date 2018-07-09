
import n2.cache
import n2.core
import n2.log
logger = n2.log.get_logger(__name__)

import io
import os
import numpy
import astropy.io.fits
import astropy.wcs
import astropy.units



FITS_AUTO_CACHE = True


def open_fits(path, hdu_num=0):
    logger.info('(open_fits) path={path}, hdu_num={hdu_num}'.format(**locals()))
    hdul = astropy.io.fits.open(path)
    hdu = hdul[hdu_num]
    if read_n2hist(hdu) == '\n':
        filename = os.path.basename(path)
        add_n2hist(hdu, 'open_fits', filename=filename, hdu_num=hdu_num)
        pass
    fimage = fitsimage(hdu, _save_cache=False)
    return fimage

def verify_header(hdu):
    if hdu.header.get('BUNIT', '') == '':
        logger.warning('(verify_header) Empty keyword: BUNIT')
        pass

    if hdu.header.get('BMAJ', '') == '':
        logger.warning('(verify_header) Empty keyword: BMAJ')
        pass

    if hdu.header.get('BMIN', '') == '':
        logger.warning('(verify_header) Empty keyword: BMIN')
        pass
    return
        

def read_n2hist(hdu):
    try:
        hist = hdu.header['HISTORY']
    except KeyError:
        hist = []
        pass
    
    n2hist = '\n'.join([_ for _ in str(hist).split('\n')
                        if _.startswith('n2:')])
    return n2hist + '\n'

def add_n2hist(hdu, funcname, *args, **kwargs):
    n2hist = gen_n2hist(funcname, *args, **kwargs)
    [hdu.header.add_history(_) for _ in n2hist.split('\n')]
    return

def gen_n2hist(funcname, *args, **kwargs):
    n2hist = ''
    n2hist += 'n2: {funcname}\n'.format(**locals())
    n2hist += 'n2: ' + '-' * len(funcname) + '\n'
    
    for i, arg in enumerate(args):
        n2hist += 'n2: args[{i}] = {arg}\n'.format(**locals())
        continue
        
    for key, value in sorted(kwargs.items()):
        n2hist += 'n2: {key} = {value}\n'.format(**locals())
        continue
    
    n2hist += 'n2:\n'
    return n2hist

    


def save_cache(hdu, key):
    io_ = io.BytesIO()
    hdu.writeto(io_)
    n2.cache.save(key, io_)
    return

def open_cache(key):
    io_ = n2.cache.open(key)
    hdu = astropy.io.fits.open(io_)[0]
    
    fimage = fitsimage(hdu)
    return fimage
    
def use_cache_if_exists(func):
    def wrapper(*args, **kwargs):
        args2 = list(args)
        self = args2.pop(0)
        funcname = func.__name__
        new_hist = gen_n2hist(funcname, *args2, **kwargs)
        new_key = self.read_n2hist() + new_hist
        
        try:
            new_fimage = open_cache(new_key)
            return new_fimage
            
        except FileNotFoundError:
            pass
        
        new_hdu = func(*args, **kwargs)
        add_n2hist(new_hdu, funcname, *args2, **kwargs)
        new_fimage = fitsimage(new_hdu)
        return new_fimage
    
    return wrapper




class fitsimage(object):
    def __init__(self, hdu, _save_cache=FITS_AUTO_CACHE):
        self.hdu = hdu
        self.data = hdu.data
        self.header = hdu.header
        self.verify_header()
        self.wcs = astropy.wcs.WCS(hdu)
        if self.wcs.naxis > 2:
            self.wcs2 = astropy.wcs.WCS(hdu, naxis=2)
            pass
        if _save_cache:
            self.save_cache()
            pass
        pass
    
    def verify_header(self):
        verify_header(self.hdu)
        return
    
    def read_n2hist(self):
        return read_n2hist(self.hdu)
        
    def show_n2hist(self):
        n2hist = self.read_n2hist()
        print(n2hist)
        return
        
    def info(self):
        def human_readable(size):
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if size < 1000:
                    return '{size:3.1f} {unit}'.format(**locals())
                    pass
                size /= 1000
                continue
            return
        
        bitpix = self.header['BITPIX']
        size = human_readable(self.hdu.data.size * abs(bitpix / 8))
        wcs = str(self.wcs).split('\n\n')[1]
        units = [astropy.units.Unit(self.header.get('CUNIT%d'%(i+1), 'deg'))
                 for i in range(self.hdu.data.ndim)]
        
        center_pix = numpy.array(self.hdu.shape[::-1]) / 2
        center_world_ = self.wcs.all_pix2world([center_pix], 0)[0]
        center_world = '  '.join(['%.3f %s'%(cw, u) for cw, u in zip(center_world_, units)])
        width = '  '.join(['%.3f %s'%(abs(self.header['CDELT%d'%(i+1)]*self.header['NAXIS%d'%(i+1)]), u)
                           for i, u in enumerate(units)])
        
        tel = self.header.get('TELESCOP', '')
        rx = self.header.get('INSTRUME', '')
        line = self.header.get('LINE', '')
        bunit = self.header.get('BUNIT', '')
        hpbw1 = self.header.get('BMAJ', 0) * 3600
        hpbw2 = self.header.get('BMIN', 0) * 3600
        
        print('OBS : {tel} / {rx}'.format(**locals()))
        print('LINE : {line} ({bunit})'.format(**locals()))
        print('HPBW : {hpbw1} x {hpbw2} arcsec'.format(**locals()))
        print('')
        print('size : {size}'.format(**locals()))
        print('BITPIX : {bitpix}'.format(**locals()))
        print('')
        print('Center : {center_world}'.format(**locals()))
        print('Width : {width}'.format(**locals()))
        print('')
        print(wcs)

        return

    def save_cache(self):
        key = self.read_n2hist()
        save_cache(self.hdu, key)
        return
    
    def writeto(self, path, **kwargs):
        self.hdu.writeto(path, **kwargs)
        return

    @use_cache_if_exists
    def _testfunc_zero(self):
        new_hdu = self.hdu.copy()
        new_hdu.data *= 0
        return new_hdu

    @use_cache_if_exists
    def _testfunc_many_args(self, a=0, b=0, c=0, d=0, e=0, f=0, g=0, h=0, i=0,
                            j=0, k=0, l=0, m=0, n=0, o=0, p=0, q=0, r=0, s=0):
        new_hdu = self.hdu.copy()
        new_hdu.data = (new_hdu.data * 0) + 1
        return new_hdu

    @use_cache_if_exists
    def cut_pix(self, x=None, y=None, z=None):
        new_hdu = n2.core.cut_pix(self.hdu, x, y, z)
        return new_hdu
        
    @use_cache_if_exists
    def cut_world(self, x=None, y=None, z=None):
        new_hdu = n2.core.cut_world(self.hdu, x, y, z)
        return new_hdu

    @use_cache_if_exists
    def convolve_pix(self, stddev):
        new_hdu = n2.core.convolve_pix(self.hdu, stddev)
        return new_hdu

    @use_cache_if_exists
    def convolve_world(self, target_hpbw):
        new_hdu = n2.core.convolve_world(self.hdu, target_hpbw)
        return new_hdu

    @use_cache_if_exists
    def velocity_binning_pix(self, nbin):
        new_hdu = n2.core.velocity_binning_pix(self.hdu, nbin)
        return new_hdu

    @use_cache_if_exists
    def velocity_binning_world(self, width):
        new_hdu = n2.core.velocity_binning_world(self.hdu, width)
        return new_hdu
    
    @use_cache_if_exists
    def peak(self):
        new_hdu = n2.core.peak(self.hdu)
        return new_hdu
        
    @use_cache_if_exists
    def mom0(self):
        new_hdu = n2.core.mom0(self.hdu)
        return new_hdu
        

__all__ = [
    'FITS_AUTO_CACHE',
    'open_fits',
]


