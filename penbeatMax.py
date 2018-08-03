''' 
pygamegame.py
created by Lukas Peraza
 for 15-112 F17 Siheon Lee's term project, 11/16/17
'''
# penbeatMax.onAirTwo(self) and penbeatMax.testingBeat(self) are from 
# codes by notalentgeek
# https://github.com/aubio/aubio/issues/78
# fonts are from dafont.com 
# logo is from freelogoservices.com
# sound files are from beatstars.com and melon.com
import threading
import time
import os
import pygame
import sys
import pyaudio
import wave
from helper import *
from bpm import *
import aubio
import numpy as num

BLACK=(0,0,0)
WHITE=(255,255,255)
RED=(255,0,0)
GREEN=(0,255,0)
BLUE=(0,0,255)
YELLOW=(255,255,0)

###########
# Classes (OOPs)
###########
# show performance (Perfect, Great, Good, Bad, Miss)
class performance(object):
    def __init__(self,name,imgPath,score,x,y):
        self.x=x
        self.y=y
        self.name=name
        self.image=pygame.image.load(imgPath)
        self.score=score
        self.rect=self.image.get_rect()
        self.rect.center=(x,y)

class Note(pygame.sprite.Sprite):
    def __init__(self,x,y,strumTime):
        pygame.sprite.Sprite.__init__(self)
        self.strum=strumTime
        self.x=x
        self.y=y
        self.width=71
        self.height=44
    def move(self,newY):
        if newY>0:
            self.y=newY+self.height//2
        self.rect=pygame.Rect(self.x,self.y,self.width,self.height)
    def update(self,delayTime):
        self.strum-=delayTime
# sprite groups for notes
class bassNote(Note):
    def __init__(self,x,y,strumTime):
        super().__init__(x,y,strumTime)
        self.beatType="Bass"
        self.image=pygame.image.load("image/bassNote.png")
        self.rect=self.image.get_rect()
        self.rect.move_ip(self.x,self.y)
        
class hiNote(Note):
    def __init__(self,x,y,strumTime):
        super().__init__(x,y,strumTime)
        self.beatType="Hi"
        self.image=pygame.image.load("image/hiNote.png")
        self.rect=self.image.get_rect()
        self.rect.move_ip(self.x,self.y)

class snareNote(Note):
    def __init__(self,x,y,strumTime):
        super().__init__(x,y,strumTime)
        self.beatType="Snare"
        self.image=pygame.image.load("image/snareNote.png")
        self.rect=self.image.get_rect()
        self.rect.move_ip(self.x,self.y)
        
# game bar class(sprite)
class gameBar(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.x=x
        self.y=y
        self.image=pygame.image.load("image/bar.png")
        self.width=218
        self.height=44
        self.rect=self.image.get_rect()
        self.rect.move_ip(self.x,self.y)
            
# songs including title, pygame mixer, bpm, length, bps
class song(object):
    def __init__(self,title):
        self.title=title
        self.length=pygame.mixer.Sound("sound/%s.wav"%title).get_length()*1000
        self.songInfo=getBeats(os.getcwd()+"/sound/%s.wav"%title)
    def __eq__(self,other):
        if not isinstance(other, song):
            return False
        else:
            return self.title==other.title and self.play==other.play
    def __hash__(self):
        return hash((self,title,self.play))
    
class beat(object):
    def __init__(self,beat):
        self.beat=beat
        self.range=[None,None,None,None,None,None,None]
    def __eq__(self,other):
        if not isinstance(other,beat):
            return False
        else:
            return self.beat==other.beat and self.range==other.range
    def __hash__(self):
        return hash((self.beat,self.range))
############
# Game Function
############
class penbeatMax(object):
############
# Init Functions
############
    # aubio related variables
    def aubioInit(self):
        self.aubioChunk = 1024
        self.aubioWidth = 2
        self.aubioChannels = 1
        self.aubioRate = 44100
        self.aubioRecSec = 1.5
        self.aubioMinVol=1000
        self.aubioVolMult=1000000
        self.testTime=int(self.aubioRate/self.aubioChunk*self.aubioRecSec)
    # initialize when game is done
    def gameRenewInit(self):
        penbeatMax.aubioInit(self)
        self.score=0
        self.combo=0
        self.currKey=None
        self.gameThread=threading.Thread(target=penbeatMax.onAirTwo,args=(self,))
        self.allSprites=pygame.sprite.Group()
        self.songs=penbeatMax.playList("/sound")
        self.songIndex=0
        self.currSongIndex=0
        self.blockCreator=None
        self.beatRangeIndex=0
        self.beatCount=0
        self.performance=None
        self.perfDic=dict()
        self.onAir=False
        self.mostAccurate=0
        self.timerCount=0
        self.songPosition=pygame.mixer.music.get_pos()
        self.lastPlayHeadPosition=0
        self.gameTimer=0
        self.testMode="ready"
    def init(self):
        # aubio related variables
        penbeatMax.aubioInit(self)
        # init variables that should be initialized when game renewed
        penbeatMax.gameRenewInit(self)
        # else
        self.gameMode="start"
        self.longButton=pygame.image.load("image/longButton.png")
        self.longButtonA=pygame.image.load("image/longButtonA.png")
        self.longButtonW=300
        self.longButtonH=60
        self.button=pygame.image.load("image/button.png")
        self.logo=pygame.image.load("image/logo.png")
        self.background=pygame.image.load("image/startBG.jpg")
        self.blockWidth=71
        self.blockHeight=self.width//9
        self.buttonWidth=138
        self.buttonHeight=45
        self.beatRange=[beat("Bass"),beat("Hi"),beat("Snare")]
        self.bar=gameBar(self.width*(3/11),self.height*(8/9))
        self.movingUnit=4
        self.testSuccess=None
        self.testAgain=""
        self.latency=-0 # should be changed for computers with high video latency
        self.delayTime=500
    
############
# Mouse Actions
############
    # mousePressed actions for starting screen
    def startMousePressed(self,x,y):
        if self.width*(2/3)<x<self.width*(2/3)+self.buttonWidth:
            # when press test button
            if self.height*(3/5)<y<self.height*(3/5)+self.buttonHeight:
                self.beatRangeIndex=0
                self.gameMode="Test"
            # when press menu button
            elif self.height*(3/4)<y<self.height*(3/4)+self.buttonHeight:
                self.gameMode="Menu"
    # mousePressed actions when testing
    def testMousePressed(self,x,y):
        # when press start button
        if self.width*(2/3)<x<self.width*(2/3)+self.buttonWidth and self.height*(3/4)<y<self.height*(3/4)+self.buttonHeight:
            self.beatRange=[beat("Bass"),beat("Hi"),beat("Snare")]
            self.beatRangeIndex=None
            penbeatMax.resetTest(self)
            self.gameMode="start"
    # mousePressed actions when game is paused
    def pausedMousePressed(self,x,y):
        if self.height*(4/5)<y<self.height*(4/5)+self.buttonHeight:
            # when press resume button
            if self.width*(2/3)<x<self.width*(2/3)+self.buttonWidth:
                self.gameMode="Game"
                pygame.mixer.music.unpause()
            # when press menu button
            elif self.width*(1/3)-self.buttonWidth<x<self.width*(1/3):
                penbeatMax.gameRenewInit(self)
                penbeatMax.turnMusic(self)
                self.gameMode="Menu"
    # mousePressed actions when game is over
    def gameOverMousePressed(self,x,y):
        if self.height*(4/5)<y<self.height*(4/5)+self.buttonHeight:
            # when press test button
            if self.width*(2/3)<x<self.width*(2/3)+self.buttonWidth:
                penbeatMax.resetTest(self)
                penbeatMax.gameRenewInit(self)
                penbeatMax.turnMusic(self)
                self.gameMode="Test"
            # when press menu button
            elif self.width*(1/3)-self.buttonWidth<x<self.width*(1/3):
                penbeatMax.gameRenewInit(self)
                penbeatMax.turnMusic(self)
                self.gameMode="Menu"
    # mousePressed actions when choosing which song to play
    def menuMousePressed(self,x,y):
        # when press back button
        backWidth,backHeight=50,50
        posX,posY=self.width//15,self.height-self.height//5
        if (posX<x<posX+backWidth and posY<y<posY+backHeight):
            penbeatMax.resetTest(self)
            penbeatMax.gameRenewInit(self)
            self.gameMode="Test"
    def mousePressed(self, x, y):
        # clicking buttons
        if self.gameMode=="start":
            penbeatMax.startMousePressed(self,x,y)
        if self.gameMode=="Test":
            penbeatMax.testMousePressed(self,x,y)
        if self.gameMode=="Paused":
            penbeatMax.pausedMousePressed(self,x,y)
        if self.gameMode=="Done":
            penbeatMax.gameOverMousePressed(self,x,y)
        if self.gameMode=="Menu":
            penbeatMax.menuMousePressed(self,x,y)
            
    def mouseReleased(self, x, y):
        pass

    def mouseMotion(self, x, y):
        pass

    def mouseDrag(self, x, y):
        pass
############
# Key Related Functions
############
    def keyPressed(self, keyCode, modifier):
        if self.gameMode=="Game":
            if keyCode==pygame.K_z:
                self.currKey="z"
            if keyCode==pygame.K_x:
                self.currKey="x"
            if keyCode==pygame.K_c:
                self.currKey="c"
            if keyCode==pygame.K_p:
                self.gameMode="Paused"
                pygame.mixer.music.pause()
        if self.gameMode=="Test":
            if self.testMode=="ready":
                if keyCode==pygame.K_s:
                    self.testMode="test"
            if self.testMode=="test":
                    penbeatMax.conductTest(self)
                    self.testMode="ready"
        if self.gameMode=="Menu":
            # able to choose which song by pressing up and down
            if self.songIndex>0 and keyCode==pygame.K_UP:
                self.songIndex-=1
            if self.songIndex<len(self.songs)-1 and keyCode==pygame.K_DOWN:
                self.songIndex+=1
            # press enter when you want to begin a game with the selected song
            if keyCode==pygame.K_RETURN:
                penbeatMax.offMusic(self)
                self.currSongIndex=self.songIndex
                self.mostAccurate=0
                penbeatMax.addNotes(self)
                # turn the sound analyzer if beats are recorded
                if penbeatMax.areBeatsRecorded(self):
                    self.onAir=True
                    self.gameThread.start()
                self.gameMode="Game"
                
    def keyReleased(self, keyCode, modifier):
        if self.gameMode=="Game":
            if keyCode==pygame.K_z or pygame.K_x or pygame.K_c:
                self.currKey=None
######################
# Tool Functions
######################
    # check whether beats are tested
    def areBeatsRecorded(self):
        for beats in self.beatRange:
            if None in beats.range:
                return False
        return True
    # resetting recorded test values in each beats
    def resetTest(self):
        for beats in self.beatRange:
            beats.__init__(beats.beat)
    # adding playing notes before game starts
    def addNotes(self):
        # 8 beats
        beat=8
        song=self.songs[self.currSongIndex]
        for timeI in range(len(song.songInfo)):
            newY=-self.blockHeight*2
            modI=timeI%beat
            if modI in (0,5):
                self.allSprites.add(bassNote(self.width*(7/11)-self.blockWidth,newY,song.songInfo[timeI]))
            if modI in (1,3,4,7):
                self.allSprites.add(hiNote(self.width*(3/11),newY,song.songInfo[timeI]))
            if modI in (2,6):
                self.allSprites.add(snareNote(self.width*(3/11)+self.blockWidth,newY,song.songInfo[timeI]))
    # turning on the music
    def turnMusic(self):
        currSong=self.songs[self.currSongIndex]
        pygame.mixer.music.load(os.getcwd()+"/sound/%s.wav"%currSong.title)
        pygame.mixer.music.play()
    # turning off the music
    def offMusic(self):
        pygame.mixer.music.stop()
    # make a song play list full with song classes
    def playList(path):
        playList=[]
        for fileName in os.listdir(os.getcwd()+path):
            if fileName.endswith(".wav"):
                wavIndex=fileName.index(".wav")
                playList.append(song(fileName[:wavIndex]))
        return playList
            
    # calculate the collision ratio between bar and note
    def getCollisionRatio(self,noteSprite):
        if self.bar.y<=noteSprite.y+noteSprite.height<=self.bar.y+self.bar.height:
            collisionHeight=(noteSprite.y+noteSprite.height-self.bar.y)
        elif self.bar.y<noteSprite.y<self.bar.y+self.bar.height:
            collisionHeight=(self.bar.y+self.bar.height)-noteSprite.y
        return collisionHeight/self.bar.height
    # calculate the score 
    def getScore(self,ratio):
        comboMult=5
        if 0.9<ratio<=1.0:
            self.performance=performance("Perfect",os.getcwd()+
                    "/image/perfect.png",100,self.width*(4/5),self.height//2)
        elif 0.7<ratio<=0.9:
            self.performance=performance("Great",os.getcwd()+
                        "/image/great.png",50,self.width*(4/5),self.height//2)
        elif 0.3<ratio<=0.7:
            self.performance=performance("Good",os.getcwd()+
                        "/image/good.png",20,self.width*(4/5),self.height//2)
        elif 0<ratio<=0.3:
            self.performance=performance("Bad",os.getcwd()+
                        "/image/bad.png", 5, self.width*(4/5),self.height//2)
            self.combo=0
        # add score based on performance and combo
        if self.performance!=None:
            self.score+=self.performance.score+comboMult*self.combo
        # update the performance dictionary
            if self.performance.name not in self.perfDic:
                self.perfDic[self.performance.name]=1
            else:
                self.perfDic[self.performance.name]+=1
######################
# Testing Functions
######################
    # testing
    def conductTest(self):
        testBeat=self.beatRange[self.beatRangeIndex]
        # record the first hit
        print("Hit %s"%testBeat.beat)
        testValue=penbeatMax.testingBeat(self)
        # divide when testing succeeds or not
        if testValue!=None:
            # will use this variable to draw whether testing was successful
            self.testSuccess=True
            print(testValue)
            # record the test value
            for valueIndex in range(len(testBeat.range)):
                if testBeat.range[valueIndex]==None:
                    testBeat.range[valueIndex]=testValue
                    break
        if testValue==None:
            self.testSuccess=False
        # proceed when testing for each beat is done
        if self.beatRangeIndex==0 and None not in testBeat.range:
            try:
                testBeat.range=getRange(testBeat.range)
                self.resetTest=""
                self.beatRangeIndex=1
            except:
                self.resetTest="Cannot make sound range, Need to retest"
                testBeat.range=[None,None,None,None,None,None,None]
            self.testSuccess=None
        elif self.beatRangeIndex==1 and None not in testBeat.range:
            try:
                testBeat.range=getRange(testBeat.range)
                self.resetTest=""
                self.beatRangeIndex=2
            except:
                self.resetTest="Cannot make sound range, Need to retest"
                testBeat.range=[None,None,None,None,None,None,None]
            self.testSuccess=None
        elif self.beatRangeIndex==2 and None not in testBeat.range:
            try:
                testBeat.range=getRange(testBeat.range)
                self.resetTest=""
            except:
                self.resetTest="Cannot make sound range, Need to retest"
                testBeat.range=[None,None,None,None,None,None,None]
            self.testSuccess=None
            self.gameMode="Menu"

    # sound recording
    def testingBeat(self):
        # used for appending resulting volume and pitch during test
        sampleRange=[]
        volLst,pitchLst=[],[]
        pitchMax,pitchCurr=-1,0
        # PyAudio object.
        p = pyaudio.PyAudio()
        # Open stream.
        stream = p.open(format=pyaudio.paFloat32, channels=self.aubioChannels, rate=self.aubioRate, input=True, frames_per_buffer=self.aubioChunk)
        
        # Aubio's pitch detection.
        pDetect = aubio.pitch("default", 2*self.aubioChunk,self.aubioChunk, self.aubioRate)
        # Set unit.
        pDetect.set_unit("Hz")
        pDetect.set_silence(-40)
        
        for i in range(0, self.testTime):
            data = stream.read(self.aubioChunk)
            samples = num.fromstring(data, dtype=aubio.float_type)
            pitch = pDetect(samples)[0]
            # Compute the energy (volume) of the
            # current frame.
            volume = num.sum(samples**2)/len(samples)
            # Format the volume output so that at most
            # it has six decimal numbers.
            volume = "{:.6f}".format(volume)
            if pitch!=0:
                sampleRange.append((float(volume)*self.aubioVolMult,pitch))
        try:
            return max(sampleRange)
        except:
            return None

    # on game realtime sound analyzer
    def onAirTwo(self):
        # PyAudio object.
        pitchIndex,volumeIndex=0,1
        minIndex,maxIndex=0,1
        bass,hi,snare=self.beatRange[0],self.beatRange[1],self.beatRange[2]
        self.aubioRecSec=0.5
        p = pyaudio.PyAudio()
        sound=[]
        # Open stream.
        stream = p.open(format=pyaudio.paFloat32, channels=self.aubioChannels, 
            rate=self.aubioRate, input=True, frames_per_buffer=self.aubioChunk)
        
        # Aubio's pitch detection.
        pDetect = aubio.pitch("default", 2*self.aubioChunk,self.aubioChunk, 
                                                                self.aubioRate)
        # Set unit
        pDetect.set_unit("Hz")
        pDetect.set_silence(-40)
        while self.onAir:
            data = stream.read(self.aubioChunk)
            samples = num.fromstring(data, dtype=aubio.float_type)
            pitch = pDetect(samples)[0]
            # Compute the energy (volume) of the
            # current frame.
            volume = num.sum(samples**2)/len(samples)
            # Format the volume output so that at most
            # it has six decimal numbers.
            volume = "{:.6f}".format(volume)
            # works if sound occurs
            self.currKey=None
            if float(volume)*self.aubioVolMult>self.aubioMinVol and pitch!=0:
                if (snare.range[volumeIndex][minIndex]
                                            <=float(volume)*self.aubioVolMult
                                  
                                        <=snare.range[volumeIndex][maxIndex]):
                    self.currKey="x"
                elif (bass.range[pitchIndex][minIndex]<=pitch
                                        <=bass.range[pitchIndex][maxIndex]):
                    self.currKey="c"
                else:
                    self.currKey="z"
            
############
# TimerFired
############
    def timerFired(self,dt):
        if self.gameMode=="Paused":
            return
        if self.gameMode=="Game":
            currSong=self.songs[self.currSongIndex]
            # whether music should be on or not
            if self.mostAccurate>=self.delayTime and not pygame.mixer.music.get_busy():
                penbeatMax.turnMusic(self)
                self.mostAccurate=0
                penbeatMax.syncMusic(self)
            if pygame.mixer.music.get_busy():
                penbeatMax.syncMusic(self)
                penbeatMax.moveNotes(self)
                penbeatMax.killNotes(self)
            if pygame.mixer.music.get_pos()>currSong.length:
                penbeatMax.offMusic(self)
                if self.onAir:
                    self.onAir=False
                    self.gameThread.join()
                self.gameTimer=0
                self.gameMode="Done"
                
    # moving notes by correct synchornization
    def syncMusic(self):
        if self.songPosition != self.lastPlayHeadPosition:
            self.mostAccurate = (self.mostAccurate + self.songPosition)/2
            self.lastPlayHeadPosition=self.songPosition
    def moveNotes(self):
        for noteSprite in self.allSprites.sprites():
            distance=self.bar.y-((noteSprite.strum-self.mostAccurate)/self.movingUnit)+self.latency
            noteSprite.move(distance)
    # killing notes by timing
    def killNotes(self):
        for noteSprite in self.allSprites.sprites():
            # check for collision
            if pygame.sprite.collide_rect(self.bar,noteSprite):
                collision=penbeatMax.getCollisionRatio(self,noteSprite)
                if self.currKey=="z" and noteSprite.beatType=="Hi":
                    self.combo+=1
                    penbeatMax.getScore(self,collision)
                    noteSprite.kill()
                elif self.currKey=="x" and noteSprite.beatType=="Snare":
                    self.combo+=1
                    penbeatMax.getScore(self,collision)
                    noteSprite.kill()
                elif self.currKey=="c" and noteSprite.beatType=="Bass":
                    self.combo+=1
                    penbeatMax.getScore(self,collision)
                    noteSprite.kill()
            elif noteSprite.y>self.height:
                self.combo=0
                self.performance=performance("Miss",os.getcwd()+"/image/miss.png",0,self.width*(4/5),self.height//2)
                noteSprite.kill()
############
# Drawing Functions
############
    # draw the start screen
    def drawStartScreen(screen,self):
        # draw background
        screen.blit(self.background,(0,0))
        # draw logo
        screen.blit(self.logo,(0,-self.height//3))
        # draw buttons
        screen.blit(self.button,(self.width*(2/3),self.height*(3/5)))
        screen.blit(self.button,(self.width*(2/3),self.height*(3/4)))
        # draw texts for buttons
        startText="Start"
        startFont=pygame.font.Font("font/AldotheApache.ttf",25)
        startSurf=startFont.render(startText, True, WHITE)
        startRect=startSurf.get_rect()
        startRect.center=(self.width*(2/3)+self.buttonWidth//2,self.height*(3/4)+self.buttonHeight//2)
        screen.blit(startSurf,startRect)
        testText="Test"
        testFont=pygame.font.Font("font/AldotheApache.ttf",25)
        testSurf=testFont.render(testText,True,WHITE)
        testRect=testSurf.get_rect()
        testRect.center=(self.width*(2/3)+self.buttonWidth//2,self.height*(3/5)+self.buttonHeight//2)
        screen.blit(testSurf,testRect)
        
    # draw game mode screen
    def drawGameScreen(screen,self):
        # draw background
        gameBG=pygame.image.load("image/gameBG.png")
        screen.blit(gameBG,(0,0))
        # draw blocks
        penbeatMax.drawBlocks(screen,self)
        # draw game board
        pygame.draw.line(screen,YELLOW,(self.width*(3/11),0),(self.width*(3/11),self.height),2)
        pygame.draw.line(screen,YELLOW,(self.width*(7/11),0),(self.width*(7/11),self.height),2)
        screen.blit(self.bar.image,(self.bar.x,self.bar.y))
        # fill when key pressed
        if self.currKey!=None:
            penbeatMax.drawKeyPressed(screen,self)
        # draw performance
        if self.performance!=None:
            screen.blit(self.performance.image,self.performance.rect)
        # draw combo
        comboText="Combo: %d"%self.combo
        comboFont=pygame.font.Font("font/Enter-The-Grid.ttf",20)
        comboSurf=comboFont.render(comboText, True, WHITE)
        comboRect=comboSurf.get_rect()
        comboRect.center=(self.width*(4/5),self.height/9)
        screen.blit(comboSurf,comboRect)

    # drawing blocks from self.blockList
    def drawBlocks(screen,self):
        for sprite in self.allSprites.sprites():
            screen.blit(sprite.image,(sprite.x,sprite.y))

    # function that draws when key is pressed
    def drawKeyPressed(screen,self):
        if self.currKey=="z":
            pointX=self.width*(3/11)
        if self.currKey=="x":
            pointX=self.width*(3/11)+self.blockWidth
        if self.currKey=="c":
            pointX=self.width*(7/11)-self.blockWidth
        pygame.draw.rect(screen,BLUE,(pointX,self.height*(8/9),self.blockWidth,self.blockHeight))
        
    # drawing paused screen
    def drawPausedScreen(screen,self):
        screen.fill(BLACK)
        # "Game Paused" Text
        pausedText="Game Paused"
        pausedFont=pygame.font.Font("font/BatmanForeverAlternate.ttf",25)
        pausedSurf=pausedFont.render(pausedText, True, WHITE)
        pausedRect=pausedSurf.get_rect()
        pausedRect.center=(self.width//2,self.height//3)
        screen.blit(pausedSurf,pausedRect)
        # draw button
        screen.blit(self.button,(self.width*(2/3),self.height*(4/5)))
        screen.blit(self.button,(self.width*(1/3)-self.buttonWidth,self.height*(4/5)))
        # draw texts for buttons
        resumeText="Resume"
        resumeFont=pygame.font.Font("font/AldotheApache.ttf",25)
        resumeSurf=resumeFont.render(resumeText, True, WHITE)
        resumeRect=resumeSurf.get_rect()
        resumeRect.center=(self.width*(2/3)+self.buttonWidth//2,self.height*(4/5)+self.buttonHeight//2)
        screen.blit(resumeSurf,resumeRect)
        menuText="Menu"
        menuFont=pygame.font.Font("font/AldotheApache.ttf",25)
        menuSurf=menuFont.render(menuText,True,WHITE)
        menuRect=menuSurf.get_rect()
        menuRect.center=(self.width*(1/3)-self.buttonWidth//2,self.height*(4/5)+self.buttonHeight//2)
        screen.blit(menuSurf,menuRect)
        
    # draw test Screen
    def drawTestScreen(screen,self):
        currentBeat=self.beatRange[self.beatRangeIndex]
        # draw background 
        screen.blit(self.background,(0,0))
        if self.testMode=="ready":
            testText="Press 's' to start testing %s(%d/%d)"%(currentBeat.beat,countTest(currentBeat.range),len(currentBeat.range))
        elif self.testMode=="test":
            testText="Testing..."
        # testing Text
        testFont=pygame.font.Font("font/BatmanForeverAlternate.ttf",20)
        testSurf=testFont.render(testText, True, WHITE)
        testRect=testSurf.get_rect()
        testRect.center=(self.width//2, self.height//4)
        screen.blit(testSurf,testRect)
        # put back button
        screen.blit(self.button,(self.width*(2/3), self.height*(3/4)))
        backText="Back"
        backFont=pygame.font.Font("font/AldotheApache.ttf",25)
        backSurf=backFont.render(backText,True,WHITE)
        backRect=backSurf.get_rect()
        backRect.center=(self.width*(2/3)+self.buttonWidth//2,self.height*(3/4)+self.buttonHeight//2)
        screen.blit(backSurf,backRect)
        # instruction Text
        if self.testMode=="ready":
            if self.testSuccess!=None:
                if self.testSuccess:
                    testResult="Recorded. "
                else:
                    testResult="Not Recorded. "
            else:
                testResult=""
        infoText=testResult+"Hit the %s when after pressing 's'"%currentBeat.beat
        infoFont=pygame.font.Font("font/BatmanForeverAlternate.ttf",15)
        infoSurf=infoFont.render(infoText, True, WHITE)
        infoRect=infoSurf.get_rect()
        infoRect.center=(self.width//2, self.height//2)
        screen.blit(infoSurf,infoRect)
        retestFont=pygame.font.Font("font/BatmanForeverAlternate.ttf",10)
        retestSurf=infoFont.render(self.testAgain, True, WHITE)
        retestRect=retestSurf.get_rect()
        retestRect.center=(self.width//2, self.height*(2/3))
        screen.blit(retestSurf,retestRect)
            
    def drawMusicMenuScreen(screen,self):
        # draw background
        screen.blit(self.background,(0,0))
        # draw info for clicking songs
        enterText="Enter any you want to play"
        enterFont=pygame.font.Font("font/BatmanForeverAlternate.ttf",25)
        enterSurf=enterFont.render(enterText,True,WHITE)
        enterRect=enterSurf.get_rect()
        enterRect.center=(self.width//2, self.height//4)
        screen.blit(enterSurf,enterRect)
        # print songs
        for index in range(len(self.songs)):
            fileText=self.songs[index].title
            fileFont=pygame.font.Font("font/BatmanForeverAlternate.ttf",20)
            fileSurf=fileFont.render(fileText,True,WHITE)
            fileRect=fileSurf.get_rect()
            fileRect.center=(self.width//2,self.height*(3/7)+self.longButtonH//2*index)
            if index==self.songIndex:
                screen.blit(self.longButtonA,(self.width//2-self.longButtonW//2,self.height*(3/7)-self.longButtonH//2+(self.longButtonH//2*index)))
            else:
                screen.blit(self.longButton,(self.width//2-self.longButtonW//2,self.height*(3/7)-self.longButtonH//2+(self.longButtonH//2*index)))
            screen.blit(fileSurf,fileRect)
        # draw back button to Test Mode
        posX,posY=self.width//15,self.height-self.height//5
        backImage=pygame.image.load("image/back.png")
        screen.blit(backImage,(posX,posY))

    def drawGameOverScreen(screen,self):
        # fill the background
        screen.blit(self.background,(0,0))
        # show result
        resultText="Result"
        resultFont=pygame.font.Font("font/BatmanForeverAlternate.ttf",25)
        resultSurf=resultFont.render(resultText,True,WHITE)
        resultRect=resultSurf.get_rect()
        resultRect.center=(self.width//2, self.height//4)
        screen.blit(resultSurf,resultRect)
        # show score
        scoreText="Score : %d"%self.score
        scoreFont=pygame.font.Font("font/BatmanForeverAlternate.ttf",20)
        scoreSurf=scoreFont.render(scoreText,True,WHITE)
        scoreRect=scoreSurf.get_rect()
        scoreRect.topleft=(self.width//4,self.height//3)
        screen.blit(scoreSurf,scoreRect)
        count=0
        # show performances
        for key in self.perfDic:
            keyText=key
            valueText=str(self.perfDic[key])
            keyValFont=pygame.font.SysFont("comicsansms",20)
            keyValSurf=keyValFont.render("%s: %s"%(keyText,valueText),True,WHITE)
            keyValRect=keyValSurf.get_rect()
            keyValRect.topleft=(self.width//4,self.height//3+(self.height//15)*(count+1))
            screen.blit(keyValSurf,keyValRect)
            count+=1
        # draw button
        screen.blit(self.button,(self.width*(2/3),self.height*(4/5)))
        screen.blit(self.button,(self.width*(1/3)-self.buttonWidth,self.height*(4/5)))
        # draw texts for buttons
        testText="Test"
        testFont=pygame.font.Font("font/AldotheApache.ttf",25)
        testSurf=testFont.render(testText, True, WHITE)
        testRect=testSurf.get_rect()
        testRect.center=(self.width*(2/3)+self.buttonWidth//2,self.height*(4/5)+self.buttonHeight//2)
        screen.blit(testSurf,testRect)
        menuText="Menu"
        menuFont=pygame.font.Font("font/AldotheApache.ttf",25)
        menuSurf=menuFont.render(menuText,True,WHITE)
        menuRect=menuSurf.get_rect()
        menuRect.center=(self.width*(1/3)-self.buttonWidth//2,self.height*(4/5)+self.buttonHeight//2)
        screen.blit(menuSurf,menuRect)
            
    def redrawAll(self, screen):
        if self.gameMode=="start":
            penbeatMax.drawStartScreen(screen,self)
        elif self.gameMode=="Test":
            penbeatMax.drawTestScreen(screen,self)
        elif self.gameMode=="Game":
            penbeatMax.drawGameScreen(screen,self)
        elif self.gameMode=="Paused":
            penbeatMax.drawPausedScreen(screen,self)
        elif self.gameMode=="Menu":
            penbeatMax.drawMusicMenuScreen(screen,self)
        elif self.gameMode=="Done":
            penbeatMax.drawGameOverScreen(screen,self)
#############
# Default functions
#############
    def isKeyPressed(self, key):
        ''' return whether a specific key is being held '''
        return self._keys.get(key, False)

    def __init__(self, width=600, height=400, fps=60, title="Pen Beat Max"):
        self.width = width
        self.height = height
        self.fps = fps
        self.title = title
        self.bgColor = BLACK
        pygame.init()

    def run(self):
        clock = pygame.time.Clock()
        screen = pygame.display.set_mode((self.width, self.height))
        previousFT = clock.get_time()
        current=0
        # set the title of the window
        pygame.display.set_caption(self.title)

        # stores all the keys currently being held down
        self._keys = dict()
        # call game-specific initialization
        self.init()
        pygame.mixer.pre_init(self.aubioRate, -16, self.aubioWidth, self.aubioChunk)
        pygame.mixer.init()
        penbeatMax.turnMusic(self)
        playing = True
        while playing:
            time=clock.tick(self.fps)
            current+=clock.get_time()
            self.mostAccurate+=current-previousFT
            previousFT=current
            self.timerFired(time)
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.mousePressed(*(event.pos))
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self.mouseReleased(*(event.pos))
                elif (event.type == pygame.MOUSEMOTION and
                      event.buttons == (0, 0, 0)):
                    self.mouseMotion(*(event.pos))
                elif (event.type == pygame.MOUSEMOTION and
                      event.buttons[0] == 1):
                    self.mouseDrag(*(event.pos))
                elif event.type == pygame.KEYDOWN:
                    self._keys[event.key] = True
                    self.keyPressed(event.key, event.mod)
                elif event.type == pygame.KEYUP:
                    self._keys[event.key] = False
                    self.keyReleased(event.key, event.mod)
                elif event.type == pygame.QUIT:
                    playing = False
            screen.fill(self.bgColor)
            self.redrawAll(screen)
            pygame.display.flip()

        pygame.quit()
        sys.exit()
            
    
def main():
    game = penbeatMax()
    game.run()

if __name__ == '__main__':
    main()