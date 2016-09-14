# -*- coding: utf-8 -*-

' a test module '

__author__ = 'Xu MaoSen'

# 导入:
from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base
import db
from SpecParam import SpecParam

# 创建对象的基类:
Base = declarative_base()

# 定义User对象:
class User(Base):
    # 表的名字:
    __tablename__ = 'test'

    # 表的结构:
    id = Column(String(20), primary_key = True)
    username = Column(String(20))
    password = Column(String(20))


# 创建新User对象:
new_user = User(id = 51, username = 'Bob', password = 'hehe')
new_user2 = User(id = 52, username = 'Bob', password = 'hehe')

# db.insert(new_user, new_user2)

spec = SpecParam(User)
spec.ne('id', '5')
# spec.like('password', 'B')
# spec.in_('id', 5, 7)
# spec.is_not_null('id')
 
# spec2 = SpecParam(User)
# spec2.eq('username', 'admin')
#  
# spec.or_(spec2)
 
for row in db.select(spec):
    print row.id, row.username, row.password
