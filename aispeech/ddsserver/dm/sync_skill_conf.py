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
    
#     productIds = ['279613689']
#     j = json.loads(open(u'C:/Users/Administrator/Desktop/车控配置/长城B07车控技能配置.json', encoding='utf-8').read())

#     '279615447', '279616508', '279617983', '279609734'
#     productIds = ['279606354']
#     j = json.loads(open(u'C:/Users/Administrator/Desktop/车控配置/长城车控技能配置.json', encoding='utf-8').read())
#  
#     '279617235', '279619444'
#     productIds = ['279611361']
#     j = json.loads(open(u'C:/Users/Administrator/Desktop/车控配置/极氪车控技能配置.json', encoding='utf-8').read())
# 
#     '279613565'
#     productIds = ['279611322']
#     j = json.loads(open(u'C:/Users/Administrator/Desktop/车控配置/北汽车控技能配置.json', encoding='utf-8').read())
 
#     productIds = ['279610994']
#     j = json.loads(open(u'C:/Users/Administrator/Desktop/车控配置/洛轲车控技能配置.json', encoding='utf-8').read())
     
#     '279617180', '279617183'
#     productIds = ['279614268']
#     j = json.loads(open(u'C:/Users/Administrator/Desktop/车控配置/比亚迪车控技能配置.json', encoding='utf-8').read())

#     productIds = ['279617351']
#     j = json.loads(open(u'C:/Users/Administrator/Desktop/车控配置/吉利车控技能配置.json', encoding='utf-8').read())
    
#     productIds = ['279618863']
#     j = json.loads(open(u'C:/Users/Administrator/Desktop/车控配置/奔驰车控技能配置.json', encoding='utf-8').read())
    
    productIds = ['tryProductId']
    j = json.loads(open(u'C:/Users/Administrator/Desktop/车控配置/公版车控技能配置.json', encoding='utf-8').read())

     
    skillIds = ['2022011900000133']
    for p in productIds:
        for s in skillIds:
#             url = 'http://apis.beta.dui.ai/v2/lyra/webhook/dsk/skill/dmconfig?productId=%s&skillId=%s' % (p, s)
#             print(url)
#             resp = requests.post(url, json=j)
#             print(resp.status_code)
#             time.sleep(1)
#                               
#             url = 'http://apis.dui.ai/v2/lyra/webhook/dsk/skill/dmconfig/sync?productId=%s&skillId=%s' % (p, s)
#             print(url)
#             resp = requests.post(url)
#             print(resp.status_code)
#             time.sleep(1)

    
