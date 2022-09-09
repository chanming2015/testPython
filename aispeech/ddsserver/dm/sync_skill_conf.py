#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 2019年3月2日

@author: XuMaosen
'''

import requests
import json
import time
       
if __name__ == '__main__':
#     productIds = ['279609734', '279606354', '278582558', '279610639', '279610836', '279609887', '279610994', '279611322', '279613565']

    productIds = ['tryProductId']
    j = json.loads(open(u'C:/Users/Administrator/Desktop/长城车控技能配置.json', encoding='utf-8').read())

#     productIds = ['279611361']
#     j = json.loads(open(u'C:/Users/Administrator/Desktop/极氪车控技能配置.json', encoding='utf-8').read())
    
    skillIds = ['2022011900000133']
    for p in productIds:
        for s in skillIds:
            url = 'http://localhost:8080/v2/lyra/webhook/dsk/skill/dmconfig?productId=%s&skillId=%s' % (p, s)
            resp = requests.post(url, json=j)
            print(resp.status_code)
            time.sleep(1)
