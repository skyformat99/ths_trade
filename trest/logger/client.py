# !/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from functools import partial


class _SysLogger(object):
    def __init__(self):
        pass

    @property
    def debug(self):
        """
        logging debug message
        """
        return partial(logging.getLogger('tornado.debug.log').debug)

    @property
    def info(self):
        """
        logging info message
        """
        return partial(logging.getLogger('tornado.info.log').info)

    @property
    def warning(self):
        """
        logging warning message
        """
        return partial(logging.getLogger('tornado.warning.log').warning)

    @property
    def error(self):
        """
        logging error message
        """
        return partial(logging.getLogger('tornado.error.log').error)

    @property
    def critical(self):
        """
        logging critical message
        """
        return partial(logging.getLogger('tornado.critical.log').critical)

SysLogger = syslogger = _SysLogger()
