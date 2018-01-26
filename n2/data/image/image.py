
import n2.cache
from . import funcs

import os
import io
import astropy.io.fits


def open(path, hdu_num=0):
    hdu = astropy.io.fits.open(path)[hdu_num]
    
    history = create_history('open', path=path, hdu_num=hdu_num)
    fimage = fitsimage(hdu, history)
    return fimage

def open_cache_file(key):
    io_ = n2.cache.open(key)
    hdu = astropy.io.fits.open(io_)[0]
    fimage = fitsimage(hdu, key, save_cache_file=False)
    return fimage

def dict2str(dict_):
    s = '{'
    for key, value in sorted(dict_.items()):
        s += "'{0}': {1}, ".format(key, value)
        continue
    s = s.strip(', ')
    s += '}'
    return s

def create_history(funcname, *args, **kwargs):
    kw = dict2str(kwargs)
    new_history = '{funcname} {args} {kw}\n'.format(**locals())
    return new_history

def use_cache_if_exists(func):
    def wrapper(*args, **kwargs):
        funcname = func.__name__
        args2 = list(args)
        self = args2.pop(0)
        #print(args2, kwargs)
        new_hist = create_history(funcname, *args2, **kwargs)
        new_key = self.history + new_hist
        
        try:
            new_fimage = open_cache_file(new_key)
            return new_fimage
            
        except FileNotFoundError:
            pass
    
        new_hdu = func(*args, **kwargs)
        new_fimage = fitsimage(new_hdu, new_key)
        return new_fimage
    
    return wrapper



class fitsimage(object):
    hdu = None
    history = ''
    id = ''
    
    def __init__(self, hdu, history, save_cache_file=True):
        self.hdu = hdu
        self.history = history
        self._update_id()
        if save_cache_file:
            self.save_cache_file()
            pass
        pass
        
    def __eq__(self, target):
        if isinstance(target, fitsimage):
            return self.id == target.id
        return False

    def _update_id(self):
        self.key = self.history
        self.id = n2.cache.hash(self.key)
        return
    
    def save_cache_file(self):
        io_ = io.BytesIO()
        self.hdu.writeto(io_)
        n2.cache.save(self.key, io_)
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
        new_hdu = funcs.cut_pix(self.hdu, x, y, z)
        return new_hdu
        
    @use_cache_if_exists
    def cut_world(self, x=None, y=None, z=None):
        new_hdu = funcs.cut_world(self.hdu, x, y, z)
        return new_hdu
        
    @use_cache_if_exists
    def decimate(self, xy=None, z=None):
        new_hdu = funcs.decimate(self.hdu, xy, z)
        return new_hdu
        
    @use_cache_if_exists
    def regrid(self, output_header, hdu_in=0, order=u'bilinear',
               independent_celestial_slices=False):
        new_hdu = funcs.reproject(self.hdu, output_header,
                                  hdu_in = hdu_in,
                                  order = order
                                  independent_celestial_slices = independent_celestial_slices)
        return new_hdu
        
        




__all__ = ['open', 'open_cache_file', 'fitsimage']


