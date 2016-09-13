#!/usr/bin/env python
# -*- coding: utf-8 -*-

' a test module '
__author__ = 'Xu MaoSen'

# 导入:
from sqlalchemy import  create_engine
from sqlalchemy.orm import sessionmaker
import threading

# 数据库引擎对象:
engine = create_engine('mysql://root:458710@127.0.0.1:3306/test')
# 创建DBSession类型:
DBSession = sessionmaker(bind=engine)

# 持有数据库连接的上下文对象:
class _DbCtx(threading.local):
    def __init__(self):
        self.__session = None

    def is_init(self):
        return not self.__session is None

    def init(self):
        self.__session = DBSession(autocommit=True)

    def cleanup(self):
        self.__session.close()
        self.__session = None

    def session(self):
        return self.__session

_db_ctx = _DbCtx()

class _SessionCtx(object):
    def __enter__(self):
        self.should_cleanup = False
        if not _db_ctx.is_init():
            _db_ctx.init()
            self.should_cleanup = True
        return self

    def __exit__(self, exctype, excvalue, traceback):
        if self.should_cleanup:
            _db_ctx.cleanup()

def session():
    return _SessionCtx()

import functools
from SpecParam import SpecParam

def with_session(func):
    @functools.wraps(func)
    def wrapper(*args, **kw):
        with session():
            return func(*args, **kw)
    return wrapper

@with_session
def select(spec):
    if not isinstance(spec, SpecParam):
            raise TypeError('type should be SpecParam')
        
    query = _db_ctx.session().query(spec.get_mapping_type())
    
    for index in spec.get_criterions():
        key = index.key
        op = index.op
        value = index.value
        if op == 'eq':
            query = query.filter(getattr(spec.get_mapping_type(), key) == value)
        elif op == 'like':
            query = query.filter(getattr(spec.get_mapping_type(), key).like('%' + value + '%'))
        elif op == 'in_':
            query = query.filter(getattr(spec.get_mapping_type(), key).in_(value))
        else:
            pass
    print query
    return query

@with_session
def insert(entity):
    return _db_ctx.session().add(entity)

@with_session
def delete(entity):
    pass

@with_session
def update(entity):
    pass
