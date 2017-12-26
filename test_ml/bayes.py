#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 2017年12月21日

@author: XuMaosen
'''
from numpy import *

def loadDataSet():
    postingList = [['my', 'dog', 'has', 'garbage'], ['stop', 'posting', 'stupid', 'worthless', 'garbage'], ['I', 'love', 'him', 'stop']]
    classVec = [0, 1, 0]
    return postingList, classVec
def createVocabList(dataSet):
    vocabSet = set([])
    for doc in dataSet:
        vocabSet = vocabSet | set(doc)
    return list(vocabSet)    
def setOfWords2Vec(vocabList, inputSet):
    returnVec = [0] * len(vocabList)
    for word in inputSet:
        if word in vocabList:
            returnVec[vocabList.index(word)] = 1
    return returnVec
    
def trainNB0(trainMatrix, trainCategory):
    numTrainDocs = len(trainMatrix)
    numWords = len(trainMatrix[0])
    pAbusive = sum(trainCategory) / float(numTrainDocs)
    p0Num = ones(numWords)
    p1Num = ones(numWords)
    p0Denom = 2.0
    p1Denom = 2.0
    for i in range(numTrainDocs):
        if trainCategory[i] == 1:
            p1Num += trainMatrix[i]
            p1Denom += sum(trainMatrix[i])
        else:
            p0Num += trainMatrix[i]
            p0Denom += sum(trainMatrix[i])
    p1Vect = log(p1Num / p1Denom)
    p0Vect = log(p0Num / p0Denom)
    return p0Vect, p1Vect, pAbusive
    
def classifyNB(vec2Classify, p0Vect, p1Vect, pClass1):
    p1 = sum(vec2Classify * p1Vect) + log(pClass1)
    p0 = sum(vec2Classify * p0Vect) + log(1 - pClass1)
    if p1 > p0:return 1 
    else:return 0    
    
    

listPosts, listClass = loadDataSet()
myVocabList = createVocabList(listPosts)
trainMat = []
for postinDoc in listPosts:
    trainMat.append(setOfWords2Vec(myVocabList, postinDoc))
p0Vect, p1Vect, pAbusive = trainNB0(trainMat, listClass)
testEntry = ['love', 'my', 'dog']
thisDoc = setOfWords2Vec(myVocabList, testEntry)
print classifyNB(thisDoc, p0Vect, p1Vect, pAbusive)

