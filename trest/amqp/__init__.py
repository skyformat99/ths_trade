#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json

from trest.config import settings

from .publisher import Publisher
from ..utils import func


def push_message(msg, msg_type='transfer_websocket'):
    """
    发送消息，消息格式根据需求和前端约定
    """
    option = {}
    option['msg_type'] = msg_type
    option['exchange'] = 'async_ex.message'
    option['routing_key'] = 'async_rtk.message'
    option['queue_name'] = 'async_q.message'
    option['durable'] = True
    option['auto_delete'] = False
    return push_to_mq(msg, option)

def push_sms(param, sms_platform):
    """
    发送短信
    """
    param['action'] = 'push_sms'
    option = {}
    option['msg_type'] = sms_platform
    option['exchange'] = 'async_ex.sms'
    option['routing_key'] = 'async_rtk.sms'
    option['queue_name'] = 'async_q.sms'
    option['durable'] = True
    option['auto_delete'] = False
    return push_to_mq(param, option)

def push_email(param, email_platform='default'):
    """
    发送Email
    """
    param['action'] = 'push_email'
    option = {}
    option['msg_type'] = email_platform
    option['exchange'] = 'async_ex.email'
    option['routing_key'] = 'async_rtk.email'
    option['queue_name'] = 'async_q.email'
    option['durable'] = True
    option['auto_delete'] = False
    return push_to_mq(param, option)

def push_to_mq(param, option):
    msg = {}
    msg['msg_type'] = option.get('msg_type', '')
    msg['msg_md5'] = func.md5(json.dumps(param))
    msg['msg'] = param
    pusher = Publisher(settings.rabbitmq_config)
    option['exchange_type'] = option.get('exchange_type', 'topic')
    res = pusher.push(msg, option)
    # print(res)
    return res
