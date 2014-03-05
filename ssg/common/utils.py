#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
from exceptions import request_error


def get_utf8_value(value):
    if not isinstance(value, basestring):
        value = str(value)
    if isinstance(value, unicode):
        return value.encode('utf-8')
    else:
        return value


def make_select_list(content, *args):
    pick_list = []
    data = json.loads(content)
    print type(data)
    if isinstance(data, list):
        for d in data:
            for a in args:
                pick_list.append(d[a])

    elif isinstance(data, dict):
        for a in args:
            print a
            pick_list.append(data[a])

    return pick_list


def make_select_dict(response, *args):
    # data_dict = dict()
    # data = response
    # print data
    #
    # for q in args:
    #     print "eeee"+data[q]
    # return data_dict
    pass


def check_response(response):
    error_check = 300
    if not response.status < error_check:
        raise request_error
    else:
        return True