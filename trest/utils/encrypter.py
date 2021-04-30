#!/usr/bin/env python
# -*- coding: utf8 -*-

import os
import rsa
import json
import hashlib
import base64
from Crypto.Cipher import AES

from trest.config import settings


class RSAEncrypter(object):
    """RSA加密解密
    参考 https://stuvel.eu/python-rsa-doc/index.html
    对应JavaScript版本参考 https://github.com/travist/jsencrypt
    [description]
    """
    @classmethod
    def encrypt(cls, plaintext, keydata):
        #明文编码格式
        content = plaintext.encode('utf8')
        if os.path.isfile(keydata):
            with open(keydata) as publicfile:
                keydata = publicfile.read()

        pubkey = rsa.PublicKey.load_pkcs1_openssl_pem(keydata)
        #公钥加密
        crypto = rsa.encrypt(content, pubkey)
        return base64.b64encode(crypto).decode('utf8')

    @classmethod
    def decrypt(cls, ciphertext, keydata):
        if os.path.isfile(keydata):
            with open(keydata) as privatefile:
                keydata = privatefile.read()
        try:
            ciphertext = base64.b64decode(ciphertext)
            privkey = rsa.PrivateKey.load_pkcs1(keydata, format='PEM')
            con = rsa.decrypt(ciphertext, privkey)
            return con.decode('utf8')
        except Exception as e:
            pass
        return False

    @classmethod
    def signing(cls, message, privkey):
        """ 签名
            https://legrandin.github.io/pycryptodome/Doc/3.2/Crypto.Signature.pkcs1_15-module.html
        """
        from Crypto.Signature import pkcs1_15
        from Crypto.Hash import SHA256
        from Crypto.PublicKey import RSA

        if os.path.isfile(privkey):
            with open(privkey) as privatefile:
                privkey = privatefile.read()
        try:
            key = RSA.import_key(privkey)
            h = SHA256.new(message.encode('utf8'))
            sign = pkcs1_15.new(key).sign(h)
            sign = base64.b64encode(sign).decode('utf8')
            return sign
        except Exception as e:
            raise e

    @classmethod
    def verify(cls, message, sign, pubkey):
        """ 验证签名
            https://legrandin.github.io/pycryptodome/Doc/3.2/Crypto.Signature.pkcs1_15-module.html
        """
        from Crypto.Signature import pkcs1_15
        from Crypto.Hash import SHA256
        from Crypto.PublicKey import RSA
        res = False
        sign = base64.b64decode(sign)
        # print('sign', type(sign), sign)
        try:
            key = RSA.importKey(pubkey)
            h = SHA256.new(message.encode('utf8'))
            pkcs1_15.new(key).verify(h, sign)
            res = True
        except (ValueError, TypeError) as e:
            raise e
        except Exception as e:
            raise e
        return res


class AESEncrypter(object):
    def __init__(self, key, iv=None):
        self.key = key.encode('utf8')
        self.iv = iv if iv else bytes(key[0:16], 'utf8')

    def _pad(self, text):
        text_length = len(text)
        padding_len = AES.block_size - int(text_length % AES.block_size)
        if padding_len == 0:
            padding_len = AES.block_size

        t2 = chr(padding_len) * padding_len
        t2 = t2.encode('utf8')
        t3 = text + t2
        return t3

    def _unpad(self, text):
        pad = ord(text[-1])
        return text[:-pad]

    def encrypt(self, raw):
        raw = raw.encode('utf8')
        raw = self._pad(raw)
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        encrypted = cipher.encrypt(raw)
        return base64.b64encode(encrypted).decode('utf8')

    def decrypt(self, enc):
        enc = enc.encode('utf8')
        enc = base64.b64decode(enc)
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        decrypted = cipher.decrypt(enc)
        return self._unpad(decrypted.decode('utf8'))

class AESSkyPay:
    """
    Tested under Python 3.7 and pycryptodome
    """
    BLOCK_SIZE = 16
    def __init__(self, key):
        #菲律宾支付通道 SkyPay Payment Specification.lending.v1.16.pdf
        # SkyPay 对密码做了如下处理
        s1 = hashlib.sha1(bytes(key, encoding='utf-8')).digest()
        s2 = hashlib.sha1(s1).digest()
        self.key = s2[0:16]
        self.mode = AES.MODE_ECB

    def pkcs5_pad(self,s):
        """
        padding to blocksize according to PKCS #5
        calculates the number of missing chars to BLOCK_SIZE and pads with
        ord(number of missing chars)
        @see: http://www.di-mgt.com.au/cryptopad.html

        @param s: string to pad
        @type s: string

        @rtype: string
        """
        BS = self.BLOCK_SIZE
        return s + ((BS - len(s) % BS) * chr(BS - len(s) % BS)).encode('utf8')

    def pkcs5_unpad(self,s):
        """
        unpadding according to PKCS #5

        @param s: string to unpad
        @type s: string

        @rtype: string
        """
        return s[:-ord(s[len(s) - 1:])]

    # 加密函数，如果text不足16位就用空格补足为16位，
    # 如果大于16当时不是16的倍数，那就补足为16的倍数。
    # 补足方法：PKCS5
    def encrypt(self, text):
        cryptor = AES.new(self.key, self.mode)
        # 这里密钥key 长度必须为16（AES-128）,
        # 24（AES-192）,或者32 （AES-256）Bytes 长度
        # 目前AES-128 足够目前使用
        ciphertext = cryptor.encrypt(self.pkcs5_pad(text.encode('utf8')))
        # 因为AES加密时候得到的字符串不一定是ascii字符集的，输出到终端或者保存时候可能存在问题
        # 所以这里将加密的字符串进行base64编码
        return base64.b64encode(ciphertext).decode()
    def decrypt(self, text):
        cryptor = AES.new(self.key, self.mode)
        plain_text = cryptor.decrypt(base64.b64decode(text))
        return bytes.decode(self.pkcs5_unpad(plain_text))


def aes_decrypt(ciphertext, secret=None, prefix='aes:::'):
    secret = secret if secret else settings.default_aes_secret
    cipher = AESEncrypter(secret)
    prefix_len = len(prefix)
    if ciphertext[0:prefix_len]==prefix:
        return cipher.decrypt(ciphertext[prefix_len:])
    else:
        return ciphertext

def aes_encrypt(plaintext, secret=None, prefix='aes:::'):
    secret = secret if secret else settings.default_aes_secret
    cipher = AESEncrypter(secret)
    encrypted = cipher.encrypt(plaintext)
    return '%s%s' % (prefix, encrypted)
