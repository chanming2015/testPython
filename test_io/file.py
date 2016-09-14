#!/usr/bin/env python
# -*- coding: utf-8 -*-

' a test module '

__author__ = 'Xu MaoSen'

import logging
logging.basicConfig(level = logging.DEBUG)

with open('../testClass/student.py', 'r') as f:
    logging.debug(f.read())

with open('./test.txt', 'w') as f:
    f.write('Hello, world!')