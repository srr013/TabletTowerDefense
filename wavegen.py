import localdefs
import os
import EventFunctions
import pygame
import localclasses
import random

def wavegen(player, enemylist):
    wave = 1
    set = 1 #a set is counted every X waves
    allwaves = []

    while wave < 100:
        enemy  = random(0, len(enemylist)-1)#selects a random enemy type

        #enemy properties are stored in the mapvar.mapdict. EventFunctions.nextwave also calls this dict.
        #need to replace the dict structure with an output from this wavegenerator. Setup a dict for each wave and return that dict
        #to towerdefense so it's accessible. Could also just stick this function in the player module.

        allwaves.append()


