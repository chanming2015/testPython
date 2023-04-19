'''
Created on 2023年4月7日

@author: Administrator
'''
import json
import os
import time
from bs4 import BeautifulSoup, Tag

def process_one_city(folder):
    # 遍历 folder 路径下的所有 xiaoqu.html
    for f in os.listdir('./' + folder):
        if f.endswith('xiaoqu.html'):
            soup = BeautifulSoup(open(folder + "/" + f, encoding='utf-8').read(), 'html.parser')
            # 获取总页数
            items = soup.find(attrs={"class":"page-box house-lst-page-box"})
            if items is None:
                print("%s has no page-data" % folder)
                return -1;
            
            result_file = folder + "/xiaoqu.csv"
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
                                            line.append(it.get('title').replace(",", " "))
                                elif ['positionInfo'] == title.get('class'):
                                    for it in title.children:
                                        if type(it) is Tag:
                                            if ['district'] == it.get('class'):
                                                line.append(it.get('title').replace("小区", "").replace(",", " "))
                                            elif ['bizcircle'] == it.get('class'):
                                                line.append(it.get('title').replace("小区", "").replace(",", " "))         
                open(result_file, 'a', encoding='utf-8').write(",".join(line) + "\n")

if __name__ == '__main__':
    print("start time: %s" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    
    # 获取城市-省份 映射关系
    cityMaps = json.loads(open("cityMaps.json", encoding='utf-8').read())
    result_file = "result.csv"
    
    if os.path.exists(result_file):
        try:
            os.remove(result_file)
        except Exception as e:
            print("Error deleting file:", e)
    
    # 遍历当前路径下的所有文件夹
    for folder in os.listdir('.'):
        if os.path.isdir(folder):
            file_name = "%s/xiaoqu.csv" % folder
            # 判断文件是否存在
            if os.path.exists(file_name):
                # To delete a file, use the os.remove() function
                try:
                    os.remove(file_name)
                except Exception as e:
                    print("Error deleting file:", e)
            
            # 生成xiaoqu.csv
            process_one_city(folder)    
            if os.path.exists(file_name):
                province = cityMaps.get(folder + '市')
                if province is not None:
                    city_xiqoqu_list = open(file_name, encoding='utf-8').readlines()
                    for li in city_xiqoqu_list:
                        li = "%s,%s,%s\n" % (li[:-2], province, folder)
                        # 写入最终结果文件
                        open(result_file, 'a', encoding='utf-8').write(li)
            
    print("end time: %s" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    
    
    
