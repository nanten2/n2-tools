
import sys
import logging

level = logging.DEBUG

c_end = '\033[0m'
c_error = '\033[31m'
c_warning = '\033[33m'
c_info = '\033[34m'
c_debug = '\033[37m'
c_time = '\033[37m'

timefmt = '%H:%M:%S'
fmt1 = c_time + '[%(asctime)s]' + c_end
fmt2 = ' %(levelname)s: %(message)s'
fmt_error = logging.Formatter(fmt1 + c_error + fmt2 + c_end)
fmt_warning = logging.Formatter(fmt1 + c_warning + fmt2 + c_end)
fmt_info = logging.Formatter(fmt1 + c_info + fmt2 + c_end)
fmt_debug = logging.Formatter(fmt1 + c_debug + fmt2 + c_end)
fmt_error.default_time_format = timefmt
fmt_warning.default_time_format = timefmt
fmt_info.default_time_format = timefmt
fmt_debug.default_time_format = timefmt


class error_filter(logging.Filter):
    def filter(self, record):
        return logging.ERROR <= record.levelno
    
class warning_filter(logging.Filter):
    def filter(self, record):
        return logging.WARNING <= record.levelno < logging.ERROR

class info_filter(logging.Filter):
    def filter(self, record):
        return logging.INFO <= record.levelno < logging.WARNING

class debug_filter(logging.Filter):
    def filter(self, record):
        return logging.DEBUG <= record.levelno < logging.INFO



def get_logger(name):
    logger = logging.getLogger(name)
    if logger.hasHandlers():
        print(logger.handlers)
        return logger
    
    e_handler = logging.StreamHandler(sys.stdout)
    e_handler.setFormatter(fmt_error)
    e_handler.addFilter(error_filter())
    e_handler.setLevel(logging.ERROR)
    
    w_handler = logging.StreamHandler(sys.stdout)
    w_handler.setFormatter(fmt_warning)
    w_handler.addFilter(warning_filter())
    w_handler.setLevel(logging.WARNING)

    i_handler = logging.StreamHandler(sys.stdout)
    i_handler.setFormatter(fmt_info)
    i_handler.addFilter(info_filter())
    i_handler.setLevel(logging.INFO)

    d_handler = logging.StreamHandler(sys.stdout)
    d_handler.setFormatter(fmt_debug)
    d_handler.addFilter(debug_filter())
    d_handler.setLevel(logging.DEBUG)
    
    logger.addHandler(e_handler)
    logger.addHandler(w_handler)
    logger.addHandler(i_handler)
    logger.addHandler(d_handler)
    logger.setLevel(level)
    logger.propagate = False
    return logger

