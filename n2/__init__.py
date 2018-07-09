
__version__ = '0.0.10'

from .data import *
from .jupyter_tools import *

from . import plot



if __name__ != '__main__':
    import n2.log
    import platform
    logger = log.get_logger(__name__)
    logger.info('python {}'.format(platform.python_version()))
    logger.info('n2-tools {__version__}'.format(**locals()))
    pass
