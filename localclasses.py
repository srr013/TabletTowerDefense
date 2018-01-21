import pygame
import os
import sys
from pygame.locals import *
import random
import time
import Towers
import math, operator
import Animation
import Utilities
import Player
import Map
import localdefs




class Timer():
    def __init__(self):
        '''Instantiate a timer class for wave length and sending new waves'''
        self.timer = 0
        self.wave_length = 11
        self.curr_wave_length= int(self.wave_length)

    def updateTimer(self):
        '''Updates the timer based on pause events and time'''
        if Player.player.wavestart == 999:
            self.timer = Player.player.wavestart
            return False

        else:
            if Player.player.pausetime > 0:
                self.curr_wave_length += Player.player.pausetime
                return False
            else:
                self.timer = (Player.player.wavestart + self.curr_wave_length) - time.time()

        if self.timer <= 0:
            self.timer = (Player.player.wavestart + self.wave_length) - time.time()
            self.curr_wave_length = int(self.wave_length)
            return True

        return False

wavetimer = Timer()