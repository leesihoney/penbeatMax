#! /usr/bin/env python
# the code is from https://github.com/aubio/aubio/blob/master/python/demos/demo_bpm_extract.py
# used for Fall 2017 15-112 Term project by Siheon Lee
from aubio import source, tempo
from numpy import median, diff
import os

def getFileBpm(path, parameter=None):
    """ Calculate the beats per minute (bpm) of a given file.
        path: path to the file
        param: dictionary of parameters
    """
    if parameter is None:
        parameter = {}
    # default:
    samplerate, win_s, hop_s = 44100, 1024, 512
    if 'mode' in parameter:
        if parameter.mode in ['super-fast']:
            # super fast
            samplerate, win_s, hop_s = 4000, 128, 64
        elif parameter.mode in ['fast']:
            # fast
            samplerate, win_s, hop_s = 8000, 512, 128
        elif parameter.mode in ['default']:
            pass
        else:
            print("unknown mode {:s}".format(parameter.mode))
    # manual settings
    if 'samplerate' in parameter:
        samplerate = parameter.samplerate
    if 'win_s' in parameter:
        win_s = parameter.win_s
    if 'hop_s' in parameter:
        hop_s = parameter.hop_s

    s = source(path, samplerate, hop_s)
    samplerate = s.samplerate
    o = tempo("specdiff", win_s, hop_s, samplerate)
    # List of beats, in samples
    beats = []
    # Total number of frames read
    total_frames = 0

    while True:
        samples, read = s()
        is_beat = o(samples)
        if is_beat:
            this_beat = o.get_last_ms()
            beats.append(this_beat)
            #if o.get_confidence() > .2 and len(beats) > 2.:
            #    break
        total_frames += read
        if read < hop_s:
            break
    def beats_to_bpm(beats, path):
        # if enough beats are found, convert to periods then to bpm
        if len(beats) > 1:
            if len(beats) < 4:
                print("few beats found in {:s}".format(path))
            bpms = 60./diff(beats)
            return median(bpms)
        else:
            print("not enough beats found in {:s}".format(path))
            return 0
    return beats_to_bpm(beats, path)
    
# append the middle values for the list
def calculate(lst):
    array=diff(lst)
    for i in range(len(array)):
        newI=2*i+1
        value=array[i]/2
        lst.insert(newI,lst[i]+value)
    return lst
def getBeats(path, parameter=None):
    """ Calculate the beats per minute (bpm) of a given file.
        path: path to the file
        param: dictionary of parameters
    """
    if parameter is None:
        parameter = {}
    # default:
    samplerate, win_s, hop_s = 44100, 1024, 512
    if 'mode' in parameter:
        if parameter.mode in ['super-fast']:
            # super fast
            samplerate, win_s, hop_s = 4000, 128, 64
        elif parameter.mode in ['fast']:
            # fast
            samplerate, win_s, hop_s = 8000, 512, 128
        elif parameter.mode in ['default']:
            pass
        else:
            print("unknown mode {:s}".format(parameter.mode))
    # manual settings
    if 'samplerate' in parameter:
        samplerate = parameter.samplerate
    if 'win_s' in parameter:
        win_s = parameter.win_s
    if 'hop_s' in parameter:
        hop_s = parameter.hop_s

    s = source(path, samplerate, hop_s)
    samplerate = s.samplerate
    o = tempo("specdiff", win_s, hop_s, samplerate)
    # List of beats, in samples
    beats = []
    # Total number of frames read
    totalFrames = 0

    while True:
        # read the sample of the song
        samples, read = s()
        # beat detection
        isBeat = o(samples)
        if isBeat:
            thisBeat = o.get_last_ms()
            # stores the time in milliseconds when beat happened
            beats.append(thisBeat)
            #if o.get_confidence() > .2 and len(beats) > 2.:
            #    break
        totalFrames += read
        if read < hop_s:
            break
    return beats


