#!/usr/bin/env python
# -*- coding: utf-8  -*-
import time
import smtplib
import tornado
import email.mime.text
import email.mime.multipart

from email.utils import parseaddr
from email.utils import formataddr
from email.header import Header

from trest.config import settings


def _format_addr(s):
    name,addr = parseaddr(s)
    return formataddr((Header(name,'utf-8').encode(), addr))


# sendmail({'to_addr':'leeyisoft@qq.com', 'subject':'ly test subject', 'content': 'abc'})
@tornado.gen.coroutine
def sendmail(params):
    """发送Email，支持HTML格式内容，支持定义发送者名称，定义邮件主题
    """
    to_name = params.get('to_name', '')
    to_addr = params.get('to_addr', None)
    subject = params.get('subject', None)
    content = params.get('content', None)
    if to_addr is None or subject is None or content is None:
        return False

    from_name = settings.email.get('from_name', '')
    from_addr = settings.email.get('from_addr', '')
    smtp_sever = settings.email.get('smtp_sever', '')
    smtp_port = settings.email.get('smtp_port', '')
    auth_code = settings.email.get('auth_code', '')

    msg = email.mime.multipart.MIMEMultipart()
    msg['from'] = _format_addr('%s <%s>' % (from_name, from_addr))
    msg['to'] = _format_addr('%s <%s>' % (to_name, to_addr))
    msg['subject'] = subject
    msg['date'] = time.strftime("%a,%d %b %Y %H:%M:%S %z")
    htm = email.mime.text.MIMEText(content, 'html','utf-8')
    msg.attach(htm)
    smtp = smtplib
    smtp = smtplib.SMTP()
    '''
    smtplib的connect（连接到邮件服务器）、login（登陆验证）、sendmail（发送邮件）
    '''
    smtp.connect(smtp_sever, smtp_port)
    smtp.login(from_addr, auth_code)
    smtp.sendmail(from_addr, to_addr, str(msg))
    smtp.quit()
    return True
