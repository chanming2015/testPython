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
            raise TypeError('key should be str')
        return func(*args, **kw)
    return wrapper

class SpecParam(object):
    
    def __init__(self, mapping_type, *query_types):
        if not isinstance(mapping_type, (DeclarativeMeta)):
            raise TypeError('mapping_type should be sqlalchemy.ext.declarative.api.DeclarativeMeta')
        
        self.__mapping_type = mapping_type
        self.__query_types = []
        if len(query_types) > 0:
            for key in query_types:
                if not isinstance(key, str):
                    raise TypeError('key should be str')
                self.__query_types.append(getattr(mapping_type, key))
        else:
            self.__query_types.append(mapping_type)
        
        
        self.__and_criterions = {}
        self.__or_spec = None
        self.__order_by = None
        
    def get_query_types(self):
        return self.__query_types
    
    def get_and_criterions(self):
        criterions = []
        for index in self.__and_criterions.values():
            key = index.key
            op = index.op
            value = index.value
            if op == 'eq':
                criterions.append(getattr(self.__mapping_type, key) == value)
            elif op == 'ne':
                criterions.append(getattr(self.__mapping_type, key) != value)
            elif op == 'like':
                criterions.append(getattr(self.__mapping_type, key).like('%' + value + '%'))
            elif op == 'in_':
                criterions.append(getattr(self.__mapping_type, key).in_(value))
            elif op == 'not_in':
                criterions.append(~getattr(self.__mapping_type, key).in_(value))
            else:
                pass
    
        return criterions

    def get_or_criterions(self):
        criterions = []
        if self.__or_spec:
            criterions = self.__or_spec.get_and_criterions()
        return criterions
    
    def get_order_by(self):
        keys = []
        if self.__order_by:
            for index in self.__order_by:
                keys.append(getattr(self.__mapping_type, index))
        return keys
           
    @check_key
    def eq(self, key, value):
        self.__and_criterions[key] = criterions(key, 'eq', value)
        return self
    
    @check_key
    def ne(self, key, value):
        self.__and_criterions[key] = criterions(key, 'ne', value)
        return self
    
    @check_key
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
    
    def or_(self):
        if not self.__or_spec:
            self.__or_spec = SpecParam(self.__mapping_type)
        return self.__or_spec
    
    @check_key
    def order_by(self, *key):
        self.__order_by = key
        return self
