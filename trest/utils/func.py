#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import sys
import time
import json
import uuid
import pytz
import hmac
import random
import string
import hashlib
import datetime
import requests
import dateutil.parser

from decimal import Decimal

from .sendmail import sendmail
from ..logger import SysLogger


_PROTECTED_TYPES = (
    type(None), int, float, Decimal, datetime.datetime, datetime.date, datetime.time,
)

"""
常用函数
"""
def sendmail(params):
    return sendmail(params);

def md5(val):
    if type(val)!=bytes:
        val = val.encode('utf-8')
    return hashlib.md5(val).hexdigest()

def uuid32():
    return str(uuid.uuid4()).replace('-','')

def hump2underline(raw_str):
    """
    驼峰法转换为下划线
    """
    p = re.compile(r'([a-z]|\d)([A-Z])')
    sub_str = p.sub(r'\1_\2', raw_str).lower()
    return sub_str

def underline2hump(raw_str, first_letter_upper = False):
    """
    下划线转换为驼峰法
    >>> underline2hump('abc_def_ghi')
    >>>     abcDefGhi
    >>> underline2hump('abc_def_ghi', True)
    >>>     AbcDefGhi
    """
    p = re.compile(r'(_\w)')
    sub_str = p.sub(lambda x:x.group(1)[1].upper(), raw_str)
    if first_letter_upper:
        sub_str = sub_str[0:1].upper() + sub_str[1:]
    return  sub_str

def random_string(length=12, allowed_chars=None):
    """
    Return a securely generated random string.

    The default length of 12 with the a-z, A-Z, 0-9 character set returns
    a 71-bit value. log_2((26+26+10)^12) =~ 71 bits
    """
    allowed_chars = allowed_chars if allowed_chars else string.ascii_letters+string.digits
    return ''.join(random.choice(allowed_chars) for i in range(length))

def force_bytes(s, encoding='utf-8', strings_only=False, errors='strict'):
    """
    Similar to smart_bytes, except that lazy instances are resolved to
    strings, rather than kept as lazy objects.

    If strings_only is True, don't convert (some) non-string-like objects.
    """
    # Handle the common case first for performance reasons.
    if isinstance(s, bytes):
        if encoding == 'utf-8':
            return s
        else:
            return s.decode('utf-8', errors).encode(encoding, errors)
    if strings_only and isinstance(s, _PROTECTED_TYPES):
        return s
    if isinstance(s, memoryview):
        return bytes(s)
    if isinstance(s, object) or not isinstance(s, str):
        return str(s).encode(encoding, errors)
    else:
        return s.encode(encoding, errors)

def safestr(obj, encoding='utf-8'):
    r"""
    Converts any given object to utf-8 encoded string.

        >>> safestr('hello')
        'hello'
        >>> safestr(u'\u1234')
        '\xe1\x88\xb4'
        >>> safestr(2)
        '2'
    """
    if isinstance(obj, bytes):
        return obj.encode(encoding)
    elif isinstance(obj, str):
        return obj
    elif hasattr(obj, 'next'):  # iterator
        return itertools.imap(safestr, obj)
    else:
        return str(obj)

def is_email(email):
    regex = r'^[0-9a-zA-Z_\-\.]{0,19}@[0-9a-zA-Z_\-]{1,13}\.[a-zA-Z\.]{1,7}$'
    return True if re.match(regex, email) else False

def is_mobile(mobile, region):
    code_map = {
        'CN': ("中国","^(\\+?0?86\\-?)?1[345789]\\d{9}$"),
        'TW': ("台湾","^(\\+?886\\-?|0)?9\\d{8}$"),
        'HK': ("香港","^(\\+?852\\-?)?[569]\\d{3}\\-?\\d{4}$"),
        'MS': ("马来西亚","^(\\+?6?01){1}(([145]{1}(\\-|\\s)?\\d{7,8})|([236789]{1}(\\s|\\-)?\\d{7}))$"),
        'PH': ("菲律宾","^(\\+?0?63\\-?)?\\d{10}$"),
        'TH': ("泰国","^(\\+?0?66\\-?)?\\d{10}$"),
        'SG': ("新加坡","^(\\+?0?65\\-?)?\\d{10}$"),
        'DZ': ("阿尔及利亚", "^(\\+?213|0)(5|6|7)\\d{8}$"),
        'SY': ("叙利亚","^(!?(\\+?963)|0)?9\\d{8}$"),
        'SA': ("沙特阿拉伯","^(!?(\\+?966)|0)?5\\d{8}$"),
        'US': ("美国","^(\\+?1)?[2-9]\\d{2}[2-9](?!11)\\d{6}$"),
        'CZ': ("捷克共和国","^(\\+?420)? ?[1-9][0-9]{2} ?[0-9]{3} ?[0-9]{3}$"),
        'DE': ("德国","^(\\+?49[ \\.\\-])?([\\(]{1}[0-9]{1,6}[\\)])?([0-9 \\.\\-\\/]{3,20})((x|ext|extension)[ ]?[0-9]{1,4})?$"),
        'DK': ("丹麦","^(\\+?45)?(\\d{8})$"),
        'GR': ("希腊","^(\\+?30)?(69\\d{8})$"),
        'AU': ("澳大利亚","^(\\+?61|0)4\\d{8}$"),
        'GB': ("英国","^(\\+?44|0)7\\d{9}$"),
        'CA': ("加拿大","^(\\+?1)?[2-9]\\d{2}[2-9](?!11)\\d{6}$"),
        'IN': ("印度","^(\\+?91|0)?[789]\\d{9}$"),
        'NZ': ("新西兰","^(\\+?64|0)2\\d{7,9}$"),
        'ZA': ("南非","^(\\+?27|0)\\d{9}$"),
        'ZM': ("赞比亚","^(\\+?26)?09[567]\\d{7}$"),
        'ES': ("西班牙","^(\\+?34)?(6\\d{1}|7[1234])\\d{7}$"),
        'FI': ("芬兰","^(\\+?358|0)\\s?(4(0|1|2|4|5)?|50)\\s?(\\d\\s?){4,8}\\d$"),
        'FR': ("法国","^(\\+?33|0)[67]\\d{8}$"),
        'IL': ("以色列","^(\\+972|0)([23489]|5[0248]|77)[1-9]\\d{6}"),
        'HU': ("匈牙利","^(\\+?36)(20|30|70)\\d{7}$"),
        'IT': ("意大利","^(\\+?39)?\\s?3\\d{2} ?\\d{6,7}$"),
        'JP': ("日本","^(\\+?81|0)\\d{1,4}[ \\-]?\\d{1,4}[ \\-]?\\d{4}$"),
        'NO': ("挪威","^(\\+?47)?[49]\\d{7}$"),
        'BE': ("比利时","^(\\+?32|0)4?\\d{8}$"),
        'PL': ("波兰","^(\\+?48)? ?[5-8]\\d ?\\d{3} ?\\d{2} ?\\d{2}$"),
        'BR': ("巴西","^(\\+?55|0)\\-?[1-9]{2}\\-?[2-9]{1}\\d{3,4}\\-?\\d{4}$"),
        'PT': ("葡萄牙","^(\\+?351)?9[1236]\\d{7}$"),
        'RU': ("俄罗斯","^(\\+?7|8)?9\\d{9}$"),
        'RS': ("塞尔维亚","^(\\+3816|06)[- \\d]{5,9}$"),
        'R': ("土耳其","^(\\+?90|0)?5\\d{9}$"),
        'VN': ("越南","^(\\+?84|0)?((1(2([0-9])|6([2-9])|88|99))|(9((?!5)[0-9])))([0-9]{7})$"),
    }
    #正则匹配电话号码
    # mobile = "13692177708"
    (coutry, regex) = code_map.get(region.upper(), ('', '.*'))
    if regex=='.*':
        raise Exception(1, '不支持的区域')
    match = re.match(regex, mobile)
    return True if match else False

def is_phone(phone, region='CN'):
    """
    #写一个正则表达式，能匹配出多种格式的电话号码，包括
    #(021)88776543   010-55667890 02584453362  0571 66345673
    #\(?0\d{2,3}[) -]?\d{7,8}
    # import re
    # phone="(021)88776543 010-55667890 02584533622 057184720483 837922740"
    """
    m = re.findall(r"\(?0\d{2,3}[) -]?\d{7,8}",phone)
    if m:
        return True
    else:
        return False

def is_phone_or_mobile(phone, region='CN'):
    return func.is_mobile(phone, region) or func.is_phone(phone, region)

def sha256_sign(val):
    """
    SHA256签名
    """
    try:
        m = hashlib.sha256()
        m.update(val.encode('utf-8'))
        return m.hexdigest()
    except Exception as e:
        raise e
    return ''

def sha256_verify_sign(sign, val):
    SysLogger.debug('sha256_sign(val): ' + sha256_sign(val))
    return True if sha256_sign(val)==sign else False
