
__version__ = '0.0.2'

from .data import *
from .jupyter_tools import *

if __name__ != '__main__':
    import n2.log
    logger = log.get_logger(__name__)
    logger.info('n2-tools (ver.{__version__})'.format(**locals()))
    pass
