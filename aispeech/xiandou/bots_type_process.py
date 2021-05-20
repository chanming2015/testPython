#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 2018年3月28日

@author: XuMaosen
'''
    
import json
import sys
reload(sys) 
sys.setdefaultencoding('utf8')

lines = open('data.txt').readlines()

all_skill_json = {}

for line in lines:
    datas = line.split('\t')
    if len(datas[0]) > 2:
        current_skill_id = datas[0]
        expression = datas[2]
        bots = datas[3]
        domain = datas[4]
        intent = datas[5]
        condition = {"expression":expression, "bots":bots, "domain":domain, "intent":intent} if len(bots) > 0 else {"expression":expression, "domain":domain, "intent":intent}
        conditions = [condition]
        # 加载默认配置
        default_entrylist = datas[6]
        current_skill_json = {}
        current_skill_json['conditions'] = conditions
        if len(default_entrylist) > 2:
            current_skill_json['entrylist'] = json.loads(default_entrylist)
        # 加载特殊配置
        extra_entrylist = datas[7]
        if len(extra_entrylist) > 2:
            condition['entrylist'] = json.loads(extra_entrylist)
        all_skill_json[current_skill_id] = current_skill_json
    else:
        expression = datas[2]
        bots = datas[3] if len(datas[3]) > 0 else bots
        domain = datas[4] if len(datas[4]) > 0 else domain
        intent = datas[5]
        condition = {"expression":expression, "bots":bots, "domain":domain, "intent":intent} if len(bots) > 0 else {"expression":expression, "domain":domain, "intent":intent}
        # 加载特殊配置
        extra_entrylist = datas[7]
        if len(extra_entrylist) > 2:
            condition['entrylist'] = json.loads(extra_entrylist)
        conditions.append(condition)


open('bots_type.json', 'w').write(json.dumps(all_skill_json, ensure_ascii=False))
print 'OK'
