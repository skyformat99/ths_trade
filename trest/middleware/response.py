#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
接口请求response之后发送MQ消息的中间件
"""
from tornado import gen
from trest.config import settings
from ..amqp import push_to_mq


class PushToMQMiddleware(object):
    @gen.coroutine
    def process_response(self, handler, clear, chunk):
        """
        请求结束后响应时调用，此方法在render之后，finish之前执行，可以对chunk做最后的封装和处理
        :param handler: handler对象
        :param chunk :
        响应内容，chunk为携带响内容的list，你不可以直接对chunk赋值，
        可以通过chunk[index]来改写响应内容，或再次执行handler.write()
        """
        if settings.get('rabbitmq_config', None) and handler.response_to_mq:
            data = handler.request.arguments
            # print('chunk', type(chunk), chunk)
            try:
                action = handler.request.uri.split('?')[0]
                param = {
                    'action': action,
                    'param': {k.strip(): ','.join([v.decode('utf-8').strip() for v in vl]) for (k, vl) in data.items()},
                    'chunk': [i.decode('utf-8') for i in chunk],
                }
                option = {}
                option['msg_type'] = action
                option['exchange_type'] = 'topic'
                option['exchange'] = 'async_ex.async_api'
                option['routing_key'] = 'async_rtk%s' % (action.replace('/','.'),)
                option['durable'] = True
                option['auto_delete'] = False
                push_to_mq(param, option)
            except Exception as e:
                pass
