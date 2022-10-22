#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 2019年3月2日

@author: XuMaosen
'''
import HTMLTestRunner
import unittest
import requests
import os
import json
import uuid
from functools import reduce
from basetest import ProductBaseTest, catch_exception
from multiprocessing.pool import Pool
    
# 天琴产品测试    
class LyraProductTest(ProductBaseTest):
    _productId = 279606354
    _versionId = 149158
    _user_cookies = None
    # 开启异常捕获
    _exception_switch = True
    
    def __init__(self, methodName, filepath, user_cookies):
        ProductBaseTest.__init__(self, methodName)
        self.filepath = filepath
        self.user_cookies = user_cookies
    
    @catch_exception(exception_switch=_exception_switch)
    def process_input_word(self, input_word, contextId):
        index = input_word.find(',')
        body = {"versionId":self._versionId, "sentence":input_word[:index], "contextId":contextId}
        resp_json = self.execute_requests(body, self.user_cookies)
        if input_word.find('"') > 0:
            input_word = input_word[index + 2:-2].replace('""', '"')
        else:
            input_word = input_word[index + 1:]
        
        expect = json.loads(input_word)
        if len(expect.get('nlg')) > 0 and len(resp_json['data']['dm'].get('nlg')) > 0:
            for k in resp_json['data']['dm'].keys():
                if k not in ["nlg", "speak", "runSequence", "command", "intentName", "taskId", "intentId"]:
                    self.assertEqual(expect.get(k), resp_json['data']['dm'].get(k)) 
        elif len(expect.get('nlg')) == 0 and len(resp_json['data']['dm'].get('nlg')) == 0:
            for k in resp_json['data']['dm'].keys():
                if k not in ["nlg", "speak", "intentName", "taskId", "intentId"]:
                    self.assertEqual(expect.get(k), resp_json['data']['dm'].get(k))
        else:
            self.assertEqual(expect.get('nlg'), resp_json['data']['dm'].get('nlg'))
    
    # 测试集测试，单轮
    def test_statement_run(self):
        for input_word in open(self.filepath, encoding='utf-8').readlines():
            self.process_input_word(input_word, None)

    # 测试集测试，多轮
    def test_statement_run_multi(self):
        contextId = uuid.uuid4()
        for input_word in open(self.filepath, encoding='utf-8').readlines():
            if len(input_word) < 3:
                contextId = uuid.uuid4()
            else:
                self.process_input_word(input_word, contextId)
                
def suite(filepath, user_cookies):
    test_suite = unittest.TestSuite()  # 创建一个测试集合
    all_tests = [
                LyraProductTest('test_statement_run', filepath, user_cookies)
                 ]
    test_suite.addTests(all_tests)  # 测试套件中添加测试用例
    return test_suite
       
def split(fromfile, chunksize):
    partnum = 0
    str_lines = open(fromfile, encoding='utf-8').readlines()
    for i in range(0, len(str_lines), chunksize):
        partnum += 1
        filename = 'part%04d' % partnum
        fileobj = open(filename, 'w', encoding='utf-8')  # make partfile
        fileobj.write(reduce(lambda a, b:a + b, str_lines[i:i + chunksize]))  # write data into partfile
        fileobj.close()
    return partnum

def exec_runner(result_path, filepath, user_cookies):
    print(result_path)
    fp = open(result_path, 'w', encoding='utf-8')  # 打开一个保存结果的html文件
    runner = HTMLTestRunner.HTMLTestRunner(stream=fp, title='产品测试报告', description='测试情况')
    runner.run(suite(filepath, user_cookies))
       
if __name__ == '__main__':
    
    # 分割测试集文件，避免文件太大
    split(u'车控测试集.csv', 250)
    # 设置技能超时时间（秒）
    skill_timeout = 5
    userName = ''
    password = ''
    login_url = 'https://authentication.duiopen.com/account/accountLogin'
    # **********  userName和password必填 **************************  userName和password必填  *****************************
    body = {"userName":userName, "password":password, "captcha":"", "remem":False}
    resp = requests.post(login_url, json=body)
    if resp.status_code == 200 and resp.json().get('code') == '0':
        user_cookies = resp.cookies
        pool = Pool(2)
        for dirpath, dirnames, filenames in os.walk('./'):
            for filepath in filter(lambda f:f.startswith('part'), filenames):
                result_path = u'产品测试报告-%s.html' % filepath
                pool.apply_async(exec_runner, args=(result_path, os.path.join(dirpath, filepath), user_cookies))
        pool.close()
        pool.join()
    else:
        print('请检查　userName和password')
