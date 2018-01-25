
from . import image

import os
import astropy.io.fits


def open(path, nocache=False, compress=False):
    if path.endswith('.fits') or path.endswith('.fits.gz'):
        hdunum = 0
        hdu = astropy.io.fits.open(path)[hdunum]
        kwargs = {'path': path, 'hdunum': 0}
        history = 'open {kwargs}'.format(**locals())
        d = image.fitsimage(hdu, history)
        return d
