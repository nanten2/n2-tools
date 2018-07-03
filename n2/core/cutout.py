
import n2.log
logger = n2.log.get_logger(__name__)

import astropy.io.fits
import astropy.wcs
import astropy.units



def cut_pix(hdu, x=None, y=None, z=None):
    logger.info('(cut_pix) x={x}, y={y}, z={z}'.format(**locals()))
    logger.debug('(cut_pix) original shape : {hdu.data.shape}'.format(**locals()))
    logger.info('(cut_pix) start calculation')
    
    newhdu = hdu.copy()
    
    if (x is not None) or (y is not None):
        newhdu = cut_pix_xy(newhdu, x, y)
        pass
        
    if z is not None:
        newhdu = cut_pix_z(newhdu, z)
        pass
    
    logger.info('(cut_pix) done'.format(**locals()))
    logger.debug('(cut_pix) result shape : {newhdu.data.shape}'.format(**locals()))
    return newhdu

def cut_pix_xy(hdu, x=None, y=None):
    ndim = hdu.header['NAXIS']
    x0 = 0
    y0 = 0
    x1 = hdu.header['NAXIS1']
    y1 = hdu.header['NAXIS2']
    
    if x is None:
        xr0 = x0
        xr1 = x1
    else:
        xr0 = int(x[0]) if x[0] >= x0 else x0
        xr1 = int(x[1]) if x[1] <= x1 else x1
        pass
    
    if y is None:
        yr0 = y0
        yr1 = y1
    else:
        yr0 = int(y[0]) if y[0] >= y0 else y0
        yr1 = int(y[1]) if y[1] <= y1 else y1
        pass
    
    if ndim == 2:
        newd = hdu.data[yr0:yr1, xr0:xr1]
    elif ndim == 3:
        newd = hdu.data[:, yr0:yr1, xr0:xr1]
        pass
    
    newh = hdu.header.copy()
    newh['NAXIS1'] = xr1 - xr0
    newh['NAXIS2'] = yr1 - yr0
    newh['CRPIX1'] = hdu.header['CRPIX1'] - xr0
    newh['CRPIX2'] = hdu.header['CRPIX2'] - yr0
    newhdu = astropy.io.fits.PrimaryHDU(newd, newh)
    return newhdu    
    
def cut_pix_z(hdu, z=None):
    z0 = 0
    z1 = hdu.header['NAXIS3']
    
    if z is None:
        zr0 = z0
        zr1 = z1
    else:
        zr0 = int(z[0]) if z[0] >= z0 else z0
        zr1 = int(z[1]) if z[1] <= z1 else z1
        pass
    
    newd = hdu.data[zr0:zr1, :, :]
    newh = hdu.header.copy()
    newh['NAXIS3'] = zr1 - zr0
    newh['CRPIX3'] = hdu.header['CRPIX3'] - zr0
    newhdu = astropy.io.fits.PrimaryHDU(newd, newh)
    return newhdu


def cut_world(hdu, x=None, y=None, z=None):
    logger.info('(cut_world) x={x}, y={y}, z={z}'.format(**locals()))
    logger.debug('(cut_world) original shape : {hdu.data.shape}'.format(**locals()))
    logger.info('(cut_world) start calculation')
    
    newhdu = hdu.copy()
    
    if (x is not None) or (y is not None):
        newhdu = cut_world_xy(newhdu, x, y)
        pass
        
    if z is not None:
        newhdu = cut_world_z(newhdu, z)
        pass
    
    logger.info('(cut_world) done'.format(**locals()))
    logger.debug('(cut_world) result shape : {newhdu.data.shape}'.format(**locals()))
    return newhdu

def cut_world_xy(hdu, x=None, y=None):
    w = astropy.wcs.WCS(hdu.header, naxis=2)
    
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
    
    x_ = [int(p0[0]), int(p1[0])]
    y_ = [int(p0[1]), int(p1[1])]
    
    logger.debug('(cut_world_xy) pix range : x={x_}, y={y_}'.format(**locals()))
    return cut_pix_xy(hdu, x_, y_)

def cut_world_z(hdu, z=None):
    w = astropy.wcs.WCS(hdu.header)
    
    p_start = [0, 0, 0]
    p_end = [0, 0, hdu.header['NAXIS3'] - 1]
    
    w_start = w.all_pix2world([p_start], 0)[0]
    w_end = w.all_pix2world([p_end], 0)[0]
    
    unitz = hdu.header['CUNIT3']
    
    if z is None:
        w_z0 = w_start[2]
        w_z1 = w_end[2]
    else:
        w_z0 = z[0].to(unitz).value if isinstance(z[0], astropy.units.Quantity) else z[0]
        w_z1 = z[1].to(unitz).value if isinstance(z[1], astropy.units.Quantity) else z[1]
        pass
    
    w0 = [0, 0, w_z0]
    w1 = [0, 0, w_z1]
    
    p0 = w.all_world2pix([w0], 0)[0]
    p1 = w.all_world2pix([w1], 0)[0]
    
    z_ = [int(p0[2]), int(p1[2])]
    
    logger.debug('(cut_world_z) pix range : z={z_}'.format(**locals()))
    return cut_pix_z(hdu, z_)


__all__ = [
    'cut_pix',
    'cut_world',
]
