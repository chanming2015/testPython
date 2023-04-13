'''
Created on 2023年4月7日

@author: Administrator
'''
import requests
import json
import os
import time
import random
from bs4 import BeautifulSoup, Tag


# 获取所有城市数据
def get_all_city():
    all_city_str = None
    try:
        all_city_str = open('all_city.html', encoding='utf-8').read()
    except Exception:
        pass
    
    if all_city_str is None:
        city_url = "https://www.ke.com/city/"
        city_resp = requests.get(city_url)
        all_city_str = city_resp.text
        open('all_city.html', 'w', encoding='utf-8').write(all_city_str)
        
    soup = BeautifulSoup(all_city_str, 'html.parser')
    items = soup.find_all(attrs={"class":"CLICKDATA"})
    city_map = {}
    for item in items:
        for it in item.children:
            if it.get('href') is not None:
                city_map[it.get_text()] = it.get('href')
    return city_map

#  分页获取一个城市的小区数据
def get_xiaoqu_by_city_page(c_name, c_url, page):
    city_xiqoqu_str = None
    file_name = "%s/%s-xiaoqu.html" % (c_name, page) 
    print(file_name, "time: %s" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    try:
        city_xiqoqu_str = open(file_name, encoding='utf-8').read()
    except Exception:
        pass
    
    if city_xiqoqu_str is None:
        if page == 1:
            f_url = "https:%s/xiaoqu/" % c_url
        else:
            f_url = "https:%s/xiaoqu/pg%s/" % (c_url, page)
        time.sleep(random.randint(20, 60))
        resp = requests.get(f_url)
        city_xiqoqu_str = resp.text
        open(file_name, 'w', encoding='utf-8').write(city_xiqoqu_str)
    
    soup = BeautifulSoup(city_xiqoqu_str, 'html.parser')
    # 获取总页数
    items = soup.find(attrs={"class":"page-box house-lst-page-box"})
    totalPage = json.loads(items.get('page-data')).get('totalPage')
    
    result_file = c_name + "/xiaoqu.txt"
    # 读取当前页小区数据
    items = soup.find_all(attrs={"class":"clear xiaoquListItem CLICKDATA"})
    for item in items:
        line = []
        for info in item.children:
            if type(info) is Tag and ['info'] == info.get('class'):
                for title in info.children:
                    if type(title) is Tag:
                        if ['title'] == title.get('class'):
                            for it in title.children:
                                if type(it) is Tag and ["maidian-detail"] == it.get('class'):
                                    line.append(it.get('title'))
                        elif ['positionInfo'] == title.get('class'):
                            for it in title.children:
                                if type(it) is Tag:
                                    if ['district'] == it.get('class'):
                                        line.append(it.get('title').replace("小区", ""))
                                    elif ['bizcircle'] == it.get('class'):
                                        line.append(it.get('title').replace("小区", ""))         
        open(result_file, 'a', encoding='utf-8').write("\t".join(line) + "\n")
    
    return totalPage

# 获取一个城市的小区数据
def get_xiaoqu_by_city(c_name, c_url):
    totalPage = get_xiaoqu_by_city_page(c_name, c_url, 1)
    for curPage in range(2, totalPage + 1):
        get_xiaoqu_by_city_page(c_name, c_url, curPage)


if __name__ == '__main__':
    print("start time: %s" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    all_city_map = get_all_city()
    
    for k, v in all_city_map.items():
        # 创建城市文件夹
        if not os.path.exists(k):
            os.mkdir(k)
        get_xiaoqu_by_city(k, v)
        break
    print("end time: %s" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    
    
    
