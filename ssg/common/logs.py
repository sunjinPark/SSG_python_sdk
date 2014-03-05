#!/usr/bin/python
# -*- coding: utf-8 -*-


def func_info(status, **kwargs):
    for key in kwargs:
        print key + ' : ' + kwargs[key]


def response_info(method, url, response):
    print method + '  ' + url
    print 'status : ' + str(response.status)
    print 'reason : ' + str(response.reason)
    print ''
