#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/
#
# Original Coder: Austin Morgan (codenameduckfin@gmail.com)
# Version: 0.8
#
# If altering the code, please keep this comment box at least. Also, please
# comment all changes or additions with two pound signs (##), so I can tell what's
# been changed and what hasn't. Adding another comment box below this one with your
# name will insure any additions or changes you made that make it into the next version
# will be credited to you. Preferably, you'd leave your email and a little description
# of your changes, but that's not absolutely needed.
#
# License:
# All code and work contained within this file and folder and package is open for
# use, however please include at least a credit to me and any other coders working
# on this project.
#
#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/

##/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#
##
## Gabriel Lazarini Baptistussi (gabrielbap1@gmail.com)
##
## I just made a small change in localclasses.Enemy.move(), now the enemies
## have a different picture for each direction they are moving.
##
##/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#

import sys, os
import pygame
from pygame.locals import *
from localdefs import *
from localclasses import *
from mapmenu import pickMap
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

def mainmenu():
    application = thorpy.Application(size=(winwid, winhei), caption="Scott's Tower Defense")

    select_map = thorpy.make_button("Select Map", func=gameloop)  # launch the main function when you click this button

    # a button for leaving the application:
    quit_button = thorpy.make_button("Quit", func=pygame.quit)

    # a background which contains quit_button and useless_button
    menubackground = thorpy.Background.make(image = imgLoad(os.path.join('backgroundimgs','background1230x930.jpg')),
                                        elements=[select_map, quit_button], mode="")

    # automatic storage of the elements
    thorpy.store(menubackground)
    menu = thorpy.Menu(menubackground)  # create a menu on top of the background
    menu.play()  # launch the menu

def gameloop():
    pygame.init()
    pygame.mouse.set_visible(1)
    if player.restart == False or player.gameover == True:
        background = mapvar.loadMap(pickMap())
    else:
        background = mapvar.backgroundimg
    screen = pygame.display.set_mode((winwid,winhei))
    player.screen = screen
    clock = pygame.time.Clock()
    genEnemyImageArray()
    run=True #Run loop
    wavestart = 999
    selected = None #Nothing is selected
    mapvar.getPathProperties()
    thorpy.set_theme('human')

    ##create a list of available towers to add to the bottom right tower selection window
    MainFunctions.makeIcons()

    ##initialize Thorpy
    if player.restart != True and player.gameover != True:
        guiMenus = MainFunctions.getGUI(0)

    font = pygame.font.Font(None,20)
    frametime = player.game_speed/60.0
    timer = Timer()
    player.restart = False
    player.gameover = False

    while run:
        starttime = time.time()
        if player.restart ==True:
            MainFunctions.resetGame()
            gameloop()
        if player.gameover == True:
            #need some sort of gameover screen. Wait on user to start new game.
            MainFunctions.resetGame()
            mainmenu()
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
            player.wavenum, wavestart = EventFunctions.nextWave(player.wavenum, Sender, starttime)
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

mainmenu()

#Thanks to everyone who looks over this code, or tests this thing out. Feel free
#to contact me at the email address listed above with any questions, comments, or
#your own set of changes. I've wanted to do a game like this for a while, so I'll
#stay committed as long as it has some interest in the community.

#Have a nice day :)