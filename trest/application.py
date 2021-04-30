#!/usr/bin/env python
# -*- coding: utf-8 -*-

import traceback

from tornado import web
from tornado import httputil
from tornado import version_info

from .logger import SysLogger
from .middleware.manager import Manager


class Application(web.Application):
    def __init__(self, handlers=None,
                 default_host="",
                 transforms=None,
                 wsgi=False,
                 middlewares=None,
                 **settings):

        super(Application, self).__init__(
            handlers=handlers,
            default_host=default_host,
            transforms=transforms,
            wsgi=wsgi, **settings)

        self.middleware_fac = Manager()
        if middlewares:
            self.middleware_fac.register_all(middlewares)
            self.middleware_fac.run_init(self)

        if version_info[0] > 3:
            this = self

            class HttpRequest(httputil.HTTPServerRequest):
                def __init__(self, *args, **kwargs):
                    super(HttpRequest, self).__init__(*args, **kwargs)
                    this.middleware_fac.set_request(self)
                    try:
                        this.middleware_fac.run_call(self)
                    except Exception as e:
                        SysLogger.trace_logger.error(traceback.format_exc())

            httputil.HTTPServerRequest = HttpRequest
