#!/usr/bin/python
# -*- coding: utf-8 -*-
from os import path
from urllib2 import quote
import json

from ssg.common import utils
from ssg.common.exceptions import *


class SSGKey(object):
    """
    Represents a key (object) in an SSG bucket.

    :ivar bucket: The parent :class:`ssg.SSG.bucket.SSGBucket`.
    :ivar name: The name of this SSGKey object.
    :ivar filename: The name of file name.
    :ivar type: Indicating which type file is.
    :ivar modified_by: The ID of who changed last
    :ivar created_by: The ID of who created.
    :ivar owner: The ID of the owner of this object
    :ivar size: The size in bytes, total file size
    :ivar size_ssg: The size in bytes, of ssg file size
    :ivar size_s3: The size in bytes, of s3 file size
    :ivar url: The url that can access to this object
    :ivar policy: The policy that can access to this object
    :ivar AWSAccessKeyId: The Id of ssg access id.
    :ivar signature: The string of ssg storage authentication.
    :ivar key: The key of query param.
    :ivar x_amz_storage_class: The storage class of the object.
    :ivar real_name: The name of user s3 real key name.
    :ivar id: The value of user's PK.
    :ivar key_path: The path that user wants to upload location.
    """
    def __init__(self, bucket=None, name=None, real_name=None):
        self.bucket = bucket
        self.name = name

        self.filename = None
        self.filepath = None
        self.type = None
        self.modified_by = None
        self.created_by = None
        self.owned_by = None
        self.size = None
        self.size_ssg = None
        self.url = None

        #upload body
        self.policy = None
        self.AWSAccessKeyId = None
        self.signature = None
        self.key = None
        self.x_amz_storage_class = None

        #related with user_s3
        self.real_name = real_name
        self.size_s3 = None
        self.id = None

        self.key_path = self._make_key_path()

    def _make_key_path(self):
        key_path = utils.get_utf8_value(self.name)
        return key_path

    def _get_key(self):
        return self.name

    def _set_key(self, value):
        self.name = value

    def exists(self):
        """
        Returns True if the key exists

        :rtype: bool
        :return: Whether the key exists on SSG
        """
        return bool(self.bucket.lookup(self.name))

    def get_metadata(self):
        return self.__dict__

    def get_contents_to_filename(self, filename):
        """
        Retrieve an object from SSSG using the name of the Key object as the
        key in SSG. Write the contents of the object to the file name
        to by 'filename'.

        :type filename: string
        :param filename: The name of download file.
        """
        method = "GET"
        url = self.url
        response, content = self.bucket.connection.make_request(method, url, file_io=True)

        try:
            utils.check_response(response)
            with open(filename, 'wb') as f:
                f.write(content)
        except request_error as re:
            self.bucket.connection.request_error_handler(re, 'get_contents_to_filename',
                                                         method, url, response)

    def build_post_form_args(self, size_s3, size_ssg):
        """
        This only returns the arguments required for the post form, not the
        actual form.  This does not return the file input field which also
        needs to be added.

        using example : It generates upload url.

        :type size_s3: int
        :param size_s3: The size in bytes, of s3 file size

        :type size_ssg: int
        :param size_ssg: The size in bytes, of ssg file size

        :rtype: list
        :return: The args of post form. (header, body, url, finish response form)
        """
        self.set_contents_from_filename(size_s3=size_s3, size_ssg=size_ssg)
        query = "/key_finish?path="+quote(self.name)
        print "in build_post form : " + query
        ssg_list = list()
        body = dict()
        body['fields'] = [{'name': 'policy', 'value': self.policy},
                          {'name': 'AWSAccessKeyId', 'value': self.AWSAccessKeyId},
                          {'name': 'key', 'value': self.key},
                          {'name': 'signature', 'value': self.signature},
                          {'name': 'x_amz_storage_class', 'value': self.x_amz_storage_class}]
        url = dict()
        url['action'] = self.url
        finish_response = dict()
        finish_response['finish_response'] = {'method': 'POST',
                                              'action': "http://54.238.232.210/bucket/"+self.bucket.name+query,
                                              'fields': [{'name': "storage_path_s3", 'value': self.real_name},
                                                         {'name': "bucket_s3", 'value': self.bucket.real_name}]}
        ssg_list.append(body)
        ssg_list.append(url)
        ssg_list.append(finish_response)
        return ssg_list

    def set_contents_from_filename(self, filename=None, size_s3=None, size_ssg=None):
        """
        Store an object in SSG using the name of the Key object as the
        key in SSG.

        :type filename: string
        :param filename: The path of upload file.

        :type size_s3: int
        :param size_s3: The size in bytes, of s3 file size

        :type size_ssg: int
        :param size_ssg: The size in bytes, of ssg file size

        :rtype: int
        :return: The number of bytes written to the key.
        """
        method = "POST"
        url = "buckets"
        self.filepath = filename
        if self.filepath is None:
            self.size_ssg = size_ssg
        else:
            self.size_ssg = path.getsize(self.filepath)
        self.size_s3 = size_s3
        self.size = self.size_s3 + self.size_ssg
        self.filename = filename
        request_param = {'name': self.name, 'size': self.size,
                         'size_s3': self.size_s3, 'size_ssg': self.size_ssg}

        response, content = self.bucket.connection.make_request(method, url,
                                                                bucket=self.bucket.name,
                                                                key=self.name,
                                                                body=request_param)
        try:
            utils.check_response(response)
            self.set_metadata(content)

        except request_error as re:
            self.bucket.connection.request_error_handler(re, 'set_contents_from_filename',
                                                         method, url, response,
                                                         bucket=self.bucket.name, key=self.name)
        return self.size_ssg

    def send_file(self):
        """
        Upload a file to a key into a bucket on SSG.
        If success to upload, It must calls finish response and update data base.
        """
        parameters = {'AWSAccessKeyId': self.AWSAccessKeyId, 'policy': self.policy,
                      'key': self.key, 'signature': self.signature,
                      'x-amz-storage-class': self.x_amz_storage_class}

        self._send_file_internal(parameters)
        self._finish_response()

    def generate_url(self):
        """
        Generate a URL to access this key.

        :rtype: string
        :return: The URL to access the key
        """
        return self.url

    def delete(self):
        """
        Delete this key from S3
        """
        method = "DELETE"
        url = "buckets"

        response, content = self.bucket.connection.make_request(method, url,
                                                                bucket=self.bucket.name,
                                                                key=self.name)
        try:
            utils.check_response(response)

        except request_error as re:
            self.bucket.connection.request_error_handler(re, 'delete_key',
                                                         method, url, response,
                                                         bucket=self.bucket.name, key=self.name)

    def set_metadata(self, content):
        data = json.loads(content)
        return self._set_metadata_internal(data)

    def _set_metadata_internal(self, metadata):
        self.id = metadata['id']
        self.created_by = metadata['created_by']
        self.modified_by = metadata['modified_by']
        self.owned_by = metadata['owned_by']
        self.real_name = metadata['storage_path_ssg']
        #self.name = metadata['path']
        #print "in set_metadata_internal : " + self.name

        upload_info = metadata['upload_info']
        self.policy = upload_info['policy']
        self.AWSAccessKeyId = upload_info['AWSAccessKeyId']
        self.key = upload_info['key']
        self.signature = upload_info['signature']
        self.x_amz_storage_class = upload_info['x-amz-storage-class']
        self.url = upload_info['upload_url']

    def _finish_response(self):
        method = "POST"
        url = "buckets"
        bucket_name = self.bucket.name
        query = "/key_finish?path="+quote(self.name)

        request_param = {"storage_path_s3": self.real_name, "bucket_s3": self.bucket.real_name}
        response, content = self.bucket.connection.make_request(method, url, body=request_param,
                                                                bucket=bucket_name, query=query)
        try:
            utils.check_response(response)
            data = json.loads(content)
            #데이터 형식 확인 후 key_list return
            print 'data : ' + str(data)

        except request_error as re:
            self.bucket.connection.request_error_handler(re, 'finish_response', method, url,
                                                         response, bucket=bucket_name, query=query)
        return True

    def _send_file_internal(self, parameters):
        import pycurl

        c = pycurl.Curl()
        c.setopt(c.POST, 1)

        c.setopt(c.URL, str(self.url))
        c.setopt(c.FOLLOWLOCATION, 1)
        c.setopt(c.MAXREDIRS, 3)

        values = []

        for k, v in parameters.iteritems():
            if isinstance(k, unicode):
                k = k.encode("utf-8")
            if isinstance(v, unicode):
                v = v.encode("utf-8")
            values.append((k, v))

        values.append(("file", (pycurl.FORM_FILE, self.filepath)))
        print values
        c.setopt(c.HTTPPOST, values)
        c.setopt(c.SSL_VERIFYHOST, False)
        c.setopt(c.SSL_VERIFYPEER, False)
        c.perform()
        c.close()
