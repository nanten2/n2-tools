
import ipywidgets

import io
import warnings
import numpy
import PIL.Image


class jpy_rgbimage(object):
    qlook_size = 500
    
    def __init__(self, red=None, green=None, blue=None,
                 nanval='max', qlook_size=500):
        self.qlook_size = qlook_size
        self.data_red = rgbdata(red, nanval, qlook_size)
        self.data_green = rgbdata(green, nanval, qlook_size)
        self.data_blue = rgbdata(blue, nanval, qlook_size)
        self.gui = rgbgui(self)
        pass
    
    def _ipython_display_(self):
        self.gui._ipython_display_()
        return
    
    def get_qlook_shape(self):
        for data in [self.data_red, self.data_green, self.data_blue]:
            if data.qlook_shape is not None:
                return data.qlook_shape
            continue
        return
    
    def get_minmax(self):
        return {
            'min_r': self.data_red.dmin,
            'max_r': self.data_red.dmax,
            'min_g': self.data_green.dmin,
            'max_g': self.data_green.dmax,
            'min_b': self.data_blue.dmin,
            'max_b': self.data_blue.dmax,
        }
    
    def get_qlook(self):
        return {
            'red': self.data_red.qlook_scaled,
            'green': self.data_green.qlook_scaled,
            'blue': self.data_blue.qlook_scaled,
        }
    
    def set_qlook_scale_red(self, scale_min, scale_max, stretch):
        self.data_red.scale_qlook(scale_min, scale_max, stretch)
        return

    def set_qlook_scale_green(self, scale_min, scale_max, stretch):
        self.data_green.scale_qlook(scale_min, scale_max, stretch)
        return
    
    def set_qlook_scale_blue(self, scale_min, scale_max, stretch):
        self.data_blue.scale_qlook(scale_min, scale_max, stretch)
        return

    def get_image(self):
        self.data_red.scale_data()
        self.data_green.scale_data()
        self.data_blue.scale_data()

        r = self.data_red.data_scaled
        g = self.data_green.data_scaled
        b = self.data_blue.data_scaled

        ny, nx = r.shape
        
        imga = numpy.zeros([ny, nx, 3], dtype=numpy.uint8)
        imga[:,:,0] = r
        imga[:,:,1] = g
        imga[:,:,2] = b
        img = PIL.Image.fromarray(imga)
        return img
    
    def save(self, path):
        img = self.get_image()
        img.save(path)
        return



class rgbdata(object):
    data = None
    data_scaled = None
    data_shape = None
    qlook = None
    qlook_scaled = None
    qlook_shape = None
    dmin = None
    dmax = None
    scale_min = None
    scale_max = None
    scale_stretch = None
    
    def __init__(self, data, nanval='max', qlook_size=500):
        warnings.filterwarnings('ignore')
        self.set_data(data, nanval, qlook_size)
        warnings.filterwarnings('default')
        pass
    
    def set_data(self, data, nanval='max', qlook_size=500):
        if data is None: return
        ny, nx = data.shape
        self.qlook_shape = (int(nx/(ny/qlook_size)), int(qlook_size))
        
        data = data.copy()
        data = data[::-1,:]
        
        if nanval == 'max':
            data[data!=data] = numpy.nanmax(data)
        elif nanval == 'min':
            data[data!=data] = numpy.nanmin(data)
        else:
            data[data!=data] = nanval
            pass
            
        self.data = data
        self.qlook = numpy.asanyarray(
            PIL.Image.fromarray(data).resize(self.qlook_shape)
        )
        self.dmin = numpy.nanmin(data)
        self.dmax = numpy.nanmax(data)
        self.scale_qlook()
        self.scale_data()
        return
    
    def scale_data(self):
        warnings.filterwarnings('ignore')
        self.data_scaled = self._scale(
            self.data, self.scale_min, self.scale_max, self.scale_stretch
        )
        warnings.filterwarnings('default')
        return self.data_scaled
    
    def scale_qlook(self, scale_min=None, scale_max=None, stretch='linear'):
        warnings.filterwarnings('ignore')
        self.qlook_scaled = self._scale(
            self.qlook, scale_min, scale_max, stretch
        )
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
        self.scale_min = scale_min
        self.scale_max = scale_max
            
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
        self.box_g._ipython_display_()
        self.box_b._ipython_display_()
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
        
        self.slider_g = ipywidgets.FloatRangeSlider(description = '<b style="color:#20af00">Green:</b>',
                                                                                    min = -9e99, max = 9e99, step = 1e98, value = (-9e99, 9e99),
                                                                                    layout = slider_layout)
        self.min_g = ipywidgets.FloatText(value=-9e99, layout=minmax_layout)
        self.max_g = ipywidgets.FloatText(value=9e99, layout=minmax_layout)
        self.stretch_g = ipywidgets.Dropdown(options=stretches, value='linear', layout=stretch_layout)
        self.box_g = ipywidgets.HBox([self.slider_g, self.min_g, self.max_g, self.stretch_g])
        self.slider_g.observe(self.scale_green, names='value')
        self.stretch_g.observe(self.scale_green, names='value')
        self.min_g.observe(self.refresh_slider, names='value')
        self.max_g.observe(self.refresh_slider, names='value')
        
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
    
        qlook_shape = self.ctrl.get_qlook_shape()
        self.img = ipywidgets.Image(height=qlook_shape[0], width=qlook_shape[1], format='bmp')
        return
    
    def refresh_slider(self, change={}):
        min_r = self.min_r.value
        max_r = self.max_r.value
        min_g = self.min_g.value
        max_g = self.max_g.value
        min_b = self.min_b.value
        max_b = self.max_b.value
        
        self.slider_r.set_trait('min', min_r)
        self.slider_r.set_trait('max', max_r)
        self.slider_r.set_trait('step', (max_r - min_r)/1000)
        
        self.slider_g.set_trait('min', min_g)
        self.slider_g.set_trait('max', max_g)
        self.slider_g.set_trait('step', (max_g - min_g)/1000)
        
        self.slider_b.set_trait('min', min_b)
        self.slider_b.set_trait('max', max_b)
        self.slider_b.set_trait('step', (max_b - min_b)/1000)
        return
    
    def init_slider(self):
        dminmax = self.ctrl.get_minmax()
        
        if dminmax['min_r'] == dminmax['max_r']:
            dminmax['min_r'] *= 0.8
            dminmax['max_r'] *= 1.2
            pass
        
        if dminmax['min_g'] == dminmax['max_g']:
            dminmax['min_g'] *= 0.8
            dminmax['max_g'] *= 1.2
            pass
        
        if dminmax['min_b'] == dminmax['max_b']:
            dminmax['min_b'] *= 0.8
            dminmax['max_b'] *= 1.2
            pass
            
        self.min_r.set_trait('value', dminmax['min_r'])
        self.max_r.set_trait('value', dminmax['max_r'])
        self.min_g.set_trait('value', dminmax['min_g'])
        self.max_g.set_trait('value', dminmax['max_g'])
        self.min_b.set_trait('value', dminmax['min_b'])
        self.max_b.set_trait('value', dminmax['max_b'])
        return
    
    def scale_red(self, change):
        dmin, dmax = self.slider_r.value
        stretch = self.stretch_r.value
        self.ctrl.set_qlook_scale_red(dmin, dmax, stretch)
        self.refresh_image()
        return
    
    def scale_green(self, change):
        dmin, dmax = self.slider_g.value
        stretch = self.stretch_g.value
        self.ctrl.set_qlook_scale_green(dmin, dmax, stretch)
        self.refresh_image()
        return
    
    def scale_blue(self, change):
        dmin, dmax = self.slider_b.value
        stretch = self.stretch_b.value
        self.ctrl.set_qlook_scale_blue(dmin, dmax, stretch)
        self.refresh_image()
        return
    
    def refresh_image(self):
        d = self.ctrl.get_qlook()
        nx, ny = self.ctrl.get_qlook_shape()
        
        imga = numpy.zeros([ny, nx, 3], dtype=numpy.uint8)
        imga[:,:,0] = d['red']
        imga[:,:,1] = d['green']
        imga[:,:,2] = d['blue']
        img = PIL.Image.fromarray(imga)
        imgio = io.BytesIO()
        img.save(imgio, 'bmp')
        imgio.seek(0)        
        self.img.value = imgio.read()
        return



__all__ = [
    'jpy_rgbimage',
]
