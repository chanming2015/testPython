#!/usr/bin/env python
# -*- coding: utf-8 -*-

' a test module '

__author__ = 'Xu MaoSen'

from sqlalchemy.ext.declarative.api import DeclarativeMeta
from collections import namedtuple

criterions = namedtuple('criterions', ['key', 'op', 'value'])

class SpecParam(object):
    
    def __init__(self, mapping_type):
        if not isinstance(mapping_type, (DeclarativeMeta,)):
            raise TypeError('type should be sqlalchemy.ext.declarative.api.DeclarativeMeta')
        self.__mapping_type = mapping_type
        self.__criterions = {}
        
    def get_mapping_type(self):
        return self.__mapping_type
    
    def get_criterions(self):
        return self.__criterions.values()
    
    def eq(self, key, value):
        self.__criterions[key] = criterions(key, 'eq', value)
        return self
    
    def like(self, key, value):
        self.__criterions[key] = criterions(key, 'like', value)
        return self
    
    def in_(self, key, *value):
        self.__criterions[key] = criterions(key, 'in_', value)
        return self
    