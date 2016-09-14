#!/usr/bin/env python
# -*- coding: utf-8 -*-

' a test module '

__author__ = 'Xu MaoSen'

import logging
logging.basicConfig(level = logging.DEBUG)

from bottle import route, run, template

@route('/hello/<name>')
def index(name):
    return template('<b>Hello {{name}}</b>!', name = name)

run(host = 'localhost', port = 8080)
