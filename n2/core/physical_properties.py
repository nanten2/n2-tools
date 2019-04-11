
import n2.log
logger = n2.log.get_logger(__name__)

import numpy
import astroquery.lamda
import astropy.units
import astropy.io.fits

from numpy import pi
from numpy import exp
from numpy import expm1
from numpy import log as ln
from astropy.constants import k_B
from astropy.constants import h
from astropy.constants import c
from astropy.units import K
from astropy.units import GHz
from astropy.units import s


def parse_line(line):
    if line.startswith('12CO'):
        trans = line.split('12CO')[-1]
        trans_up = int(trans.split('-')[0])
        trans_low = int(trans.split('-')[-1])
        return {'molecule': 'co',
                'transition': trans,
                'up': trans_up, 'low': trans_low}

    if line.startswith('13CO'):
        trans = line.split('13CO')[-1]
        trans_up = int(trans.split('-')[0])
        trans_low = int(trans.split('-')[-1])
        return {'molecule': '13co',
                'transition': trans,
                'up': trans_up, 'low': trans_low}

    if line.startswith('C18O'):
        trans = line.split('C18O')[-1]
        trans_up = int(trans.split('-')[0])
        trans_low = int(trans.split('-')[-1])
        return {'molecule': 'c18o',
                'transition': trans,
                'up': trans_up, 'low': trans_low}

    if line.startswith('C17O'):
        trans = line.split('C17O')[-1]
        trans_up = int(trans.split('-')[0])
        trans_low = int(trans.split('-')[-1])
        return {'molecule': 'c17o',
                'transition': trans,
                'up': trans_up, 'low': trans_low}

    return {'molecule': '',
            'transition': '',
            'up': None, 'low': None}
    

def get_bunit(hdu):
    return astropy.units.Unit(hdu.header.get('BUNIT', ''))

def get_Tbg(Tbg):
    if Tbg is None: return 2.725*K
    return Tbg

def get_quantity(q, default_unit=''):
    if isinstance(q, astropy.units.Quantity):
        return q, str(q)
    
    elif isinstance(q, astropy.io.fits.PrimaryHDU):
        bunit = get_bunit(q)
        return get_quantity(q.data, bunit)[0], q.header['N2HASH']

    elif isinstance(q, n2.data.fitsimage.fitsimage):
        return get_quantity(q.data, q.bunit)[0], q.header['N2HASH']
    
    else:
        ret = q * astropy.units.Unit(default_unit)
        return ret, str(ret)

def get_freq(hdu, freq):
    if freq is not None: return freq
    line = parse_line(hdu.header['LINE'])
    col, trans, elev = astroquery.lamda.Lamda.query(mol=line['molecule'])
    return trans[trans['Upper']==line['up']+1]['Frequency'][0] * GHz
    
def get_EinsteinA(hdu, A):
    if A is not None: return A
    line = parse_line(hdu.header['LINE'])
    col, trans, elev = astroquery.lamda.Lamda.query(mol=line['molecule'])
    return trans[trans['Upper']==line['up']+1]['EinsteinA'][0] / s

def get_level(hdu, level):
    if level is not None: return level
    return int(hdu.header['LEVEL'])
    
def get_B(hdu, B):
    if B is not None: return B
    line = parse_line(hdu.header['LINE'])
    col, trans, elev = astroquery.lamda.Lamda.query(mol=line['molecule'])
    E0 = trans['E_u(K)'][0] * K
    J = 1
    return k_B * E0 / (h * J * (J+1))


def tex(hdu, tau, freq=None, Tbg=None):
    tau, tau_str = get_quantity(tau, '')    
    T = get_quantity(hdu.data, get_bunit(hdu))[0]
    freq = get_freq(hdu, freq)
    Tbg = get_Tbg(Tbg)
    
    logger.info('(tex) tau={tau_str}, freq={freq}, Tbg={Tbg}'.format(**locals()))
    logger.info('(tex) start calculation')

    hvk = h * freq / k_B
    A = T / hvk / (-1 * expm1(-tau))
    B = 1 / expm1(hvk / Tbg)
    tex = hvk * (ln(1 + (A + B)**-1))**-1
    
    logger.debug('(tex) hv/k : {0:.3e}'.format(hvk.to('Hz K s')))
    logger.debug('(tex) hv/k/expm1(hv/kTbg) : {0:.3e}'.format(B * hvk.to('Hz K s')))
    logger.info('(tex) done')
    
    new_header = hdu.header.copy()
    new_header['BUNIT'] = 'K'
    new_hdu = astropy.io.fits.PrimaryHDU(tex.to('K'), new_header)
    return new_hdu


def tau(hdu, Tex, freq=None, Tbg=None):
    tex, tex_str = get_quantity(Tex, 'K')
    T = get_quantity(hdu.data, get_bunit(hdu))[0]
    freq = get_freq(hdu, freq)
    Tbg = get_Tbg(Tbg)
    
    logger.info('(tau) Tex={tex_str}, freq={freq}, Tbg={Tbg}'.format(**locals()))
    logger.info('(tau) start calculation')
    
    hvk = h * freq / k_B
    A = 1 / expm1(hvk / tex) 
    B = 1 / expm1(hvk / Tbg)
    tau = -ln(1 - T/hvk * (A - B)**-1)
    
    logger.debug('(tau) hv/k : {0:.3e}'.format(hvk))
    logger.debug('(tau) 1/expm1(hv/kTbg) : {0:.3e}'.format(B))
    logger.info('(tau) done')
    
    new_header = hdu.header.copy()
    new_header['BUNIT'] = ''
    new_hdu = astropy.io.fits.PrimaryHDU(tau.to(''), new_header)
    return new_hdu


def column_density_upper(hdu, Tex, EinsteinA=None, freq=None):
    tex, tex_str = get_quantity(Tex, 'K')
    line = parse_line(hdu.header['LINE'])
    tau = get_quantity(hdu.data, get_bunit(hdu))[0]
    freq = get_freq(hdu, freq)
    EinsteinA = get_EinsteinA(hdu, EinsteinA)
    
    logger.info('(column_density_upper) Tex={tex_str}, EinsteinA={EinsteinA}, freq={freq}'.format(**locals()))
    logger.info('(column_density_upper) start calculation')
    
    N_up = 8 * pi * freq**3 / c**3 / EinsteinA / expm1(h*freq/k_B/tex) * tau
    
    logger.debug('(column_density_upper) 8 pi v3 / c3 / A : {0:.3e}'.format(8 * pi * (freq**3 / c**3 / EinsteinA).to('s m-3')))
    logger.info('(column_density_upper) done')
    
    new_header = hdu.header.copy()
    new_header['BUNIT'] = 'cm-2'
    new_header['MOLECULE'] = line['molecule']
    new_header['LEVEL'] = line['up']
    new_header['PROPERTY'] = 'Column density'
    new_hdu = astropy.io.fits.PrimaryHDU(N_up.to('cm-2'), new_header)
    return new_hdu


def column_density_total_LTE(hdu, Tk, level=None, B=None):
    tk, tk_str = get_quantity(Tk, 'K')
    level = get_level(hdu, level)
    B = get_B(hdu, B)
    Nj = get_quantity(hdu.data, get_bunit(hdu))[0]
    
    logger.info('(column_density_total_LTE) Tk={tk_str}, level={level}, B={B}'.format(**locals()))
    logger.info('(column_density_total_LTE) start calculation')
    
    Tcalc = tk[None,:,:]
    Jcalc = numpy.arange(100)[:,None,None]
    Ecalc = h * B * Jcalc * (Jcalc+1)
    
    Qcalc = (2 * Jcalc+1) * exp(-Ecalc / k_B / Tcalc)
    Q = numpy.nansum(Qcalc, axis=0)
    maxQ = numpy.nanmax(Q)
    maxkThB = numpy.nanmax(k_B*tk/h/B)    
    Ej = h * B * level * (level+1)
    Ntot = Nj * Q / ((2 * level+1) * exp(-Ej / k_B / tk))

    logger.info('(column_density_total_LTE) done')
    new_header = hdu.header.copy()
    new_header['BUNIT'] = 'cm-2'
    new_header['PROPERTY'] = 'Column density'
    new_header['METHOD'] = 'LTE, {0}'.format(hdu.header['LINE'])
    if 'LEVEL' in new_header: del(new_header['LEVEL'])
    new_hdu = astropy.io.fits.PrimaryHDU(Ntot.to('cm-2'), new_header)
    return new_hdu


def convert_N13CO_to_NH2(hdu, factor='Frerking1982'):
    X13_Frerking1982 = 7.1e5
    
    if str(factor).lower()=='frerking1982':
        X = X13_Frerking1982
        
    elif not isinstance(factor, str):
        X = factor

    else:
        X = X13_Frerking1982
        pass
    
    logger.info('(convert_N13CO_to_NH2) factor={factor}'.format(**locals()))
    logger.debug('(convert_N13CO_to_NH2) factor={X:.3e}'.format(**locals()))
    logger.info('(convert_N13CO_to_NH2) start calculation')    
    NH2 = hdu.data * X
    logger.info('(convert_N13CO_to_NH2) done')
    
    new_header = hdu.header.copy()
    new_header['BUNIT'] = 'cm-2'
    new_header['PROPERTY'] = 'Column density'
    new_header['MOLECULE'] = 'h2'
    new_hdu = astropy.io.fits.PrimaryHDU(NH2, new_header)
    return new_hdu

    
def convert_NC18O_to_NH2(hdu, factor='Frerking1982'):
    X18_Frerking1982 = 5.9e6
    
    if str(factor).lower()=='frerking1982':
        X = X18_Frerking1982
        
    elif not isinstance(factor, str):
        X = factor

    else:
        X = X18_Frerking1982
        pass
    
    logger.info('(convert_N18CO_to_NH2) factor={factor}'.format(**locals()))
    logger.debug('(convert_N18CO_to_NH2) factor={X:.3e}'.format(**locals()))
    logger.info('(convert_N18CO_to_NH2) start calculation')    
    NH2 = hdu.data * X
    logger.info('(convert_N18CO_to_NH2) done')
    
    new_header = hdu.header.copy()
    new_header['BUNIT'] = 'cm-2'
    new_header['PROPERTY'] = 'Column density'
    new_header['MOLECULE'] = 'h2'
    new_hdu = astropy.io.fits.PrimaryHDU(NH2, new_header)
    return new_hdu


def convert_to_NH2(hdu, factor='Okamoto2017'):
    X_Dame2001 = 1.8e20
    X_Okamoto2017 = 1e20
    
    if str(factor).lower()=='dame2001':
        X = X_Dame2001
        
    elif str(factor).lower()=='okamoto2017':
        X = X_Okamoto2017
        
    elif not isinstance(factor, str):
        X = factor

    else:
        X = X_Okamoto2017
        pass
    
    logger.info('(convert_to_NH2) factor={factor}'.format(**locals()))
    logger.debug('(convert_to_NH2) factor={X:.3e}'.format(**locals()))
    logger.info('(convert_to_NH2) start calculation')    
    NH2 = hdu.data * X
    logger.info('(convert_to_NH2) done')
    
    new_header = hdu.header.copy()
    new_header['BUNIT'] = 'cm-2'
    new_header['PROPERTY'] = 'Column density'
    new_header['MOLECULE'] = 'h2'
    new_hdu = astropy.io.fits.PrimaryHDU(NH2, new_header)
    return new_hdu





__all__ = [
    'tex',
    'tau',
    'column_density_upper',
    'column_density_total_LTE',
    'convert_N13CO_to_NH2',
    'convert_NC18O_to_NH2',
    'convert_to_NH2',
]
