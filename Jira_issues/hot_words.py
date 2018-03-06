#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 2018年3月5日

@author: XuMaosen
'''
    
login_params = {
    'os_username':'xiongfuliang',
    'os_password':'xiongfuliang',
    'login':'login'
    }

from lxml import etree
import requests
import json

jira_host = 'https://jira.spetechcular.com'

def lxml_issues_parser(page):
    data = []
    doc = etree.HTML(page)
    all_tr = doc.xpath('//tr[@class="issuerow"]')
    for row in all_tr:
        value = {}
        value['issuekey'] = row.attrib['data-issuekey']
        value['status'] = row.xpath('.//td[@class="status"]')[0].xpath('.//span')[0].text
        value['time'] = row.xpath('.//td[@class="created"]')[0].xpath('.//time')[0].text
        data.append(value)
    return data

def lxml_issues_parser2(page):
    data = []
    doc = etree.HTML(page)
    all_tr = doc.xpath('//tr[@class="issuerow"]')
    for row in all_tr:
        value = {}
        components = row.xpath('.//td[@class="components"]')[0].xpath('.//a')
        if len(components) > 0:
            value['components'] = components[0].text.replace('\n', '').strip()
        epic_link = row.xpath('.//td[@class="customfield_10006"]')[0].xpath('.//a')
        if len(epic_link) > 0:
            value['epic_link'] = epic_link[0].text.replace('\n', '').strip()
        value['time'] = row.xpath('.//td[@class="created"]')[0].xpath('.//time')[0].text
        if len(value.keys()) > 1:
            data.append(value)
    return data

def lxml_details_parser(page):
    doc = etree.HTML(page)
    row = doc.xpath('//div[@class="user-content-block"]')[0]
    return row.xpath('.//p')[0].text

if __name__ == '__main__':
    login_url = '%s/login.jsp' % jira_host
    res = requests.get(login_url, params=login_params, verify=False)
    _cookies = res.cookies
    
    data = []
    for i in range(8):
        issues_url = '%s/issues/?jql=createdDate >= "2017-01-01" AND createdDate < "2018-01-01" ORDER BY createdDate DESC&startIndex=%s' % (jira_host, i * 70)
        issues_res = requests.get(issues_url, cookies=_cookies, verify=False)
        data += lxml_issues_parser2(issues_res.content)
        
#    for v in data:
#        details_url = '%s/browse/%s' % (jira_host, v['issuekey'])
#        details_res = requests.get(details_url, cookies=_cookies, verify=False)
#        v['details'] = lxml_details_parser(details_res.content)
    
    open('issues.txt', 'w').write(json.dumps(data, ensure_ascii=False))
    print 'OK'
