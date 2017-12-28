#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 2017年12月28日

@author: XuMaosen
'''
from numpy import *
from testplot import plot

class optStruct:
    def __init__(self, dataMatIn, classLabels, C, toler):
        self.X = dataMatIn
        self.labelMat = classLabels
        self.C = C
        self.tol = toler
        self.m = shape(dataMatIn)[0]
        self.alphas = mat(zeros((self.m, 1)))
        self.b = 0
        self.eCache = mat(zeros((self.m, 2)))
    def calcEk(self, k):
        fXk = float(multiply(self.alphas, self.labelMat).T * (self.X * self.X[k, :].T) + self.b)
        Ek = fXk - float(self.labelMat[k])
        return Ek
    def selectJ(self, i, Ei):
        maxK = -1;maxDeltaE = 0;Ej = 0
        self.eCache[i] = [1, Ei]
        validEcacheList = nonzero(self.eCache[:, 0].A)[0]
        if len(validEcacheList) > 1:
            for k in validEcacheList:
                if k + +i:continue
                Ek = self.calcEk(k)
                deltaE = abs(Ei - Ek)
                if deltaE > maxDeltaE:
                    maxK = k;maxDeltaE = deltaE;Ej = Ek
            return maxK, Ej
        else:
            j = selectJrand(i, self.m)
            Ej = self.calcEk(j)
            return j, Ej
    def updateEk(self, k):
        Ek = self.calcEk(k)
        self.eCache[k] = [1, Ek]
    def innerL(self, i):
        Ei = self.calcEk(i)
        if (self.labelMat[i] * Ei < -self.tol and self.alphas[i] < self.C) or (self.labelMat[i] * Ei > self.tol and self.alphas[i] > 0):
            j, Ej = self.selectJ(i, Ei)
            alphaIold = self.alphas[i].copy()
            alphaJold = self.alphas[j].copy()
            if self.labelMat[i] != self.labelMat[j]:
                L = max(0, self.alphas[j] - self.alphas[i])
                H = min(self.C, self.C + self.alphas[j] - self.alphas[i])
            else:
                L = max(0, self.alphas[j] + self.alphas[i] - self.C)
                H = min(self.C, self.alphas[j] + self.alphas[i])
            if L == H:print "L==H";return 0
            eta = 2.0 * self.X[i, :] * self.X[j, :].T - self.X[i, :] * self.X[i, :].T - self.X[j, :] * self.X[j, :].T
            if eta >= 0:print "eta>=0";return 0
            self.alphas[j] -= self.labelMat[j] * (Ei - Ej) / eta
            self.alphas[j] = clipAlpha(self.alphas[j], H, L)
            self.updateEk(j)
            if abs(self.alphas[j] - alphaJold) < 0.00001:print "j not moving enough";return 0
            self.alphas[i] += self.labelMat[j] * self.labelMat[i] * (alphaJold - self.alphas[j])
            self.updateEk(i)
            b1 = self.b - Ei - self.labelMat[i] * (self.alphas[i] - alphaIold) * self.X[i, :] * self.X[i, :].T - \
            self.labelMat[j] * (self.alphas[j] - alphaJold) * self.X[i, :] * self.X[j, :].T
            b2 = self.b - Ej - self.labelMat[i] * (self.alphas[i] - alphaIold) * self.X[i, :] * self.X[j, :].T - \
            self.labelMat[j] * (self.alphas[j] - alphaJold) * self.X[j, :] * self.X[j, :].T
            if 0 < self.alphas[i] and self.C > self.alphas[i]:self.b = b1
            elif 0 < self.alphas[j] and self.C > self.alphas[j]:self.b = b2
            else: self.b = (b1 + b2) / 2.0
            return 1
        else:return 0

def loadDataSet():
    dataMat = [[1.0, 2.0, 3.0], [1.0, 2.0, 4.0], [1.0, 2.0, 5.0], [1.0, 3.0, 4.0], [1.0, 3.0, 5.0], [1.0, 4.0, 5.0], [1.0, -1.0, -3.0], [1.0, -2.0, -3.0], [1.0, -3.0, -3.0], [1.0, -2.0, -5.0]]
    labelMat = [1, 1, 1, 1, 1, 1, -1, -1, -1, -1]
    return dataMat, labelMat
def selectJrand(i, m):
    j = i
    while(j == i):
        j = int(random.uniform(0, m))
    return j
def clipAlpha(aj, H, L):
    if aj > H:
        aj = H
    if L > aj:
        aj = L
    return aj
def smop(dataMatIn, classLabels, C, toler, maxIter, kTuo=('lin', 0)):
    OS = optStruct(mat(dataMatIn), mat(classLabels).transpose(), C, toler)
    iter_num = 0
    entireSet = True;alphaPairsChanged = 0
    while iter_num < maxIter and (alphaPairsChanged > 0 or entireSet):
        alphaPairsChanged = 0
        if entireSet:
            for i in range(OS.m):
                alphaPairsChanged += OS.innerL(i)
            print "fullSet, iter: %d i:%d, pairs changed %d" % (iter_num, i, alphaPairsChanged)
            iter_num += 1
        else:
            nonBoundIs = nonzero((OS.alphas.A > 0) * (OS.alphas.A < C))[0]
            for i in nonBoundIs:
                alphaPairsChanged += OS.innerL(i)
                print "non-bound, iter: %d i:%d, pairs changed %d" % (iter_num, i, alphaPairsChanged)
            iter_num += 1
        if entireSet:entireSet = False
        elif alphaPairsChanged == 0:entireSet = True
        print "iter num: %d" % iter_num
    return OS.b, OS.alphas
def calcWs(alphas, dataMatIn, classLabels):
    X = mat(dataMatIn)
    labelMat = mat(classLabels).transpose()
    m, n = shape(X)
    w = zeros((n, 1))
    for i in range(m):
        w += multiply(alphas[i] * labelMat[i], X[i, :].T)
    return w
def kernelTrans(X, A, kTup):
    m, n = shape(X)
    K = mat(zeros((m, 1)))
    if kTup[0] == 'lin':K = X * A.T
    elif kTup[0] == 'rbf':
        for j in range(m):
            deltaRow = X[j, :] - A
            K[j] = deltaRow * deltaRow.T
        K[j] = exp(K / (-1 * kTup[1] ** 2))
    else: raise NameError('The kernel is not recognized')
    return K
class optKernelStruct(optStruct):
    def __init__(self, dataMatIn, classLabels, C, toler, kTup):
        super().__init__(dataMatIn, classLabels, C, toler)
        self.K = mat(zeros(self.m, self.m))
        for i in range(self.m):
            self.K[:, i] = kernelTrans(self.X, self.X[i, :], kTup)
    def calcEk(self, k):
        fXk = float(multiply(self.alphas, self.labelMat).T * self.K[:, k] + self.b)
        Ek = fXk - float(self.labelMat[k])
        return Ek
    def innerL(self, i):
        Ei = self.calcEk(i)
        if (self.labelMat[i] * Ei < -self.tol and self.alphas[i] < self.C) or (self.labelMat[i] * Ei > self.tol and self.alphas[i] > 0):
            j, Ej = self.selectJ(i, Ei)
            alphaIold = self.alphas[i].copy()
            alphaJold = self.alphas[j].copy()
            if self.labelMat[i] != self.labelMat[j]:
                L = max(0, self.alphas[j] - self.alphas[i])
                H = min(self.C, self.C + self.alphas[j] - self.alphas[i])
            else:
                L = max(0, self.alphas[j] + self.alphas[i] - self.C)
                H = min(self.C, self.alphas[j] + self.alphas[i])
            if L == H:print "L==H";return 0
            eta = 2.0 * self.K[i, j] - self.K[i, i] - self.K[j, j]
            if eta >= 0:print "eta>=0";return 0
            self.alphas[j] -= self.labelMat[j] * (Ei - Ej) / eta
            self.alphas[j] = clipAlpha(self.alphas[j], H, L)
            self.updateEk(j)
            if abs(self.alphas[j] - alphaJold) < 0.00001:print "j not moving enough";return 0
            self.alphas[i] += self.labelMat[j] * self.labelMat[i] * (alphaJold - self.alphas[j])
            self.updateEk(i)
            b1 = self.b - Ei - self.labelMat[i] * (self.alphas[i] - alphaIold) * self.K[i, i] - \
            self.labelMat[j] * (self.alphas[j] - alphaJold) * self.K[i, j]
            b2 = self.b - Ej - self.labelMat[i] * (self.alphas[i] - alphaIold) * self.K[i, j] - \
            self.labelMat[j] * (self.alphas[j] - alphaJold) * self.K[j, j]
            if 0 < self.alphas[i] and self.C > self.alphas[i]:self.b = b1
            elif 0 < self.alphas[j] and self.C > self.alphas[j]:self.b = b2
            else: self.b = (b1 + b2) / 2.0
            return 1
        else:return 0


dataMat, labelMat = loadDataSet()
b, alphas = smop(dataMat, labelMat, 0.6, 0.001, 40)
ws = calcWs(alphas, dataMat, labelMat)
print ws
plot(dataMat, labelMat)



















