
import n2.core

import ipywidgets

import io
import warnings
import numpy
import PIL.Image


class jpy_red_blue_cube(object):
    def __init__(self, cube, nanval='max'):
        self.data = rgbcube(cube, nanval)
        self.gui = rgbgui(self)
        pass
    
    def _ipython_display_(self):
        self.gui._ipython_display_()
        return
    
    def get_shape(self):
        return self.data.data_shape
    
    def get_minmax(self):
        return {
            'min': self.data.dmin,
            'max': self.data.dmax,
        }
    
    def set_data_scale_red(self, scale_min, scale_max, stretch):
        self.data.scale_data_red(scale_min, scale_max, stretch)
        return
    
    def set_data_scale_blue(self, scale_min, scale_max, stretch):
        self.data.scale_data_blue(scale_min, scale_max, stretch)
        return

    def velocity_binning_red(self, nbin):
        self.data.velocity_binning_red(nbin)
        return
    
    def velocity_binning_blue(self, nbin):
        self.data.velocity_binning_blue(nbin)
        return
    
    def get_red_ch(self, ch):
        return self.data.get_ch_red(ch)
    
    def get_blue_ch(self, ch):
        return self.data.get_ch_blue(ch)
    
    def get_image(self):
        return self.gui.generate_image()
    
    def save(self, path):
        img = self.get_image()
        img.save(path)
        return



class rgbcube(object):
    nanval = 'max'
    hdu = None
    data_r = None
    data_b = None
    data_scaled_r = None
    data_scaled_b = None
    data_shape = None
    dmin = None
    dmax = None
    scale_min_r = None
    scale_min_b = None
    scale_max_r = None
    scale_max_b = None
    stretch_r = None
    stretch_b = None
    
    def __init__(self, hdu, nanval='max'):
        warnings.filterwarnings('ignore')
        self.nanval = nanval
        self.set_data(hdu)
        warnings.filterwarnings('default')
        pass
    
    def set_data(self, hdu):
        if hdu is None: return
        self.hdu = hdu.copy()
        
        data_r = hdu.data.copy()
        data_b = hdu.data.copy()
        
        data_r = data_r[:,::-1,:]
        data_b = data_b[:,::-1,:]
        
        self.nanval_red(data_r)
        self.nanval_blue(data_b)
        
        self.data_shape = data_r.shape
        nx, ny, nx = data_r.shape
        
        self.dmin = numpy.nanmin(data_r)
        self.dmax = numpy.nanmax(data_r) 
        self.scale_data_red()
        self.scale_data_blue()
        return
    
    def get_ch_red(self, ch):
        return self.data_scaled_r[ch]
    
    def get_ch_blue(self, ch):
        return self.data_scaled_b[ch]
    
    def nanval_red(self, data, nanval=None):
        self.data_r = self._nanval(data, nanval)
    
    def nanval_blue(self, data, nanval=None):
        self.data_b = self._nanval(data, nanval)
    
    def _nanval(self, data, nanval=None):
        data = data.copy()
        if nanval is None: nanval = self.nanval
        
        if nanval == 'max':
            data[data!=data] = numpy.nanmax(data)
        elif nanval == 'min':
            data[data!=data] = numpy.nanmin(data)
        else:
            data[data!=data] = nanval
            pass

        return data
    
    def velocity_binning_red(self, nbin):
        new_hdu = n2.core.velocity_binning_pix(self.hdu, nbin)
        self.data_r = new_hdu.data[:,::-1,:]
        self.scale_data_red(self.scale_min_r, self.scale_max_r, self.stretch_r)
        return
    
    def velocity_binning_blue(self, nbin):
        new_hdu = n2.core.velocity_binning_pix(self.hdu, nbin)
        self.data_b = new_hdu.data[:,::-1,:]
        self.scale_data_red(self.scale_min_b, self.scale_max_b, self.stretch_b)
        return
    
    def scale_data_red(self, scale_min=None, scale_max=None, stretch='linear'):
        warnings.filterwarnings('ignore')
        self.data_scaled_r = self._scale(self.data_r, scale_min, scale_max, stretch)
        self.scale_min_r = scale_min
        self.scale_max_r = scale_max
        self.stretch_r = stretch
        warnings.filterwarnings('default')
        return
    
    def scale_data_blue(self, scale_min=None, scale_max=None, stretch='linear'):
        warnings.filterwarnings('ignore')
        self.data_scaled_b = self._scale(self.data_b, scale_min, scale_max, stretch)
        self.scale_min_b = scale_min
        self.scale_max_b = scale_max
        self.stretch_b = stretch
        warnings.filterwarnings('default')
        return
    
    def _scale(self, data, scale_min=None, scale_max=None, stretch='linear'):
        if stretch == 'linear':
            scale_func = self._scale_linear
        elif stretch == 'log':
            scale_func = self._scale_log
        elif stretch == 'sqrt':
            scale_func = self._scale_sqrt
        else:
            scale_func = self._scale_linear
            pass
        
        if scale_min is None:
            scale_min = numpy.nanmin(data)
            pass
        
        if scale_max is None:
            scale_max = numpy.nanmax(data)
            pass
            
        self.scale_stretch = stretch
        
        scaled = scale_func(data, scale_min, scale_max)
        scaled = numpy.uint8(scaled * 255)
        return scaled
    
    def _scale_linear(self, data, scale_min, scale_max):
        scaled = (data - scale_min) / (scale_max - scale_min)
        scaled[numpy.where(scaled<0)] = 0
        scaled[numpy.where(scaled>=1)] = 1
        return scaled
    
    def _scale_log(self, data, scale_min, scale_max):
        scaled = self._scale_linear(data, scale_min, scale_max)
        scaled = numpy.log10((scaled * 9) + 1)
        return scaled
    
    def _scale_sqrt(self, data, scale_min, scale_max):
        scaled = self._scale_linear(data, scale_min, scale_max)
        scaled = numpy.sqrt(scaled)
        return scaled



class rgbgui(object):
    def __init__(self, ctrl):
        self.ctrl = ctrl
        self.init_gui()
        self.init_slider()
        self.refresh_slider()
        self.refresh_image()
        pass
    
    def _ipython_display_(self):
        self.refresh_image()
        self.box_text._ipython_display_()
        self.box_r._ipython_display_()
        self.box_b._ipython_display_()
        self.chbox_r._ipython_display_()
        self.chbox_b._ipython_display_()
        self.img._ipython_display_()
        return
    
    def init_gui(self):
        stretches = ['linear', 'sqrt', 'log']
        
        slider_layout = {'min_width': '50%'}
        minmax_layout = {'width': '100px'}
        stretch_layout = {'width': '80px'}
        
        text_range = ipywidgets.Label(value='', layout={'min_width': '50%'})
        text_min = ipywidgets.Label(value='min.', layout=minmax_layout)
        text_max = ipywidgets.Label(value='max.', layout=minmax_layout)
        text_stretch = ipywidgets.Label(value='stretch', layout=stretch_layout)
        self.box_text = ipywidgets.HBox([text_range, text_min, text_max, text_stretch])
        
        self.slider_r = ipywidgets.FloatRangeSlider(description = '<b style="color:#cc3737">Red:</b>',
                                                    min = -9e99, max = 9e99, step = 1e98, value = (-9e99, 9e99),
                                                    layout = slider_layout)
        self.min_r = ipywidgets.FloatText(value=-9e99, layout=minmax_layout)
        self.max_r = ipywidgets.FloatText(value=9e99, layout=minmax_layout)
        self.stretch_r = ipywidgets.Dropdown(options=stretches, value='linear', layout=stretch_layout)
        self.box_r = ipywidgets.HBox([self.slider_r, self.min_r, self.max_r, self.stretch_r])
        self.slider_r.observe(self.scale_red, names='value')
        self.stretch_r.observe(self.scale_red, names='value')
        self.min_r.observe(self.refresh_slider, names='value')
        self.max_r.observe(self.refresh_slider, names='value')
        
        self.slider_b = ipywidgets.FloatRangeSlider(description = '<b style="color:#496bd8">Blue:</b>',
                                                    min = -9e99, max = 9e99, step = 1e98, value = (-9e99, 9e99),
                                                    layout = slider_layout)
        self.min_b = ipywidgets.FloatText(value=-9e99, layout=minmax_layout)
        self.max_b = ipywidgets.FloatText(value=9e99, layout=minmax_layout)
        self.stretch_b = ipywidgets.Dropdown(options=stretches, value='linear', layout=stretch_layout)
        self.box_b = ipywidgets.HBox([self.slider_b, self.min_b, self.max_b, self.stretch_b])
        self.slider_b.observe(self.scale_blue, names='value')
        self.stretch_b.observe(self.scale_blue, names='value')
        self.min_b.observe(self.refresh_slider, names='value')
        self.max_b.observe(self.refresh_slider, names='value')
        
        cube_shape = self.ctrl.get_shape()
        ch_len = cube_shape[0]
        self.slider_chr = ipywidgets.IntSlider(description = '<b style="color:#cc3737">ch-R:</b>',
                                               min = 0, max = ch_len-1, step = 1, value = 0,
                                               layout = slider_layout)
        self.slider_chr.observe(self.refresh_image, names='value')
        self.nbin_r = ipywidgets.IntText(description='nbin', value=1)
        self.nbin_r.observe(self.nbin_red)
        self.chbox_r = ipywidgets.HBox([self.slider_chr, self.nbin_r])
        self.slider_chb = ipywidgets.IntSlider(description = '<b style="color:#496bd8">ch-B:</b>',
                                               min = 0, max = ch_len-1, step = 1, value = 0,
                                               layout = slider_layout)
        self.slider_chb.observe(self.refresh_image, names='value')
        self.nbin_b = ipywidgets.IntText(description='nbin', value=1)
        self.nbin_b.observe(self.nbin_blue)
        self.chbox_b = ipywidgets.HBox([self.slider_chb, self.nbin_b])
        
        shape = self.ctrl.get_shape()
        self.img = ipywidgets.Image(height=shape[1], width=shape[2], format='bmp')
        return
    
    def refresh_slider(self, change={}):
        min_r = self.min_r.value
        max_r = self.max_r.value
        min_b = self.min_b.value
        max_b = self.max_b.value
        
        self.slider_r.set_trait('min', min_r)
        self.slider_r.set_trait('max', max_r)
        self.slider_r.set_trait('step', (max_r - min_r)/1000)
        
        self.slider_b.set_trait('min', min_b)
        self.slider_b.set_trait('max', max_b)
        self.slider_b.set_trait('step', (max_b - min_b)/1000)
        return
    
    def init_slider(self):
        dminmax = self.ctrl.get_minmax()
        
        if dminmax['min'] == dminmax['max']:
            dminmax['min'] *= 0.8
            dminmax['max'] *= 1.2
            pass
        
        self.min_r.set_trait('value', dminmax['min'])
        self.max_r.set_trait('value', dminmax['max'])
        self.min_b.set_trait('value', dminmax['min'])
        self.max_b.set_trait('value', dminmax['max'])
        return
    
    def nbin_red(self, change):
        nbin = self.nbin_r.value
        self.ctrl.velocity_binning_red(nbin)
        self.refresh_image()
        return
    
    def nbin_blue(self, change):
        nbin = self.nbin_r.value
        self.ctrl.velocity_binning_blue(nbin)
        self.refresh_image()
        return
    
    def scale_red(self, change):
        dmin, dmax = self.slider_r.value
        stretch = self.stretch_r.value
        self.ctrl.set_data_scale_red(dmin, dmax, stretch)
        self.refresh_image()
        return
    
    def scale_blue(self, change):
        dmin, dmax = self.slider_b.value
        stretch = self.stretch_b.value
        self.ctrl.set_data_scale_blue(dmin, dmax, stretch)
        self.refresh_image()
        return
    
    def generate_image(self):
        ch_r = self.slider_chr.value
        ch_b = self.slider_chb.value
        r = self.ctrl.get_red_ch(ch_r)
        b = self.ctrl.get_blue_ch(ch_b)
        
        ny, nx = r.shape
    
        imga = numpy.zeros([ny, nx, 3], dtype=numpy.uint8)
        imga[:,:,0] = r
        imga[:,:,1] = (r/2 + b/2)
        imga[:,:,2] = b
        img = PIL.Image.fromarray(imga)
        return img
    
    def refresh_image(self, *args, **kwargs):
        img = self.generate_image()
        imgio = io.BytesIO()
        img.save(imgio, 'bmp')
        imgio.seek(0)        
        self.img.value = imgio.read()
        return 



__all__ = [
    'jpy_red_blue_cube',
]
