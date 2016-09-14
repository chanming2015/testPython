# !/usr/bin/env python
# -*- coding: utf-8 -*-

' a test module '
__author__ = 'Xu MaoSen'

# 导入:
from sqlalchemy import create_engine
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
def select(spec):
    if not isinstance(spec, SpecParam):
            raise TypeError('type should be SpecParam')
    
    query_types = []
    
    if len(spec.get_query_types()) > 0:
        for key in spec.get_query_types():
            query_types.append(getattr(spec.get_mapping_type(), key))
    else:
        query_types.append(spec.get_mapping_type())
    
    if len(query_types) == 1:
        query = _db_ctx.session().query(query_types[0])
    elif len(query_types) == 2:
        query = _db_ctx.session().query(query_types[0], query_types[1])
    elif len(query_types) == 3:
        query = _db_ctx.session().query(query_types[0], query_types[1], query_types[2])
    elif len(query_types) == 4:
        query = _db_ctx.session().query(query_types[0], query_types[1], query_types[2], query_types[3])
    elif len(query_types) == 5:
        query = _db_ctx.session().query(query_types[0], query_types[1], query_types[2], query_types[3], query_types[4])
    
    # process and criterions
    for index in spec.get_and_criterions():
        key = index.key
        op = index.op
        value = index.value
        if op == 'eq':
            query = query.filter(getattr(spec.get_mapping_type(), key) == value)
        elif op == 'ne':
            query = query.filter(getattr(spec.get_mapping_type(), key) != value)
        elif op == 'like':
            query = query.filter(getattr(spec.get_mapping_type(), key).like('%' + value + '%'))
        elif op == 'in_':
            query = query.filter(getattr(spec.get_mapping_type(), key).in_(value))
        elif op == 'not_in':
            query = query.filter(~getattr(spec.get_mapping_type(), key).in_(value))
        else:
            pass
    
    # process or criterions if have
#    for index in spec.get_or_specs():
#        query = query.filter(or_(index))
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
