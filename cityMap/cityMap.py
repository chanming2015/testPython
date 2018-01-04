# !/usr/bin/env python
# -*- coding: utf-8 -*-

class cityMap:
    def __init__(self, code, name, lat, lng):
        self.code = code
        self.name = name
        self.lat = float(lat)
        self.lng = float(lng)
        self.province = None
        self.city = None
        self.area = None
        self.radian = 0
        
    def getInfo(self):
        return '|'.join((self.province, self.city, self.area))
    
def takeOneCity(values):
    if len(values) == 4:
        return cityMap(values[0], values[1], values[2], values[3])
    else: return cityMap(values[0], values[1], '0.0', '0.0')
    
gprovince = None
city = None
def mapLine(line):
    values = line.split('\t')
    cityMapClass = None
    global province
    global city
    if len(values[0]) > 0:
        cityMapClass = takeOneCity(values)
        cityMapClass.province = cityMapClass.name
        cityMapClass.city = cityMapClass.name
        cityMapClass.area = cityMapClass.name
        province = cityMapClass.name
        return cityMapClass
    if len(values[1]) > 0:
        cityMapClass = takeOneCity(values[1:])
        cityMapClass.province = province
        cityMapClass.city = cityMapClass.name
        cityMapClass.area = cityMapClass.name
        city = cityMapClass.name
        return cityMapClass
    if len(values[2]) > 0:
        cityMapClass = takeOneCity(values[2:])
        cityMapClass.province = province
        cityMapClass.city = city
        cityMapClass.area = cityMapClass.name
        return cityMapClass


citys = filter(lambda x: x.lat > 0, map(lambda x:mapLine(x), open('cityMap.txt').readlines()))
def getCity(lat, lng):
    alpha = 0.25
    result = []
    while(len(result) == 0):
        result = filter(lambda city:abs(city.lat - lat) < alpha and abs(city.lng - lng) < alpha, citys)
        alpha += alpha
    return result
  
import math
def getRadian(latA, lngA, latB, lngB):
    return math.acos(math.cos(90 - latB) * math.cos(90 - latA) + math.sin(90 - latB) * math.sin(90 - latA) * math.cos(lngB - lngA))

def setRadian(cityMap, latB, lngB):
    cityMap.radian = getRadian(cityMap.lat, cityMap.lng, latB, lngB)
    return cityMap

lat = 22.5238799
lng = 113.936759
print sorted(map(lambda x: setRadian(x, lat, lng), getCity(lat, lng)), key=lambda cityMap:cityMap.radian)[0].getInfo()














