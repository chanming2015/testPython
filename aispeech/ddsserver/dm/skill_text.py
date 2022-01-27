#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 2019年3月2日

@author: XuMaosen
'''
import HTMLTestRunner
import unittest
import requests
import sys, os
from basetest import SkillBaseTest, catch_exception
reload(sys)
sys.setdefaultencoding('utf-8')
from multiprocessing import Pool

# 车载控制技能测试    
class LyraCarCtlSkillTest(SkillBaseTest):
    _skill_id = 2022011900000133
    _skill_version = 'latest'
    # 开启异常捕获
    _exception_switch = True
    
    def __init__(self, methodName, filepath, user_cookies):
        SkillBaseTest.__init__(self, methodName)
        self.filepath = filepath
        self.user_cookies = user_cookies

    @catch_exception(exception_switch=_exception_switch)
    def execute_requests_cmd(self, input_word, user_cookies, contextId=None):
        resp_json = self.execute_requests(input_word, user_cookies, contextId)
        self.assertIsNotNone(resp_json['data']['dm'].get('command'))
        self.assertEqual(resp_json['data']['dm']['nlg'], '')
    
    @catch_exception(exception_switch=_exception_switch)
    def execute_requests_nlg(self, input_word, user_cookies, contextId=None):
        resp_json = self.execute_requests(input_word, user_cookies, contextId)
        self.assertIsNone(resp_json['data']['dm'].get('command'))
        self.assertNotEqual(resp_json['data']['dm']['nlg'], '')
    
    # 说法集测试
    def test_statement_run(self):
        for input_word in open(self.filepath).readlines():
            if input_word.find('TTS') > 0:
                input_word = input_word[0:input_word.find('==》')]
                for strinw in input_word.split('/'):
                    self.execute_requests_nlg(strinw, self.user_cookies)
            else:
                for strinw in input_word.split('/'):
                    self.execute_requests_cmd(strinw, self.user_cookies)
        
def suite(filepath, user_cookies):
    test_suite = unittest.TestSuite()  # 创建一个测试集合
    all_tests = [
                LyraCarCtlSkillTest('test_statement_run', filepath, user_cookies)
                 ]
    test_suite.addTests(all_tests)  # 测试套件中添加测试用例
    return test_suite
       
def split(fromfile, chunksize):
    partnum = 0
    str_lines = open(fromfile).readlines()
    for i in range(0, len(str_lines), chunksize):
        partnum += 1
        filename = 'part%04d' % partnum
        fileobj = open(filename, 'wb')  # make partfile
        fileobj.write(reduce(lambda a, b:a + b, str_lines[i:i + chunksize]))  # write data into partfile
        fileobj.close()
    return partnum

def exec_runner(result_path, filepath, user_cookies):
    print result_path
    fp = open(result_path, 'wb')  # 打开一个保存结果的html文件
    runner = HTMLTestRunner.HTMLTestRunner(stream=fp, title='产品测试报告', description='测试情况')
    runner.run(suite(filepath, user_cookies))
       
if __name__ == '__main__':
    
    # 分割说法集文件，避免文件太大,默认五千行一个文件
    split(u'全部说法集.txt', 100)
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
        pool = Pool(4)
        for dirpath, dirnames, filenames in os.walk('./'):
            for filepath in filter(lambda f:f.startswith('part'), filenames):
                result_path = u'产品测试报告-%s.html' % filepath
                pool.apply_async(exec_runner, args=(result_path, os.path.join(dirpath, filepath), user_cookies))
        pool.close()
        pool.join()
    else:
        print '请检查　userName和password'
