
import n2.cache
import n2.core
import n2.log
logger = n2.log.get_logger(__name__)

import io
import os
import functools
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

    hdu.header['N2HASH'] = n2.cache.hash(read_n2hist(hdu.header))
    fimage = fitsimage(hdu, _save_cache=False)
    return fimage

def verify_header(hdu):
    if hdu.header.get('BUNIT', None) == None:
        logger.warning('(verify_header) Empty keyword: BUNIT')
        pass

    if hdu.header.get('BMAJ', '') == '':
        logger.warning('(verify_header) Empty keyword: BMAJ')
        pass

    if hdu.header.get('BMIN', '') == '':
        logger.warning('(verify_header) Empty keyword: BMIN')
        pass
    return
        

def read_n2hist(hdu_or_header):
    if isinstance(hdu_or_header, astropy.io.fits.Header):
        header = hdu_or_header
    else:
        header = hdu_or_header.header
        pass
    
    try:
        hist = header['HISTORY']
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
        if isinstance(arg, astropy.io.fits.Header):
            arg = n2.cache.hash(str(arg))
            pass
        n2hist += 'n2: args[{i}] = {arg}\n'.format(**locals())
        continue
        
    for key, value in sorted(kwargs.items()):
        if isinstance(value, astropy.io.fits.Header):
            value = n2.cache.hash(str(value))
            pass
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
    @functools.wraps(func)
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
        new_hdu.header['N2HASH'] = n2.cache.hash(read_n2hist(new_hdu.header))
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
        else:
            self.wcs2 = self.wcs
            pass

        self.bunit = astropy.units.Unit(hdu.header.get('BUNIT', ''))        
        
        if _save_cache:
            self.save_cache()
            pass
        self.writeto = self.hdu.writeto
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
    
    def get_vaxis(self):
        indv = numpy.arange(self.header['NAXIS3'])
        pix = numpy.array([indv*0, indv*0, indv]).T
        v = self.wcs.all_pix2world(pix, 0).T[2]
        cunit = astropy.units.Unit(self.header['CUNIT3'])
        return v * cunit

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
    def single_ch(self, ch):
        new_hdu = n2.core.single_ch(self.hdu, ch)
        return new_hdu
    
    @use_cache_if_exists
    def peak(self):
        new_hdu = n2.core.peak(self.hdu)
        return new_hdu
        
    @use_cache_if_exists
    def mom0(self):
        new_hdu = n2.core.mom0(self.hdu)
        return new_hdu
        
    @use_cache_if_exists
    def mom1(self):
        new_hdu = n2.core.mom1(self.hdu)
        return new_hdu

    @use_cache_if_exists
    def mom2(self):
        new_hdu = n2.core.mom2(self.hdu)
        return new_hdu

    @use_cache_if_exists
    def moment_mask(self, smooth_xy=0, smooth_v=0, nsig=5, minsize=5):
        new_hdu = n2.core.moment_mask(self.hdu, smooth_xy, smooth_v,
                                      nsig, minsize)
        return new_hdu

    @use_cache_if_exists
    def regrid(self, output_header, order='bilinear'):
        new_hdu = n2.core.regrid(self.hdu, output_header, order)
        return new_hdu
    
    @use_cache_if_exists
    def pv(self, sumaxis):
        new_hdu = n2.core.pv(self.hdu, sumaxis)
        return new_hdu
    
    @use_cache_if_exists
    def apply_mask(self, mask):
        new_hdu = n2.core.apply_mask(self.hdu, mask)
        return new_hdu
    
    @use_cache_if_exists
    def mask_inpolygon(self, polygon, axis=None):
        new_hdu = n2.core.mask_inpolygon(self.hdu, polygon)
        return new_hdu
    
    @use_cache_if_exists
    def tex(self, tau, freq=None, Tbg=2.725*astropy.units.K):
        new_hdu = n2.core.tex(self.hdu, tau, freq, Tbg)
        return new_hdu
    
    @use_cache_if_exists
    def tex_optically_thick(self, freq=None, Tbg=2.725*astropy.units.K):
        new_hdu = n2.core.tex(self.hdu, numpy.inf, freq, Tbg)
        return new_hdu
    
    @use_cache_if_exists
    def tau(self, tex, freq=None, Tbg=2.725*astropy.units.K):
        new_hdu = n2.core.tau(self.hdu, tex, freq, Tbg)
        return new_hdu
    
    @use_cache_if_exists
    def column_density_upper(self, tex, EinsteinA=None, freq=None):
        new_hdu = n2.core.column_density_upper(self.hdu, tex, EinsteinA, freq)
        return new_hdu
    
    @use_cache_if_exists
    def column_density_total_LTE(self, Tk, level=None, B=None):
        new_hdu = n2.core.column_density_total_LTE(self.hdu, Tk, level, B)
        return new_hdu
    
    @use_cache_if_exists
    def convert_N13CO_to_NH2(self, factor='Frerking1982'):
        new_hdu = n2.core.convert_N13CO_to_NH2(self.hdu, factor)
        return new_hdu
    
    @use_cache_if_exists
    def convert_NC18O_to_NH2(self, factor='Frerking1982'):
        new_hdu = n2.core.convert_NC18O_to_NH2(self.hdu, factor)
        return new_hdu
    
    @use_cache_if_exists
    def convert_to_NH2(self, factor='Okamoto2017'):
        new_hdu = n2.core.convert_to_NH2(self.hdu, factor)
        return new_hdu
    
    

__all__ = [
    'FITS_AUTO_CACHE',
    'open_fits',
]


