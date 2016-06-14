import sys
import os
import logging
import inspect

class LogMixin(object):
    @property
    def logger(self):
        name = '.'.join([__name__, self.__class__.__name__])
        return logging.getLogger(name)

def relpath(path):
    filename = inspect.getfile(sys._getframe(1))
    realdir = os.path.split(os.path.realpath(filename))[0]
    return os.path.relpath(os.path.join(realdir, path))

