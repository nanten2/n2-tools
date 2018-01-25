

import astropy.io.fits


def cut_pix(hdu, x=None, y=None, z=None):
    if hdu.header['NAXIS'] == 2:
        return cut_pix_2d(hdu, x, y)
        
    elif hdu.header['NAXIS'] == 3:
        return cut_pix_3d(hdu, x, y, z)
    
    return


def cut_pix_2d(hdu, x=None, y=None):
    x0 = 0
    y0 = 0
    x1 = hdu.header['NAXIS1']
    y1 = hdu.header['NAXIS2']
    
    if x is None:
        xr0 = x0
        xr1 = x1
    else:
        xr0 = x[0] if x[0] >= x0 else x0
        xr1 = x[1] if x[1] <= x1 else x1
        pass
    
    if y is None:
        yr0 = y0
        yr1 = y1
    else:
        yr0 = y[0] if y[0] >= y0 else y0
        yr1 = y[1] if y[1] <= y1 else y1
        pass
    
    newd = hdu.data[yr0:yr1, xr0:xr1]
    newh = hdu.header.copy()
    newh['NAXIS1'] = xr1 - xr0
    newh['NAXIS2'] = yr1 - yr0
    newh['CRPIX1'] = hdu.header['CRPIX1'] - xr0
    newh['CRPIX2'] = hdu.header['CRPIX2'] - yr0
    newhdu = astropy.io.fits.PrimaryHDU(newd, newh)
    return newhdu
    
    
def cut_pix_3d(hdu, x=None, y=None, z=None):
    x0 = 0
    y0 = 0
    z0 = 0
    x1 = hdu.header['NAXIS1']
    y1 = hdu.header['NAXIS2']
    z1 = hdu.header['NAXIS3']
    
    if x is None:
        xr0 = x0
        xr1 = x1
    else:
        xr0 = x[0] if x[0] >= x0 else x0
        xr1 = x[1] if x[1] <= x1 else x1
        pass
    
    if y is None:
        yr0 = y0
        yr1 = y1
    else:
        yr0 = y[0] if y[0] >= y0 else y0
        yr1 = y[1] if y[1] <= y1 else y1
        pass
    
    if z is None:
        zr0 = z0
        zr1 = z1
    else:
        zr0 = z[0] if z[0] >= z0 else z0
        zr1 = z[1] if z[1] <= z1 else z1
        pass
    
    newd = hdu.data[zr0:zr1, yr0:yr1, xr0:xr1]
    newh = hdu.header.copy()
    newh['NAXIS1'] = xr1 - xr0
    newh['NAXIS2'] = yr1 - yr0
    newh['NAXIS3'] = zr1 - zr0
    newh['CRPIX1'] = hdu.header['CRPIX1'] - xr0
    newh['CRPIX2'] = hdu.header['CRPIX2'] - yr0
    newh['CRPIX3'] = hdu.header['CRPIX3'] - zr0
    newhdu = astropy.io.fits.PrimaryHDU(newd, newh)
    return newhdu
