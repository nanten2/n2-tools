
import n2.log
logger = n2.log.get_logger(__name__)

import numpy
import matplotlib.path
import astropy.wcs



def apply_mask(hdu, mask):
    mask_str = mask.header['N2HASH']
    logger.info('(apply_mask) mask={mask_str}'.format(**locals()))
    logger.info('(apply_mask) start calculation')
    new_d = hdu.data.copy()
    new_d[mask.data==0] = numpy.nan
    logger.info('(apply_mask) done')
    
    new_header = hdu.header.copy()
    new_hdu = astropy.io.fits.PrimaryHDU(new_d, new_header)
    return new_hdu


def mask_inpolygon(hdu, polygon, axis=('x', 'y')):
    logger.info('(mask_inpolygon) polygon={polygon}, axis={axis}'.format(**locals()))
    logger.info('(mask_inpolygon) start calculation')
    wcs = astropy.wcs.WCS(hdu.header)
    polygon_p = wcs.all_world2pix(polygon, 0)
    path = matplotlib.path.Path(polygon_p)
    ax1 = numpy.arange(hdu.data.shape[1])
    ax2 = numpy.arange(hdu.data.shape[0])
    ax12 = numpy.array([_.ravel() for _ in numpy.meshgrid(ax1, ax2)]).T
    mask = path.contains_points(ax12).reshape(hdu.data.shape).astype(int)
    logger.info('(mask_inpolygon) done')
    
    new_header = hdu.header.copy()
    new_hdu = astropy.io.fits.PrimaryHDU(mask, new_header)
    return new_hdu



__all__ = [
    'apply_mask',
    'mask_inpolygon',
]
