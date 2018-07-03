
import n2.log
logger = n2.log.get_logger(__name__)

import numpy
import astropy.wcs
import astropy.units
import astropy.io.fits



def remove_velocity_axis(hdu):
    newh = astropy.wcs.WCS(hdu.header, naxis=2).to_header()
    for k, v in hdu.header.items():
        if k[:5] in ['NAXIS', 'CTYPE', 'CRVAL', 'CRPIX', 'CDELT', 'CROTA', 'CUNIT']:
            continue
        newh[k] = v
        continue
    return newh

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
    mom0 = numpy.nansum(hdu.data, axis=0).astype(numpy.float32) * bunit
    mom0 *= cdelt3
    logger.info('(mom0) done')
    
    try:
        mom0 = (mom0).to('K km / s').value
        new_bunit = astropy.units.Unit('K km / s')
    except:
        mom0 = (mom0).to(new_bunit).value
        pass

    logger.debug('(mom0) new bunit : {new_bunit}'.format(**locals()))
    new_header = remove_velocity_axis(hdu)
    new_header['BUNIT'] = new_bunit.to_string()
    
    new_hdu = astropy.io.fits.PrimaryHDU(mom0, new_header)
    return new_hdu



__all__ = [
    'peak',
    'mom0',
]
