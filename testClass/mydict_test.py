#!/usr/bin/env python
# -*- coding: utf-8 -*-

' a test module '

__author__ = 'Xu MaoSen'

import logging
logging.basicConfig(level = logging.DEBUG)

import unittest

from mydict import Dict

class TestDict(unittest.TestCase):

    def setUp(self):
        self.__d = Dict()
    
    def test_init(self):
        d = Dict(a = 1, b = 'test')
        self.assertEquals(d.a, 1)
        self.assertEquals(d.b, 'test')
        self.assertTrue(isinstance(d, dict))

    def test_key(self):
        self.__d['key'] = 'value'
        self.assertEquals(self.__d.key, 'value')

    def test_attr(self):
        self.__d.key = 'value'
        self.assertTrue('key' in self.__d)
        self.assertEquals(self.__d['key'], 'value')

    def test_keyerror(self):
        with self.assertRaises(KeyError):
            value = self.__d['empty']

    def test_attrerror(self):
        with self.assertRaises(AttributeError):
            value = self.__d.empty
            
    def tearDown(self):
        logging.debug('tearDown...')