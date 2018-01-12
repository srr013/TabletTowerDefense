##########################################################################
# This code is the work of Scott Rossignol (srr0132@gmail.com)
# It was adapted from an open source Tower Defense game, info below.
# Additional credits for artwork and algorithms are in the Content Sources document
#
# License:
# All code and work contained within this file and folder and package is open for
# use, however please include at least a credit to me and any other coders working
# on this project.

#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/
#Original source credit:
# Base Coder: Austin Morgan (codenameduckfin@gmail.com)
# Version: 0.8
# Legacy code: https://sourceforge.net/projects/ppgtd/
#
#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/


import sys, os
import pygame
from pygame.locals import *
from localdefs import *
from localclasses import *
from SenderClass import Sender
import MainFunctions
import EventFunctions
import time
import thorpy
from GUI import *
import Animation


x = 300
y = 0
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x,y)

#the game's main loop
def gameloop():
    #instantiate required classes and variables
    application = thorpy.Application(size=(winwid, winhei), caption="Scott's Tower Defense")
    thorpy.set_theme('human')
    pygame.init()
    pygame.mouse.set_visible(1)
    background = mapvar.loadMap("Pathfinding")
    screen = pygame.display.set_mode((winwid,winhei))
    player.screen = screen
    clock = pygame.time.Clock()
    run=True #Run loop
    wavestart = 999
    selected = None #Nothing is selected
    mapvar.getPathProperties()


    ##create a list of available towers to add to the bottom right tower selection window
    MainFunctions.makeIcons()

    ##initialize Thorpy
    if player.gameover != True:
        guiMenus = MainFunctions.getGUI(0)

    font = pygame.font.Font(None,20)
    frametime = player.game_speed/60.0
    timer = Timer()
    player.gameover = False

    while run:
        starttime = time.time()
        if player.gameover == True:
            #need some sort of gameover screen. Wait on user to start new game.
            MainFunctions.resetGame()
            gameloop()
        ##update path when appropriate
        if mapvar.updatePath == True:
            background = MainFunctions.updatePath(mapvar.openPath)
        ##Blit screen to background, increment clock 30 ms
        MainFunctions.tickAndClear(clock, background)
        ##Sends enemies based on a prior "n" press
        MainFunctions.workSenders(frametime)
        ##Check each tower and shoot at an enemy if one is in range
        MainFunctions.workTowers(frametime)
        ##Blit towers to screen
        MainFunctions.dispStructures()
        ##Display explosions from any enemies killed in during previous frame
        MainFunctions.dispExplosions()
        ##Check if enemy is slowed and move the enemy
        MainFunctions.workEnemies(frametime)
        ##handle GUI blitting
        MainFunctions.updateGUI(timer.timer)
        ##update menu for thorpy reactions
        menu = thorpy.Menu(MainFunctions.updateMenu())
        ##check for keyboard/Mouse input and take action based on those inputs
        MainFunctions.workShots()
        ##work events from user input
        selected,wavestart=MainFunctions.workEvents(selected, wavestart, menu)
        if player.paused == True:
            localdefs.pauseGame()
        if player.next_wave == True:
            player.bonus_score += timer.timer * player.wavenum
            wavestart = EventFunctions.nextWave(Sender, starttime)
            player.next_wave = False
        ##update the wave timer
        if timer.updateTimer(wavestart):
            wavestart = EventFunctions.nextWave(Sender, starttime)
        ##Blit alerts to the screen
        MainFunctions.dispText()

        ##if an icon is selected then display the tower + circle around it where the mouse is located
        if player.towerSelected is not None:
            selected = player.towerSelected
        if (selected and selected.__class__ == Icon):
            selected = MainFunctions.selectedIcon(selected)
        ##if a tower is selected then display the circle around it
        if selected and Tower in selected.__class__.__bases__:
            MainFunctions.selectedTower(selected)

        pygame.display.flip()


        frametime = (time.time() - starttime - player.pausetime) * player.game_speed
        player.pausetime = 0

gameloop()