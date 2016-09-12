#!/usr/bin/env python
# -*- coding: utf-8 -*-

' a test module '

__author__ = 'Xu MaoSen'

print [x * x for x in range(1, 11) if x % 2 == 0]

g = (x * x for x in range(1, 11) if x % 2 == 0)
print g.next()


def f(x):
    return x * x

print map(f, range(5))

def fn(x, y):
    return x * 10 + y

print reduce(fn, range(5))

def is_odd(n):
    return n % 2 == 1

print filter(is_odd, range(10))

print map(lambda x: x * x, range(10))

import functools

def log(func):
    @functools.wraps(func)
    def wrapper(*args, **kw):
        print 'call %s():' % func.__name__
        return func(*args, **kw)
    return wrapper

@log
def test_log():
    print 'test_log'

test_log()

int2 = functools.partial(int, base=2)
print int2('1000000')

