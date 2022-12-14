#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 2019年3月2日

@author: XuMaosen
'''
import unittest
import requests
import time
import json
from functools import reduce

def get_time():
    return time.strftime("%H:%M:%S", time.localtime())

def catch_exception(**kwds):
    def decorate(fn):
        def sayspam(*args):
            switch = kwds.get('exception_switch', False)
            if switch:
                result = None
                try:
                    result = fn(*args)
                except Exception as e:
                    print('Exception Happened: %s' % e)
                return result
            else:
                return fn(*args);
        return sayspam
    return decorate

class BaseTest(unittest.TestCase):
    # 异常捕获开关，默认关闭异常捕获，出错则测试停止
    _exception_switch = False
        
    # 包含判断
    @catch_exception(exception_switch=_exception_switch)
    def assertIn(self, member, container, msg=None):
        print(get_time(), 'assert if %s in (%s)' % (member, reduce(lambda x, y:'%s,%s' % (x, y), container)))
        unittest.TestCase.assertIn(self, member, container, msg);
    # 正则匹配判断
    @catch_exception(exception_switch=_exception_switch)
    def assertRegexpMatches(self, text, expected_regexp, msg=None):
        print(get_time(), 'assert if %s regexp %s' % (text, expected_regexp))
        unittest.TestCase.assertRegexpMatches(self, text, expected_regexp, msg)
    # 相等判断
    @catch_exception(exception_switch=_exception_switch)
    def assertEqual(self, first, second, msg=None):
        print(get_time(), 'assert if %s == %s' % (first, second))
        unittest.TestCase.assertEqual(self, first, second, msg)
    # 不相等判断
    @catch_exception(exception_switch=_exception_switch)
    def assertNotEqual(self, first, second, msg=None):
        print(get_time(), 'assert if %s != %s' % (first, second))
        unittest.TestCase.assertNotEqual(self, first, second, msg)
    # 类型判断
    @catch_exception(exception_switch=_exception_switch)
    def assertIsInstance(self, obj, cls, msg=None):
        print(get_time(), 'assert if %s isInstance %s' % (obj, cls))
        unittest.TestCase.assertIsInstance(self, obj, cls, msg)
    # 不存在判断
    @catch_exception(exception_switch=_exception_switch)
    def assertIsNone(self, obj, msg=None):
        print(get_time(), 'assert if %s isNone' % (obj))
        unittest.TestCase.assertIsNone(self, obj, msg)
    # 存在判断
    @catch_exception(exception_switch=_exception_switch)
    def assertIsNotNone(self, obj, msg=None):
        print(get_time(), 'assert if %s isNotNone' % (obj))
        unittest.TestCase.assertIsNotNone(self, obj, msg)
        
    def get_contextId(self, resp_json):
        return resp_json['data']['contextId']
    def assertSkill(self, resp_json, skill, msg=None):
        return self.assertEqual(resp_json['data']['nlu']['skill'], skill, msg)
    def assertSkillId(self, resp_json, skill_id, msg=None):
        return self.assertEqual(resp_json['data']['nlu']['skillId'], skill_id, msg)
    def assertSkillVersion(self, resp_json, skill_version, msg=None):
        return self.assertEqual(resp_json['data']['nlu']['skillVersion'], skill_version, msg)
    def assertIntent(self, resp_json, intent, msg=None):
        return self.assertEqual(resp_json['data']['dm']['intentName'], intent, msg)
    def assertSlotEqual(self, resp_json, slotName, slotValue, msg=None):
        slots_map = {}
        for slot in resp_json['data']['nlu'].get('semantics', {}).get('request', {}).get('slots', []):
            slots_map[slot['name']] = slot['value']
        return self.assertEqual(slots_map.get(slotName.decode('utf-8'), '').encode('utf-8'), slotValue, msg)
    def assertSlotExist(self, resp_json, slotName, msg=None):
        slots_map = {}
        for slot in resp_json['data']['nlu'].get('semantics', {}).get('request', {}).get('slots', []):
            slots_map[slot['name']] = slot['value']
        return self.assertIsNotNone(slots_map.get(slotName.decode('utf-8')), msg)

class SkillBaseTest(BaseTest):
    _skill_url = 'https://www.duiopen.com/skill/%s/test?sentence=%s&version=%s'
    _skill_id = None
    _skill_version = None
    # 异常捕获开关，默认关闭异常捕获，出错则测试停止
    _exception_switch = False
    
    def tearDown(self):
        print('%s %s End\n' % (get_time(), self.__str__()))
    def setUp(self):
        print(get_time(), '%s Start skillId: %d versionId: %s' % (self.__str__(), self._skill_id, self._skill_version))
    @classmethod
    def tearDownClass(self):
        print('SkillTest Finished')
    @classmethod
    def setUpClass(self):
        print('SkillTest Starting...')
        
    @catch_exception(exception_switch=_exception_switch)
    def execute_requests(self, input_word, user_cookies, contextId=None):
        print('\ninput:%s' % input_word)
        _url = self._skill_url % (self._skill_id, input_word, self._skill_version)
        if contextId:
            _url += '&contextId=%s' % contextId
        resp = requests.get(_url, cookies=user_cookies, timeout=4.5)
        self.assertEqual(200, resp.status_code)
        result = resp.json()
        print('nlg:%s' % result['data']['dm'].get('nlg'))
        print('dm:%s' % json.dumps(result['data']['dm'], ensure_ascii=False))
        print('dm_result:%s' % json.dumps(result, ensure_ascii=False, indent=4))
        self.assertIsNone(result['data'].get('error'))
        time.sleep(0.2)
        return result

class ProductBaseTest(BaseTest):
    _product_url = 'https://www.duiopen.com/product/version/debug?productId=%d'
    _productId = None
    _versionId = None
    # 异常捕获开关，默认关闭异常捕获，出错则测试停止
    _exception_switch = False
    
    def tearDown(self):
        print('%s %s End\n' % (get_time(), self.__str__()))
    def setUp(self):
        print(get_time(), '%s Start productId: %d versionId: %s' % (self.__str__(), self._productId, self._versionId))
    @classmethod
    def tearDownClass(self):
        print('ProductTest Finished')
    @classmethod
    def setUpClass(self):
        print('ProductTest Starting...')
        
    @catch_exception(switch=_exception_switch)    
    def execute_requests(self, body, user_cookies):
        print('\ninput:%s' % body['sentence'])
        resp = requests.post(self._product_url % (self._productId), cookies=user_cookies, json=body, timeout=4.5)
        self.assertEqual(200, resp.status_code)
        result = resp.json()
        print('nlg:%s' % result['data']['dm'].get('nlg'))
        print('dm:%s' % json.dumps(result['data']['dm'], ensure_ascii=False))
        print('dm_result:%s' % json.dumps(result, ensure_ascii=False, indent=4))
        self.assertIsNone(result['data'].get('error'))
        time.sleep(0.2)
        return result
