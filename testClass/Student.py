#!/usr/bin/env python
# -*- coding: utf-8 -*-

' a test module '

__author__ = 'Xu MaoSen'

import logging
logging.basicConfig(level = logging.DEBUG)

import json

from types import MethodType

class Student(object):

    def __init__(self, name, score):
        self.__name = name
        self.__score = score
    @property
    def name(self):
        return self.__name
    @property
    def score(self):
        return self.__score
    @score.setter
    def score(self, value):
        if not isinstance(value, int):
            raise ValueError('score must be an integer!')
        if value < 0 or value > 100:
            raise ValueError('score must between 0 ~ 100!')
        self.__score = value
    def __str__(self):
        return 'Student object (name: %s)' % self.__name
    
s = Student('hehe', '100')
logging.debug('%s: %s' % (s.name, s.score))

s.score = 50
logging.debug(s.score)

s.value = 'aa'  # 动态给实例绑定一个属性
logging.debug(s.value)

def set_age(self, age):  # 定义一个函数作为实例方法
    self.age = age
    
Student.set_age = MethodType(set_age, None, Student)
s.set_age('18')
logging.debug(s.age)

logging.debug(s)

logging.debug(json.dumps(s, default = lambda obj: obj.__dict__))