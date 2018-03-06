#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 2018年3月5日

@author: XuMaosen
'''

import jieba  
import jieba.analyse as analyse
jieba.enable_parallel(4)
import json

def getWords(content):  
    # 去除停用词  
    stopkey = [line.strip().decode('utf-8').encode('gbk') for line in open('stopkey.txt').readlines()]  
    stopkey = {}.fromkeys(stopkey)  
    segs = jieba.cut(content, cut_all=False)  
    final = ''  
    for seg in segs:  
        seg = seg.strip().encode('gbk')  
        if seg not in stopkey and len(seg) > 0:  
            final += seg  
            final += ' '  
    return final

issues = json.loads(open('issues.json').read())
content = reduce(lambda x, y:x + '\n' + y, map(lambda x:str(x['details']), issues))
final = getWords(content) 

keywords = []
for key in analyse.extract_tags(final, 50, withWeight=True):
    keywords.append(key)

for tag, weight in keywords:
    print tag, weight
