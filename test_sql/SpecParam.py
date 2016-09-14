# !/usr/bin/env python
# -*- coding: utf-8 -*-

' a test module '

__author__ = 'Xu MaoSen'

from sqlalchemy.ext.declarative.api import DeclarativeMeta
from collections import namedtuple

criterions = namedtuple('criterions', ['key', 'op', 'value'])

import functools
def check_key(func):
    @functools.wraps(func)
    def wrapper(*args, **kw):
        if not isinstance(args[1], str):
            raise TypeError('type should be str')
        return func(*args, **kw)
    return wrapper

class SpecParam(object):
    
    def __init__(self, mapping_type):
        if not isinstance(mapping_type, (DeclarativeMeta,)):
            raise TypeError('type should be sqlalchemy.ext.declarative.api.DeclarativeMeta')
        self.__mapping_type = mapping_type
        self.__and_criterions = {}
        self.__or_specs = []
        
    def get_mapping_type(self):
        return self.__mapping_type
    
    def get_and_criterions(self):
        return self.__and_criterions.values()
    
    def get_or_specs(self):
        return self.__or_specs
    
    @check_key
    def eq(self, key, value):
        self.__and_criterions[key] = criterions(key, 'eq', value)
        return self
    
    @check_key
    def ne(self, key, value):
        self.__and_criterions[key] = criterions(key, 'ne', value)
        return self
    
    def like(self, key, value):
        self.__and_criterions[key] = criterions(key, 'like', value)
        return self
    
    @check_key
    def in_(self, key, *value):
        self.__and_criterions[key] = criterions(key, 'in_', value)
        return self
    
    @check_key
    def not_in(self, key, *value):
        self.__and_criterions[key] = criterions(key, 'not_in', value)
        return self
    
    @check_key
    def is_null(self, key):
        self.__and_criterions[key] = criterions(key, 'eq', None)
        return self
    
    @check_key
    def is_not_null(self, key):
        self.__and_criterions[key] = criterions(key, 'ne', None)
        return self
    
    def or_(self, other_spec):
        if not isinstance(other_spec, SpecParam):
            raise TypeError('type should be SpecParam')
        self.__or_specs.append(other_spec)
