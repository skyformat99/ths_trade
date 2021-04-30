#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
异常Class
"""
from tornado.web import Finish
from tornado.web import HTTPError


class ArgumentError(Exception):
    """Arguments error"""


class ConfigError(Exception):
    """raise config error"""


class NotCallableError(Exception):
    """callable error"""


class Http404(HTTPError):
    def __init__(self, log_message='not found', *args, **kwargs):
        super(Http404, self).__init__(404, log_message, *args, **kwargs)


class JsonError(Finish):
    """docstring for JsonError"""

    def __init__(self, msg='error', code=1, data=[], **kwargs):
        if hasattr(data, 'as_dict'):
            data = data.as_dict()
        elif type(data) == list:
            data = [item.as_dict() if hasattr(item, 'as_dict') else item for item in data]

        res = {
            'msg': msg,
            'code': code,
            'result': data,
        }
        res.update(kwargs)
        super(JsonError, self).__init__(res)
