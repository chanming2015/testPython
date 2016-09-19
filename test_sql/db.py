# !/usr/bin/env python
# -*- coding: utf-8 -*-

' a test module '
__author__ = 'Xu MaoSen'

# 导入:
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker
import threading

# 数据库引擎对象:
engine = create_engine('mysql://root:458710@127.0.0.1:3306/test')
# 创建DBSession类型:
DBSession = sessionmaker(bind = engine)

# 持有数据库连接的上下文对象:
class _DbCtx(threading.local):
    def __init__(self):
        self.__session = None

    def is_init(self):
        return not self.__session is None

    def init(self):
        self.__session = DBSession()

    def cleanup(self, should_commit):
        if should_commit:
            self.__session.commit()
        self.__session.close()
        self.__session = None

    def session(self):
        return self.__session

_db_ctx = _DbCtx()

class _SessionCtx(object):
    
    def __init__(self, should_commit):
        self.__should_cleanup = False
        self.__should_commit = should_commit
    
    def __enter__(self):
        if not _db_ctx.is_init():
            _db_ctx.init()
            self.__should_cleanup = True
        return self

    def __exit__(self, exctype, excvalue, traceback):
        if self.__should_cleanup:
            _db_ctx.cleanup(self.__should_commit)

def session(should_commit):
    return _SessionCtx(should_commit)

import functools
from SpecParam import SpecParam

def with_session(should_commit = False):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            with session(should_commit):
                return func(*args, **kw)
        return wrapper
    return decorator

@with_session()
def select(spec, limit = None, offset = None):
    if not isinstance(spec, SpecParam):
            raise TypeError('type should be SpecParam')
    
    query = _db_ctx.session().query(*spec.get_query_types())
    
    and_criterions = spec.get_and_criterions()
    if len(and_criterions) > 0:
        query = query.filter(*and_criterions)
        
    or_criterions = spec.get_or_criterions()
    if len(or_criterions) > 0:
        query = query.filter(or_(*or_criterions))
    
    order_by_key = spec.get_order_by()
    if len(order_by_key) > 0:
        query = query.order_by(*spec.get_order_by())
    
    if isinstance(limit, int):
        query = query.limit(limit)
        
    if isinstance(offset, int):
        query = query.offset(offset)
        
    print query
    return query

@with_session(True)
def insert(*entitys):
    return _db_ctx.session().add_all(entitys)

@with_session(True)
def delete(entity):
    return _db_ctx.session().delete(entity)

@with_session(True)
def update(entity):
    return _db_ctx.session().add(entity)
