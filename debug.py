import functools
import inspect
import sys

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
 
def logthis(f):
    @functools.wraps(f)
    def logged(*args, **kwargs):
        if sys.version_info.major == 3:
            f_signature = inspect.signature(f)
            f_callargs = f_signature.bind(*args, **kwargs)
        elif sys.version_info.major == 2:
            f_callargs = inspect.getcallargs(f, *args, **kwargs)
        logger.debug("Called {:s} with arguments {:s}" .format(f.__name__, repr(f_callargs)))
        return f(*args, **kwargs)
    return logged


class LoggingContext(object):
    def __init__(self, logger, level=None, handler=None, close=True):
        self.logger = logger
        self.level = level
        self.handler = handler
        self.close = close

    def __enter__(self):
        if self.level is not None:
            self.old_level = self.logger.level
            self.logger.setLevel(self.level)
        if self.handler:
            self.logger.addHandler(self.handler)

    def __exit__(self, et, ev, tb):
        if self.level is not None:
            self.logger.setLevel(self.old_level)
        if self.handler:
            self.logger.removeHandler(self.handler)
        if self.handler and self.close:
            self.handler.close()
        # implicit return of None => don't swallow exceptions
