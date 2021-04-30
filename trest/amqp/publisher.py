#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pika
import json
import traceback


class Publisher(object):
    connection = None
    channel = None

    def __init__(self, config):
        self.connection = pika.BlockingConnection(pika.URLParameters(config))
        self.channel = self.connection.channel()
        self.exchange_name = None
        self.queue_name = None

    def push(self, message, option):
        message = message if type(message)==str else json.dumps(message)

        exchange_type = option.get('exchange_type', 'fanout')
        exchange = option.get('exchange', 'push_msg')
        routing_key = option.get('routing_key', 'push_msg')
        queue_name = option.get('queue_name', None)
        durable = option.get('durable', True)
        auto_delete = option.get('auto_delete', False)
        try:
            self._declare_exchange(exchange_type, exchange, durable, auto_delete)
            # 如果接受到消息的Exchange没有与任何Queue绑定，则消息会被抛弃。
            if queue_name is not None:
                self._declare_queue(queue_name, routing_key, durable, auto_delete)
            self.channel.basic_publish(exchange=exchange,
                                      routing_key=routing_key,
                                      body=message)
            # print(" [x] Sent message %r" % message)
            return ('ok', 'success', [])
        except Exception as e:
            print(repr(e))
            traceback.print_exc()
            raise e
        finally:
            if self.connection:
                self.connection.close()

    def _declare_exchange(self, exchange_type, exchange_name, durable=True, auto_delete=False):
        """
        定义一个exchange
        """
        self.exchange_name = exchange_name
        self.channel.exchange_declare(exchange=exchange_name
            , exchange_type=exchange_type
            , durable=durable
            , auto_delete=auto_delete
        )

    def _declare_queue(self, queue_name, routing_key="*", durable=True, auto_delete=False):
        """
        定义一个queue
        """
        self.queue_name = queue_name
        self.channel.queue_declare(queue=queue_name, durable=durable, auto_delete=auto_delete)
        self.channel.queue_bind(exchange=self.exchange_name
            , queue=queue_name
            , routing_key=routing_key
        )

    def _create_connection(self):
        credentials = pika.PlainCredentials(self.config['username'], self.config['password'])
        parameters = pika.ConnectionParameters(self.config['host'], self.config['port'],
                                               self.config['virtual_host'], credentials, ssl=False)
        return pika.BlockingConnection(parameters)
