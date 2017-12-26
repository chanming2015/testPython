#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 2017年12月21日

@author: XuMaosen
'''

from numpy import *
import operator
import matplotlib
import matplotlib.pyplot as plt

def createDataSet():
    group = array([[1.0, 1.1], [1.0, 1.0], [0, 0], [0, 0.1]])
    labels = [1, 1, 2, 2]
    return group, labels    

def classify0(inX, dataSet, labels, k):
    dataSetSize = dataSet.shape[0]
    diffMat = tile(inX, (dataSetSize, 1)) - dataSet
    sqDiffMat = diffMat ** 2
    sqDistances = sqDiffMat.sum(axis=1)
    distances = sqDistances ** 0.5
    sortedDisIndicies = distances.argsort()
    classCount = {}
    for i in range(k):
        voteIlabel = labels[sortedDisIndicies[i]]
        classCount[voteIlabel] = classCount.get(voteIlabel, 0) + 1
    sortedClassCount = sorted(classCount.iteritems(), key=operator.itemgetter(1), reverse=True)
    return sortedClassCount[0][0]
    
dataSet, labels = createDataSet()
# print classify0([0, 2], dataSet, labels, 3);
    
fig = plt.figure()
ax = fig.add_subplot(111)
ax.scatter(dataSet[:, 0], dataSet[:, 1], 15.0 * array(labels), 15.0 * array(labels))
plt.show()    
    
    
    
    
    
    
