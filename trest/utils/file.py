#!/usr/bin/env python
# -*- coding: utf-8  -*-

import os
import hashlib
import mimetypes
import tornado.httputil

from trest.config import settings


class Uploader(object):

    @staticmethod
    def upload_img(file_md5, img, save_name, path, param):
        path = f'{settings.STATIC_PATH}/upload/{path}'
        if not os.path.exists(path):
            os.makedirs(path)
        path_file = path + save_name

        file_ext = FileUtil.file_ext(img['filename'])

        with open(path_file, 'wb') as f:
            f.write(img['body'])

        prefix = settings.get('static_url_prefix', '/static')
        param.update({
            'file_md5': file_md5,
            'file_ext': file_ext,
            'file_size': FileUtil.file_size(path_file),
            'file_mimetype': FileUtil.file_mimetype(path_file),
            'origin_name': img['filename'],
            'path_file': path_file.replace(settings.STATIC_PATH, prefix),
        })
        return param


class FileUtil(object):
    """docstring for FileUtil"""
    @staticmethod
    def file_name(fname):
        return fname.split("/")[-1]

    @staticmethod
    def file_md5(fname):
        """
        from http://stackoverflow.com/questions/3431825/generating-a-md5-checksum-of-a-file
        """
        hash = hashlib.md5()
        with open(fname, "rb") as f:
            for chunk in iter(lambda: f.read(40960), b""):
                hash.update(chunk)
        return hash.hexdigest()

    @staticmethod
    def file_ext(fname):
        ext = os.path.splitext(fname)[1]
        return ext[1:] if ext[0:1]=='.' else ext

    @staticmethod
    def file_mimetype(fname):
        return mimetypes.guess_type(fname)[0] or 'application/octet-stream'

    @staticmethod
    def file_size(fname):
        """获取文件的大小,结果保留两位小数，单位为Byte(1Byte=8Bit)
        """
        return os.path.getsize(fname)
