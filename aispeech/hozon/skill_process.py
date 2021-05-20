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

skill_id = "2018053100000019"

jsob = json.loads(open("%s_tasks.json" % skill_id).read())

def remove_info(obj):
    obj.pop('slots')
    for intent in obj.get('intents', []):
        intent.pop('utterances')
        intent.pop('slots')

map(remove_info, jsob.get('tasks', []))

open('%s_tmp.json' % skill_id, 'w').write(json.dumps(jsob, ensure_ascii=False))

def process_output(output):
    output['itemsPerPage'] = 3
    output['totalPages'] = 3
    if "command" == output.get('resource', ''):
        output['resource'] = 'native'
    elif "webhook" == output.get('resource', ''):
        location = output.get('location', '')
        output['location'] = location.replace('v2/lyra/webhook', 'eis/hz/api').replace('lyra/webhook', 'eis/hz/api')
        print output['location']
    for resp in output['responses']:
        condition_type = resp['condition'][0]['type']
        if 'greater' == condition_type:
            resp['condition'][0]['type'] = 'greaterThan'
        elif 'ne' == condition_type:
            resp['condition'][0]['type'] = 'notEqual'
        elif 'ge' == condition_type:
            resp['condition'][0]['type'] = 'greaterThanOrEqual'
        elif 'required' == condition_type:
            resp['condition'][0]['type'] = 'miss'

def make_dm(obj):
    task = obj['name']
    dm_task = {}
    for intent in obj['intents']:
        process_output(intent.get('output', {}))
        dm_task[intent['name']] = {'input':intent.get('input', []), 'output':intent.get('output', {}), 'error':intent.get('error', {})}
        
    return (task, dm_task)

def make_skill_dm(obj):
    dm_tasks = {}
    for dm in map(make_dm, jsob.get('tasks', [])):
        dm_tasks[dm[0]] = dm[1]
    open('skill-dm-%s.json' % skill_id, 'w').write(json.dumps({'tasks':dm_tasks, 'config':{'isFallback':False}}, ensure_ascii=False))

make_skill_dm(jsob)

print 'OK'
