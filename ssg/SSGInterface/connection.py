#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
from urllib2 import quote
import traceback

import httplib2

from bucket import SSGBucket
from ssg.common import utils, logs
from ssg.common.exceptions import *


class Location(object):

    DEFAULT = ''  # US Classic Region
    EU = 'EU'
    USWest = 'us-west-1'
    USWest2 = 'us-west-2'
    SAEast = 'sa-east-1'
    APNortheast = 'ap-northeast-1'
    APSoutheast = 'ap-southeast-1'
    APSoutheast2 = 'ap-southeast-2'
    CNNorth1 = 'cn-north-1'


class SSGConnection(object):

    auth_token = None
    #tmp var
    owner = None
    _host = None
    _port = None
    _header = None

    def __init__(self, group_key=None, bucket_class=SSGBucket):

        if not None == group_key:
            self.connection(group_key, bucket_class)
        self.bucket_class = bucket_class

    def connection(self, group_key, bucket_class=SSGBucket):
        self.group_key = group_key
        method = "POST"
        url = "key_tokens"
        param = {"group_key": self.group_key}

        response, content = self.make_request(method, url, body=param)

        try:
            utils.check_response(response)
            data = json.loads(content)
            self._set_token(data)
        except request_error as re:
            self.request_error_handler(re, 'connection', method, url,
                                       response)
        self.bucket_class = bucket_class

    def get_all_buckets(self):
        method = "GET"
        url = "keys"
        query = "/bucket"
        response, content = self.make_request(method, url, group_key=self.group_key, query=query)
        bucket_list = []
        try:
            utils.check_response(response)
            bucket_list = self._make_bucket_list(content)
        except request_error as re:
            self.request_error_handler(re, 'get_all_bucket', method, url,
                                       response, group_key=self.group_key)

        return bucket_list

    def create_bucket(self, bucket_name, location=Location.DEFAULT):
        """
        create bucket by bucket_name. return user's real bucket name

        :type bucket_name: string
        :param bucket_name: The name of the new bucket

        :type location: str
        :param location: The location of the new bucket. You can use one of the
            constants in :class: ssg.SSGInterface.connection.Location
        """
        method = "POST"
        url = 'buckets'
        request_param = {'name': bucket_name, 'group_key': self.group_key}
        bucket = None

        if not location == Location.DEFAULT:
            request_param.update({'location': location})

        response, content = self.make_request(method, url, body=request_param)

        try:
            utils.check_response(response)
            data = json.loads(content)
            real_name = self._get_real_name(data)
            bucket = self.bucket_class(self, bucket_name, real_name)
            print bucket_name+" is made success."

        except request_error as re:
            self.request_error_handler(re, 'create_bucket', method, url,
                                       response, bucket=bucket_name)

        return bucket

    def get_bucket(self, bucket_name, validate=True):
        """
        Retrieves a bucket by name.

        If the bucket does not exist, an ``SS3_Request_error`` will be raised. If
        you are unsure if the bucket exists or not, you can use the
        ``S3Connection.lookup`` method, which will either return a valid bucket
        or ``None``.

        :type bucket_name: string
        :param bucket_name: The name of the bucket

        :type validate: boolean
        :param validate: If True, it will try to verify the bucket exists
                        on the service-side. (Default: False)
        """
        method = "GET"
        url = "buckets"
        bucket = None
        response, content = self.make_request(method, url, bucket=bucket_name)
        try:
            utils.check_response(response)
            data = json.loads(content)
            real_name = self._get_real_name(data)
            bucket = self.bucket_class(self, bucket_name, real_name)
        except request_error as re:
            if not validate is True:
                self.request_error_handler(re, 'get_bucket', method, url,
                                           response, bucket=bucket_name)
            bucket = self.bucket_class(self, bucket_name)

        return bucket

    def generate_url(self):
        return self._generate_path('groups', group_key=self.group_key)

    def lookup(self, bucket_name, validate=False):
        """
        Attempts to get a bucket from S3.

        Works identically to ``SSGConnection.get_bucket``, save for that it
        will return ``None`` if the bucket does not exist instead of throwing
        an exception.

        :type bucket_name: string
        :param bucket_name: The name of the bucket

        :type validate: boolean
        :param validate: If True, it will try to verify the bucket exists
                        on the service-side. (Default: False)
        """
        try:
            bucket = self.get_bucket(bucket_name, False)
        except request_error:
            return None

        return bucket

    def make_request(self, method, url='', bucket='', key='', group_key='',
                     query='', headers=None, body=None, file_io=False):
        """
        handling request_error and printing where error occurs and request type.

        :type method: str
        :param method: method that SDK requests to server.

        :type url: str
        :param url: indicates what SDK target class is.

        :type bucket: str
        :param bucket: user's bucket name

        :type key: str
        :param key: user's key name

        :type group_key: str
        :param group_key: user's private group_key that was provided by server
                        before making bucket

        :type body: list
        :param body: Http body

        :type file_io: bool
        :param file_io:

        :rtype: httplib2.response
        :return: server response for request

        """
        request_body = None
        request_header = dict()
        http = httplib2.Http()

        if file_io is True:
            pass
        else:
            url = self._generate_path(url, bucket, key, group_key, query)

            request_header.update(self.header)
            if not (headers is None):
                request_header.update(headers)

            if not None == body:
                request_body = json.dumps(body)
        print url
        return http.request(url, method, request_body, request_header)

    @property
    def header(self):
        self._header = {
            'Accept': 'application/json',
            'Content-type': 'application/json; charset=UTF-8',
            }
        if not (self.auth_token is None):
            self._header.update({'Authorization': self.auth_token})
        return self._header

    @property
    def host(self):
        self._host = "54.238.232.210"
        return self._host

    @property
    def port(self):
        self._port = "80"
        return self._port

    def set_bucket_class(self, bucket_class):
        """
        Set the Bucket class associated with this bucket.  By default, this
        would be the boto.s3.key.Bucket class but if you want to subclass that
        for some reason this allows you to associate your new class.

        :type bucket_class: class
        :param bucket_class: A subclass of Bucket that can be more specific
        """
        self.bucket_class = bucket_class

    def _get_real_name(self, response_data):
        real_name = response_data['real_name']
        return real_name

    def _generate_path(self, url, bucket='', key='', group_key='', query=''):
        path = 'http://'+str(self.host)+':'+str(self.port)+'/'+str(url)

        if not group_key == '':
            path = path+'/'+group_key

        if not bucket == '':
            path = path+'/'+quote(bucket)

            if not key == '':
                path = path+'/key?path='+quote(key)

        if not query == '':
            path = path + query

        print 'in _generate_path : '+path
        return path

    def _set_token(self, response_data):
        self.auth_token = 'token '+str(response_data['token'])
        #self.owner = data['id']

    def _make_bucket_list(self, content):
        response_bucket_list = utils.make_select_list(content, 'name')
        bucket_list = list()

        for b in response_bucket_list:
            bucket_list.append(SSGBucket(self, b))

        return bucket_list

    def request_error_handler(self, re, func, method, url, response, **kwarg):
        """
        handling request_error and printing where error occurs and request type.

        :type re: str
        :param re: notice what error_class is called.

        :type func: str
        :param func: function name where occurred error.

        :type method: str
        :param method: method that SDK requests to server.

        :type url: str
        :param url: indicates what SDK target class is.

        :type response: httplib2.response.
        :param response: response of request.

        :type **kwarg: dict
        :param **kwarg: including path.

        """
        bucket = ''
        key = ''
        group_key = ''
        query = ''

        if 'group_key' in kwarg:
            group_key = kwarg('group_key')
        elif 'bucket' in kwarg:
            bucket = kwarg['bucket']
            if 'key' in kwarg:
                key = kwarg['key']
        if 'query' in kwarg:
            query = kwarg['query']

        request_url = self._generate_path(url, bucket=bucket, key=key, group_key=group_key, query=query)
        print ''
        print traceback.format_exc().strip()
        logs.func_info(re.error, function=func, msg='fails to '+func)
        logs.response_info(method, request_url, response)
        exit()