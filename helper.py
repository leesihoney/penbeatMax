########################
# Helper Functions for Pen Beat Max
########################
import os

def countTest(lst):
    count=0
    for val in lst:
        if val!=None:
            count+=1
    return count+1

def getRange(lst):
    pitchLst=[]
    volumeLst=[]
    # separate volume and pitch
    for (volume,pitch) in lst:
        pitchLst.append(pitch)
        volumeLst.append(volume)
    # sort pitches and volumes for convenience in calculating the IQR
    pitchLst.sort()
    volumeLst.sort()
    # find Q2
    qTwoIndex=len(lst)//2
    # split pitch list and volume list based on Q2
    pitchQOneLst,pitchQThreeLst=pitchLst[:qTwoIndex],pitchLst[qTwoIndex+1:]
    volumeQOneLst,volumeQThreeLst=volumeLst[:qTwoIndex],volumeLst[qTwoIndex+1:]
    # find Q1 and Q3 of pitch/volume lists based on splited versions
    qIndex=len(pitchQOneLst)//2
    # calcualate IQRs of both lists
    pitchIQR=pitchQThreeLst[qIndex]-pitchQOneLst[qIndex]
    volumeIQR=volumeQThreeLst[qIndex]-volumeQOneLst[qIndex]
    # eradicate outliers of both recorded pitches and volumes
    for i in range(len(pitchLst)):
        if pitchLst[i]<pitchQOneLst[qIndex]-pitchIQR*1.5 or pitchLst[i]>pitchQThreeLst[qIndex]+pitchIQR*1.5:
            pitchLst.pop(i)
        if volumeLst[i]<volumeQOneLst[qIndex]-volumeIQR*1.5 or volumeLst[i]>volumeQThreeLst[qIndex]+pitchIQR*1.5:
            volumeLst.pop(i)
    return [[min(pitchLst),max(pitchLst)],[min(volumeLst),max(volumeLst)]]