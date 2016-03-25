import resource

import pygame.mixer

lastchannel=0
channels={}

sounds={}

def load_sound(name):
    global lastchannel

    path=resource.path("sound", name)
    
    channels[name]=pygame.mixer.Channel(lastchannel)
    lastchannel+=1

    snd=pygame.mixer.Sound(path)
    
    return snd

def play_sound(name):
    if not (name in sounds):
        sounds[name]=load_sound(name)

    channels[name].play(sounds[name])

def init():
    pygame.mixer.pre_init(44100, size=-16, channels=16)
