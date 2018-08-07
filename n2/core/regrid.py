
import n2.log
logger = n2.log.get_logger(__name__)

import astropy.io.fits
import astropy.wcs
import astropy.units

import reproject


def read_n2hist(header):
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


def regrid(hdu, output_header, order='bilinear'):
    outh = output_header['N2HASH']
    logger.info('(regrid) output_header={outh}, order={order}'.format(**locals()))
    logger.info('(regrid) start calculation'.format(**locals()))
    regrided, footprint = reproject.reproject_interp(hdu, output_header, order=order)
    logger.info('(regrid) done'.format(**locals()))
    
    new_hdu = astropy.io.fits.PrimaryHDU(regrided, output_header)
    
    hist1 = hdu.header['HISTORY']
    hist2 = new_hdu.header['HISTORY']

    hist1n2 = '\n'.join([_ for _ in str(hist1).split('\n')
                         if _.startswith('n2:')])
    hist2other = '\n'.join([_ for _ in str(hist1).split('\n')
                            if not _.startswith('n2:')])
    new_hist = hist2other + '\n' + hist1n2
    try:
        new_hdu.header.pop('HISTORY')
    except KeyError:
        pass
    [new_hdu.header.add_history(_) for _ in new_hist.split('\n')]
    
    if 'BUNIT' in hdu.header: new_hdu.header['BUNIT'] = hdu.header['BUNIT']
    if 'BSCALE' in hdu.header: new_hdu.header['BSCALE'] = hdu.header['BSCALE']
    if 'BZERO' in hdu.header: new_hdu.header['BZERO'] = hdu.header['BZERO']
    if 'BMAJ' in hdu.header: new_hdu.header['BMAJ'] = hdu.header['BMAJ']
    if 'BMIN' in hdu.header: new_hdu.header['BMIN'] = hdu.header['BMIN']
    if 'BTYPE' in hdu.header: new_hdu.header['BTYPE'] = hdu.header['BTYPE']
    if 'BUNIT' in hdu.header: new_hdu.header['BUNIT'] = hdu.header['BUNIT']
    if 'OBJECT' in hdu.header: new_hdu.header['OBJECT'] = hdu.header['OBJECT']
    if 'MAPID' in hdu.header: new_hdu.header['MAPID'] = hdu.header['MAPID']
    if 'MAPVER' in hdu.header: new_hdu.header['MAPVER'] = hdu.header['MAPVER']
    if 'RESTFRQ' in hdu.header: new_hdu.header['RESTFRQ'] = hdu.header['RESTFRQ']
    if 'SPECSYS' in hdu.header: new_hdu.header['SPECSYS'] = hdu.header['SPECSYS']
    if 'LINE' in hdu.header: new_hdu.header['LINE'] = hdu.header['LINE']
    if 'TELESCOP' in hdu.header: new_hdu.header['TELESCOP'] = hdu.header['TELESCOP']
    if 'INSTRUME' in hdu.header: new_hdu.header['INSTRUME'] = hdu.header['INSTRUME']
    return new_hdu

__all__ = [
    'regrid',
]
