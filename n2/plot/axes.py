
import matplotlib.pyplot


def subplots(xpix, ypix, ncols=1, nrows=1, left=50, right=20, bottom=50,
              top=20, wspace=0, hspace=0, dpi=100, projection=None):
    wfig = xpix * ncols + wspace * (ncols - 1) + left + right
    hfig = ypix * nrows + hspace * (nrows - 1) + bottom + top
    figsize = (wfig/dpi, hfig/dpi)
    
    fig = matplotlib.pyplot.figure(figsize=figsize)
    ax = []
    for _r in range(nrows):
        for _c in range(ncols):
            l = (left + _c * (xpix + wspace)) / wfig
            b = 1 - (top + (_r + 1) * ypix + _r * hspace) / hfig
            w = xpix / wfig
            h = ypix / hfig
            _ax = fig.add_axes([l, b, w, h], projection=projection)
            ax.append(_ax)
            continue
        continue
    if len(ax)==1: ax = ax[0]
    return fig, ax



def colorbar(ax, image, direction='vertical', start=0, stop=1,
             space=0.01, width=8):
    
    def pix2figfraction(pix, fig, direction='x'):
        if direction == 'x':
            frac = pix / (fig.get_figwidth() * fig.dpi)
        elif direction == 'y':
            frac = pix / (fig.get_figheight() * fig.dpi)
        else:
            return
        return frac
    
    
    if type(ax) in [list, tuple]:
        bboxes = [_.get_position() for _ in ax]
        x0 = numpy.min([[_.x0, _.x1] for _ in bboxes])
        x1 = numpy.max([[_.x0, _.x1] for _ in bboxes])
        y0 = numpy.min([[_.y0, _.y1] for _ in bboxes])
        y1 = numpy.max([[_.y0, _.y1] for _ in bboxes])
        fig = ax[0].figure
    else:
        bbox = ax.get_position()
        x0 = bbox.x0
        x1 = bbox.x1
        y0 = bbox.y0
        y1 = bbox.y1
        fig = ax.figure
        pass
    
    if direction == 'vertical':
        l = x1 + space
        b = start * (y1 - y0) + y0
        w = pix2figfraction(width, fig, 'x')
        h = stop * (y1 - y0) - start * (y1 - y0)
        rect = (l, b, w, h)
    
    elif direction == 'horizontal':
        l = start * (x1 - x0) + x0
        b = y1 + space + pix2figfraction(18, fig, 'y')
        w = stop * (x1 - x0) - start * (x1 - x0)
        h = pix2figfraction(width, fig, 'y')
        rect = (l, b, w, h)
    
    else:
        return
        
    cb_ax = fig.add_axes(rect)
    cax = fig.colorbar(image, cax=cb_ax, orientation=direction)
    return cax



__all__ = [
    'subplots',
    'colorbar',
]
