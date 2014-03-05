#!/usr/bin/python
# -*- coding: utf-8 -*-


class ssg_exception(BaseException):
    def __init__(self):
        self.exception = 'ssg exception'


class request_error(ssg_exception):
    def __init__(self):
        self.error = 'request error'
