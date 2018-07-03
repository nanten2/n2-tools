
import n2.log
logger = n2.log.get_logger(__name__)

import numpy
import astropy.units
import astropy.convolution


SIG2FWHM = 2 * numpy.sqrt(2*numpy.log(2))


def convolve_pix(hdu, stddev):
    logger.info('(convolve_pix) stddev={stddev}'.format(**locals()))    
    
    bmaj = hdu.header.get('BMAJ', 0) * astropy.units.deg
    bmin = hdu.header.get('BMIN', 0) * astropy.units.deg    
    logger.debug('(convolve_pix) original BMAJ : {bmaj}'.format(**locals()))    
    logger.debug('(convolve_pix) original BMIN : {bmin}'.format(**locals()))    
    
    logger.info('(convolve_pix) start calculation'.format(**locals()))
    
    if hdu.data.ndim == 2:
        new_hdu = convolve_pix2d(hdu, stddev)
    
    elif hdu.data.ndim == 3:
        new_hdu = convolve_pix3d(hdu, stddev)
        pass
    
    logger.info('(convolve_pix) done'.format(**locals()))
    
    cunit = astropy.units.Unit(hdu.header['CUNIT1'])
    cdelt = hdu.header['CDELT1'] * cunit
    
    kernel_hpbw = stddev * SIG2FWHM * cdelt
    new_bmaj = (bmaj**2 + kernel_hpbw**2)**0.5
    new_bmin = (bmin**2 + kernel_hpbw**2)**0.5
    
    new_hdu.header['BMAJ'] = new_bmaj.to('deg').value
    new_hdu.header['BMIN'] = new_bmin.to('deg').value
    logger.debug('(convolve_pix) new BMAJ : {new_bmaj}'.format(**locals()))    
    logger.debug('(convolve_pix) new BMIN : {new_bmin}'.format(**locals()))    
    return new_hdu


def convolve_pix2d(hdu, stddev):
    kernel = astropy.convolution.Gaussian2DKernel(stddev)
    dconv = astropy.convolution.convolve(hdu.data, kernel,
                                         normalize_kernel=True)
    new_hdu = hdu.copy()
    new_hdu.data = dconv
    return new_hdu


def convolve_pix3d(hdu, stddev):
    kernel2d = astropy.convolution.Gaussian2DKernel(stddev)
    y, x = kernel2d.array.shape
    kernel3d = kernel2d.array.reshape((1, y, x))
    dconv = astropy.convolution.convolve(hdu.data, kernel3d,
                                         normalize_kernel=True)
    new_hdu = hdu.copy()
    new_hdu.data = dconv
    return new_hdu


def convolve_world(hdu, target_hpbw):
    logger.info('(convolve_world) target_hpbw={target_hpbw}'.format(**locals()))
    
    if hdu.header.get('BMAJ', '') == '':
        logger.error("(convolve_world) header must have 'BMAJ' record, but not")
        logger.error('(convolve_world) execution is terminated')
        return None
    
    cunit = astropy.units.Unit(hdu.header['CUNIT1'])
    cdelt = hdu.header['CDELT1'] * cunit
    hpbw = hdu.header.get('BMAJ', 0) * astropy.units.deg
    kernel_hpbw = (target_hpbw**2 - hpbw**2)**0.5
    kernel_stddev = kernel_hpbw / SIG2FWHM
    kernel_stddev_pix = abs((kernel_stddev / cdelt).to('').value)
    return convolve_pix(hdu, kernel_stddev_pix)



def velocity_binning_pix(hdu, nbin):
    nbin = int(nbin)
    logger.info('(velocity_binning_pix) width={nbin}'.format(**locals()))
    logger.info('(velocity_binning_pix) start calculation'.format(**locals()))
    kernel1d = astropy.convolution.Box1DKernel(nbin)
    z = len(kernel1d.array)
    kernel3d = kernel1d.array.reshape((z, 1, 1))
    dconv = astropy.convolution.convolve(hdu.data, kernel3d,
                                         normalize_kernel=True)
    
    logger.info('(velocity_binning_pix) done'.format(**locals()))
    
    new_hdu = hdu.copy()
    new_hdu.data = dconv
    return new_hdu

def velocity_binning_world(hdu, width):
    logger.info('(velocity_binning_world) width={width}'.format(**locals()))
    cunit = astropy.units.Unit(hdu.header['CUNIT3'])
    cdelt = hdu.header['CDELT3'] * cunit
    nbin = int(abs((width / cdelt).to('').value))
    return velocity_binning_pix(hdu, nbin)




__all__ = [
    'convolve_pix',
    'convolve_world',
    'velocity_binning_pix',
    'velocity_binning_world',
]
