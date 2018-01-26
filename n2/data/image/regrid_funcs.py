
import numpy
import astropy.io.fits
import astropy.wcs
import astropy.units


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


def cut_world(hdu, x=None, y=None, z=None):
    if hdu.header['NAXIS'] == 2:
        return cut_world_2d(hdu, x, y)
        
    elif hdu.header['NAXIS'] == 3:
        return cut_world_3d(hdu, x, y, z)
    
    return


def cut_world_2d(hdu, x=None, y=None):
    w = astropy.wcs.WCS(hdu.header)
    
    p_bottom_left = [0, 0]
    p_top_right = [hdu.header['NAXIS1'] - 1,
                   hdu.header['NAXIS2'] - 1]
    
    w_bottom_left = w.all_pix2world([p_bottom_left], 0)[0]
    w_top_right = w.all_pix2world([p_top_right], 0)[0]
    
    unitx = hdu.header.get('CUNIT1', astropy.units.deg)
    unity = hdu.header.get('CUNIT2', astropy.units.deg)
    
    if x is None:
        w_x0 = w_bottom_left[0]
        w_x1 = w_top_right[0]
    else:
        w_x0 = x[0].to(unitx).value if isinstance(x[0], astropy.units.Quantity) else x[0]
        w_x1 = x[1].to(unitx).value if isinstance(x[1], astropy.units.Quantity) else x[1]
        pass
    
    if y is None:
        w_y0 = w_bottom_left[1]
        w_y1 = w_top_right[1]
    else:
        w_y0 = y[0].to(unity).value if isinstance(y[0], astropy.units.Quantity) else y[0]
        w_y1 = y[1].to(unity).value if isinstance(y[1], astropy.units.Quantity) else y[1]
        pass

    w0 = [w_x0, w_y0]
    w1 = [w_x1, w_y1]
    
    p0 = w.all_world2pix([w0], 0)[0]
    p1 = w.all_world2pix([w1], 0)[0]
    
    x_ = [p0[0], p1[0]]
    y_ = [p0[1], p1[1]]
    
    return cut_pix_2d(hdu, x_, y_)


def cut_world_3d(hdu, x=None, y=None, z=None):
    w = astropy.wcs.WCS(hdu.header)
    
    p_bottom_left = [0, 0, 0]
    p_top_right = [hdu.header['NAXIS1'] - 1,
                   hdu.header['NAXIS2'] - 1, 
                   hdu.header['NAXIS3'] - 1]
    
    w_bottom_left = w.all_pix2world([p_bottom_left], 0)[0]
    w_top_right = w.all_pix2world([p_top_right], 0)[0]
    
    unitx = hdu.header['CUNIT1']
    unity = hdu.header['CUNIT2']
    unitz = hdu.header['CUNIT3']
    
    if x is None:
        w_x0 = w_bottom_left[0]
        w_x1 = w_top_right[0]
    else:
        w_x0 = x[0].to(unitx).value if isinstance(x[0], astropy.units.Quantity) else x[0]
        w_x1 = x[1].to(unitx).value if isinstance(x[1], astropy.units.Quantity) else x[1]
        pass
    
    if y is None:
        w_y0 = w_bottom_left[1]
        w_y1 = w_top_right[1]
    else:
        w_y0 = y[0].to(unity).value if isinstance(y[0], astropy.units.Quantity) else y[0]
        w_y1 = y[1].to(unity).value if isinstance(y[1], astropy.units.Quantity) else y[1]
        pass

    if z is None:
        w_z0 = w_bottom_left[2]
        w_z1 = w_top_right[2]
    else:
        w_z0 = z[0].to(unitz).value if isinstance(z[0], astropy.units.Quantity) else z[0]
        w_z1 = z[1].to(unitz).value if isinstance(z[1], astropy.units.Quantity) else z[1]
        pass
    
    w0 = [w_x0, w_y0, w_z0]
    w1 = [w_x1, w_y1, w_z1]
    
    p0 = w.all_world2pix([w0], 0)
    p1 = w.all_world2pix([w1], 0)
    
    x_ = [p0[0], p1[0]]
    y_ = [p0[1], p1[1]]
    z_ = [p0[2], p1[2]]
    
    return cut_pix_3d(hdu, x_, y_, z_)


def decimate(hdu, xy=None, z=None):
    newhdu = hdu
    
    if xy is not None:
        newhdu = decimate_xy(newhdu, xy)
        pass
        
    if z is not None:
        newhdu = decimate_z(newhdu, z)
        pass
        
    return newhdu

def decimate_xy(hdu, fraction):
    ndim = hdu.header['NAXIS']
    step = int(1/fraction)
    
    newh = hdu.header.copy()
    newh['NAXIS1'] = numpy.ceil(hdu.header['NAXIS1'] / step)
    newh['NAXIS2'] = numpy.ceil(hdu.header['NAXIS2'] / step)
    newh['CRPIX1'] = ((hdu.header['CRPIX1'] - 1) / step) + 1
    newh['CRPIX2'] = ((hdu.header['CRPIX2'] - 1) / step) + 1
    newh['CDELT1'] = hdu.header['CDELT1'] * step
    newh['CDELT2'] = hdu.header['CDELT2'] * step
    
    if ndim == 2:
        newd = hdu.data[::step, ::step]
        
    elif ndim == 3:
        newd = hdu.data[:, ::step, ::step]
        pass
    
    newhdu = astropy.io.fits.PrimaryHDU(newd, newh)
    return newhdu

def decimate_z(hdu, fraction):
    ndim = hdu.header['NAXIS']
    step = int(1/fraction)
    
    newh = hdu.header.copy()
    
    if ndim == 2:
        newd = hdu.data
        
    elif ndim == 3:
        newd = hdu.data[::step, :, :]
        newh['NAXIS3'] = numpy.ceil(hdu.header['NAXIS3'] / step)
        newh['CRPIX3'] = ((hdu.header['CRPIX3'] - 1) / step) + 1
        newh['CDELT3'] = hdu.header['CDELT3'] * step
        pass
    
    newhdu = astropy.io.fits.PrimaryHDU(newd, newh)
    return newhdu


    
__all__ = ['cut_pix', 'cut_world', 'decimate']


