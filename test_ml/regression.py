#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 2018年3月13日

@author: XuMaosen
'''
    
from numpy import *
import matplotlib.pyplot as plt

def loadDataSet():
    dataMat = [[1.0, 0.01], [1.0, 0.02], [1.0, 0.03], [1.0, 0.04], [1.0, 0.05], [1.0, 0.06]]
    labelMat = [0.13, 0.26, 0.34, 0.42, 0.57, 0.69]
    return dataMat, labelMat

def standRegres(xMat, yMat):
    xTx = xMat.T * xMat
    if linalg.det(xTx) == 0.0:
        print 'This matrix is singular, cannot do inverse'
        return
    ws = xTx.I * (xMat.T * yMat)
    return ws

def lwlr(testPoint, xMat, yMat, k=1.0):
    m = shape(xMat)[0]
    weights = mat(eye((m)))
    for j in range(m):
        diffMat = testPoint - xMat[j, :]
        weights[j, j] = exp(diffMat * diffMat.T / (-2.0 * k ** 2))
    xTx = xMat.T * (weights * xMat)
    if linalg.det(xTx) == 0.0:
        print 'This matrix is singular, cannot do inverse'
        return
    ws = xTx.I * (xMat.T * (weights * yMat))
    return testPoint * ws

def lwlrTest(testArr, xMat, yMat, k=1.0):
    m = shape(testArr)[0]
    yHat = zeros(m)
    for i in range(m):
        yHat[i] = lwlr(testArr[i], xMat, yMat, k)
    return yHat

xArr, yArr = loadDataSet()
xMat = mat(xArr)
yMat = mat(yArr)
# ws = standRegres(xMat, yMat.T)

fig = plt.figure()
ax = fig.add_subplot(111)
ax.scatter(xMat[:, 1].flatten().A[0], yMat.T[:, 0].flatten().A[0], c='red')

# xCopy = xMat.copy()
# xCopy.sort(0)
# yHat = xCopy * ws
# print corrcoef(yHat.T, yMat)
# ax.plot(xCopy[:, 1], yHat)

srtInd = xMat[:, 1].argsort(0)
xSort = xMat[srtInd][:, 0, :]
yHat = lwlrTest(xMat, xMat, yMat.T, 0.01)
print corrcoef(yHat.T, yMat)
ax.plot(xSort[:, 1], yHat[srtInd])
plt.show()
