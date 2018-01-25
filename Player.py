import os.path
import math
import os
import sys
import pygame
import threading
import time
from sys import exit as sysexit
from pygame.locals import *
import pathfinding
import Map
import wavegen


from kivy.uix.image import Image

playerhealth = 20
playermoney = 50

class Player():
    def __init__(self):
        self.name = "player"
        self.health = playerhealth
        self.money = playermoney
        self.abilities = list()
        self.wavenum = 0
        self.gameover = False
        self.towerSelected = None
        self.tbbox = None
        self.wavestart = 999
        self.next_wave = False
        self.game_speed = 3
        self.screen = None
        self.pausetime = 0
        self.state = "Menu"
        self.restart = False
        self.kill_score = 0
        self.bonus_score = 0
        self.waveList = wavegen.wavegen() #[{'wavenum': 1, 'setnum': 1, 'enemytype': 'b', 'enemymods': []}, dict repeats]


        #Legacy code handling player access to towers and attributes.
        self.modDict = dict()
        self.modDict['towerCostMod'] = 0
        self.modDict['towerRangeMod'] = 0
        self.modDict['towerDamageMod'] = 0
        self.modDict['towerSpeedMod'] = 0

        self.modDict['fighterCostMod'] = 0
        self.modDict['fighterRangeMod'] = 0
        self.modDict['fighterDamageMod'] = 0
        self.modDict['fighterSpeedMod'] = 0

        self.modDict['archerCostMod'] = 0
        self.modDict['archerRangeMod'] = 0
        self.modDict['archerDamageMod'] = 0
        self.modDict['archerSpeedMod'] = 0

        self.modDict['mineCostMod'] = 0
        self.modDict['mineRangeMod'] = 0
        self.modDict['mineDamageMod'] = 0
        self.modDict['mineSpeedMod'] = 0

        self.modDict['slowCostMod'] = 0
        self.modDict['slowRangeMod'] = 0
        self.modDict['slowDamageMod'] = 0
        self.modDict['slowSpeedMod'] = 0

        self.modDict['antiairCostMod'] = 0
        self.modDict['antiairRangeMod'] = 0
        self.modDict['antiairDamageMod'] = 0
        self.modDict['antiairSpeedMod'] = 0

        self.modDict['towerAbilities'] = set()
        self.modDict['towerSellMod'] = 0
        self.modDict['towerAccess'] = list(('Fighter','Archer','Mine','Slow',"AntiAir"))

        self.modDict['towerAbilities'].add("Sell")
        self.modDict['towerAbilities'].add("AddFighter")
        self.modDict['towerAbilities'].add("RemoveFighter")
        self.modDict['towerAbilities'].add("ExtraDamage1")
        self.modDict['towerAbilities'].add("ExtendRange1")

    def die(self):
        '''Set gameover to True to reset the game'''
        self.gameover = True

    def game_speed_update(change=0, keydown=False):
        pass


player = Player()