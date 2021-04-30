#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
access log中间件，替换tornado的log_request实现插件式日志输出
"""
import os
import time
import logging

access_log = logging.getLogger('access_log')


class AccessLogMiddleware(object):
    def process_init(self, application):
        application.settings['log_function'] = self.log

    def log(self, handler):
        if handler.request.uri.startswith('/static/'):
            return
        if handler.request.uri in ['/favicon.ico']:
            return
        data = handler.request.arguments
        dstr = '&'.join(['%s=%s'%(k.strip(), ','.join([v.decode('utf-8').strip() for v in vl])) for (k, vl) in data.items()])
        message = {
            'pid': os.getpid(),
            'remote_ip': handler.request.remote_ip,
            'created_at': time.time(),
            'protocol': handler.request.protocol,
            'host': handler.request.host,
            'method': handler.request.method,
            'uri': handler.request.uri,
            'version': handler.request.version,
            'status_code': handler.get_status(),
            'content_length': handler.request.headers.get('Content-Length', ''),
            'referer': handler.request.headers.get('Referer', ''),
            'user_agent': handler.request.headers.get('User-Agent', ''),
            'request_time': 1000.0 * handler.request.request_time(),
            'token': handler.get_argument('token', handler.request.headers.get('token', '')),
            'param': dstr,
        }
        access_log.info(message)
