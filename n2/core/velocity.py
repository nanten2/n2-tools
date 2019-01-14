
import n2.log
logger = n2.log.get_logger(__name__)
import n2.core.smoothing

import numpy
import scipy.ndimage

import astropy.wcs
import astropy.units
import astropy.io.fits
import astropy.modeling



def remove_velocity_axis(hdu):
    newh = astropy.wcs.WCS(hdu.header, naxis=2).to_header()
    for k, v in hdu.header.items():
        if k[:5] in ['NAXIS', 'WCSAX', 'CTYPE', 'CRVAL', 'CRPIX', 'CDELT', 'CROTA', 'CUNIT']:
            continue
        newh[k] = v
        continue
    return newh

def single_ch(hdu, ch):
    logger.info('(single_ch) start calculation')
    single_ch = hdu.data[ch].astype(numpy.float32)
    logger.info('(single_ch) done')
    new_header = remove_velocity_axis(hdu)
    new_hdu = astropy.io.fits.PrimaryHDU(single_ch, new_header)
    return new_hdu

def peak(hdu):
    logger.info('(peak) start calculation')
    peak = numpy.nanmax(hdu.data, axis=0).astype(numpy.float32)
    logger.info('(peak) done')
    new_header = remove_velocity_axis(hdu)
    new_hdu = astropy.io.fits.PrimaryHDU(peak, new_header)
    return new_hdu

def mom0(hdu):
    bunit_str = hdu.header.get('BUNIT', '')
    bunit = astropy.units.Unit(bunit_str)
    cunit3_str = hdu.header.get('CUNIT3', '')
    cunit3 = astropy.units.Unit(cunit3_str)
    cdelt3 = hdu.header.get('CDELT3') * cunit3
    new_bunit = bunit * cunit3
    
    if bunit != '':
        logger.debug('(mom0) original bunit : {bunit}'.format(**locals()))        
    else:
        logger.warning('(mom0) BUNIT is not set in header')
        pass

    if cunit3 != '':
        logger.debug('(mom0) original cunit3 : {cunit3}'.format(**locals()))
    else:
        logger.warning('(mom0) CUNIT3 is not set in header')
        pass

    logger.info('(mom0) start calculation')
    nanmask = numpy.logical_not(numpy.isnan(hdu.data)).sum(axis=0) == 0
    
    mom0 = numpy.nansum(hdu.data, axis=0).astype(numpy.float32) * bunit
    mom0 *= abs(cdelt3)
    mom0[nanmask] = numpy.nan
    logger.info('(mom0) done')
    
    try:
        mom0 = (mom0).to(bunit_str + ' km / s').value
        new_bunit = astropy.units.Unit(bunit_str + ' km / s')
    except:
        mom0 = (mom0).to(new_bunit).value
        pass

    logger.debug('(mom0) new bunit : {new_bunit}'.format(**locals()))
    new_header = remove_velocity_axis(hdu)
    new_header['BUNIT'] = new_bunit.to_string()
    
    new_hdu = astropy.io.fits.PrimaryHDU(mom0, new_header)
    return new_hdu


def mom1(hdu):
    bunit_str = hdu.header.get('BUNIT', '')
    bunit = astropy.units.Unit(bunit_str)
    cunit3_str = hdu.header.get('CUNIT3', '')
    cunit3 = astropy.units.Unit(cunit3_str)
    cdelt3 = hdu.header.get('CDELT3') * cunit3
    new_bunit = cunit3
    
    if bunit != '':
        logger.debug('(mom1) original bunit : {bunit}'.format(**locals()))        
    else:
        logger.warning('(mom1) BUNIT is not set in header')
        pass

    if cunit3 != '':
        logger.debug('(mom1) original cunit3 : {cunit3}'.format(**locals()))
    else:
        logger.warning('(mom1) CUNIT3 is not set in header')
        pass

    logger.info('(mom1) start calculation')
    nanmask = numpy.logical_not(numpy.isnan(hdu.data)).sum(axis=0) == 0
    d = hdu.data * bunit
    indv = numpy.arange(hdu.header.get('NAXIS3'))
    v = pix2world(indv, hdu.header, 3)
    
    mom0 = numpy.nansum(d, axis=0).astype(numpy.float32)
    vi = d * v[:,None,None]
    mom1 = numpy.nansum(vi, axis=0) / mom0
    mom1[nanmask] = numpy.nan
    logger.info('(mom1) done')
    
    try:
        mom1 = (mom1).to('km / s').value
        new_bunit = astropy.units.Unit('km / s')
    except:
        mom1 = (mom1).to(new_bunit).value
        pass

    logger.debug('(mom1) new bunit : {new_bunit}'.format(**locals()))
    new_header = remove_velocity_axis(hdu)
    new_header['BUNIT'] = new_bunit.to_string()
    
    new_hdu = astropy.io.fits.PrimaryHDU(mom1, new_header)
    return new_hdu


def mom2(hdu):
    bunit_str = hdu.header.get('BUNIT', '')
    bunit = astropy.units.Unit(bunit_str)
    cunit3_str = hdu.header.get('CUNIT3', '')
    cunit3 = astropy.units.Unit(cunit3_str)
    cdelt3 = hdu.header.get('CDELT3') * cunit3
    new_bunit = cunit3
    
    if bunit != '':
        logger.debug('(mom2) original bunit : {bunit}'.format(**locals()))        
    else:
        logger.warning('(mom2) BUNIT is not set in header')
        pass

    if cunit3 != '':
        logger.debug('(mom2) original cunit3 : {cunit3}'.format(**locals()))
    else:
        logger.warning('(mom2) CUNIT3 is not set in header')
        pass

    logger.info('(mom2) start calculation')
    nanmask = numpy.logical_not(numpy.isnan(hdu.data)).sum(axis=0) == 0
    d = hdu.data * bunit
    indv = numpy.arange(hdu.header.get('NAXIS3'))
    v = pix2world(indv, hdu.header, 3)
    
    mom0 = numpy.nansum(d, axis=0).astype(numpy.float32)
    vi = d * v[:,None,None]
    mom1 = numpy.nansum(vi, axis=0) / mom0
    vvi = d * (v[:,None,None] - mom1[None,:,:,])**2
    mom2 = (numpy.nansum(vvi, axis=0) / mom0)**0.5
    mom2[nanmask] = numpy.nan
    logger.info('(mom2) done')
    
    try:
        mom2 = (mom2).to('km / s').value
        new_bunit = astropy.units.Unit('km / s')
    except:
        mom2 = (mom2).to(new_bunit).value
        pass

    logger.debug('(mom2) new bunit : {new_bunit}'.format(**locals()))
    new_header = remove_velocity_axis(hdu)
    new_header['BUNIT'] = new_bunit.to_string()
    
    new_hdu = astropy.io.fits.PrimaryHDU(mom2, new_header)
    return new_hdu


def moment_mask(hdu, smooth_xy=0, smooth_v=0, nsig=5, minsize=5):
    logger.info('(moment_mask) smooth_xy={smooth_xy}, smooth_v={smooth_v}, nsig={nsig}, minsize={minsize}'.format(**locals()))
    logger.info('(moment_mask) start calculation')
    hdu2 = hdu.copy()
    
    nanmask = numpy.isnan(hdu2.data)
    hdu2.data[nanmask] = 0    
    
    if smooth_xy > 0:
        hdu2 = n2.core.smoothing.convolve_pix(hdu2, smooth_xy)
        pass
    
    if smooth_v > 0:
        hdu2 = n2.core.smoothing.velocity_binning_pix(hdu2, smooth_v)
        pass
    
    rms = calc_rms(hdu2.data)
    logger.debug('(moment_mask) smoothed rms = {rms:.2f}'.format(**locals()))
    mommask = hdu2.data > rms * nsig
    
    data_labels, data_nums = scipy.ndimage.label(mommask)
    data_areas = scipy.ndimage.sum(mommask, data_labels, numpy.arange(data_nums+1))
    
    small_size_mask = data_areas < minsize
    small_mask = small_size_mask[data_labels.ravel()].reshape(data_labels.shape)
    num_masked_pixels = numpy.sum(small_mask)
    logger.debug('(moment_mask) num of masked pixels = {num_masked_pixels:d}'.format(**locals()))

    hdu3 = hdu.copy()
    hdu3.data[nanmask] = numpy.nan
    hdu3.data[small_mask] = numpy.nan
    logger.info('(moment_mask) done')
    return hdu3


def pv(hdu, sumaxis=1):
    logger.info('(pv) sumaxis={sumaxis}'.format(**locals()))
    
    bunit_str = hdu.header.get('BUNIT', '')
    bunit = astropy.units.Unit(bunit_str)
    cunit_str = hdu.header.get('CUNIT{sumaxis}'.format(**locals()), '')
    cunit = astropy.units.Unit(cunit_str)
    cdelt = hdu.header.get('CDELT{sumaxis}'.format(**locals())) * cunit
    new_bunit = bunit * cunit
    
    if bunit != '':
        logger.debug('(pv) original bunit : {bunit}'.format(**locals()))        
    else:
        logger.warning('(pv) BUNIT is not set in header')
        pass

    if cunit != '':
        logger.debug('(pv) original cunit{sumaxis} : {cunit}'.format(**locals()))
    else:
        logger.warning('(pv) CUNIT{sumaxis} is not set in header'.format(**locals()))
        pass

    logger.info('(pv) start calculation')
    nanmask = numpy.logical_not(numpy.isnan(hdu.data)).sum(axis=3-sumaxis) == 0
    
    pv = numpy.nansum(hdu.data, axis=3-sumaxis).astype(numpy.float32) * bunit
    pv *= cdelt
    pv[nanmask] = numpy.nan
    pvshape = list(pv.shape)
    pvshape.insert(3-sumaxis, 1)
    pv = pv.reshape(pvshape)
    logger.info('(pv) done')
    
    logger.debug('(pv) new bunit : {new_bunit}'.format(**locals()))
    new_header = hdu.header.copy()
    new_header['BUNIT'] = new_bunit.to_string()
    
    new_hdu = astropy.io.fits.PrimaryHDU(pv, new_header)
    return new_hdu


def pix2world(pix, header, axis):
    wcs = astropy.wcs.WCS(header)
    cunit = astropy.units.Unit(header.get('CUNIT%d'%(axis)))
    
    pix = numpy.array(pix)
    if pix.ndim == 0:
        plen = 1
    else:
        plen = len(pix)
        pass
    
    p = numpy.zeros([plen, wcs.naxis])
    p[:,axis-1] = pix
    world = wcs.all_pix2world(p, 0)[:,axis-1] * cunit
    
    if pix.ndim == 0:
        return world[0]

    return world


def calc_rms(data):
    g = astropy.modeling.models.Gaussian1D(mean=0)
    g.fixed['mean'] = True
    f = astropy.modeling.fitting.LevMarLSQFitter()
    
    d = data.copy().ravel()
    dmin = numpy.nanmin(d)
    h1 = numpy.histogram(d, bins=10, range=(dmin, 0))    
    x1 = (h1[1][:-1] + h1[1][1:])/2
    t1 = f(g, x1, h1[0])
    
    h2 = numpy.histogram(d, bins=10, range=(t1.stddev*-3, t1.stddev*-1))    
    x2 = (h2[1][:-1] + h2[1][1:])/2
    t2 = f(g, x2, h2[0])
    
    return t2.stddev.value


__all__ = [
    'single_ch',
    'peak',
    'mom0',
    'mom1',
    'mom2',
    'moment_mask',
    'pv',
]
