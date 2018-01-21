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
import localdefs
import localclasses
from SenderClass import Sender
import MainFunctions
import EventFunctions
import time
import Animation
import Map
import Player
import Towers
import GUI_Kivy
import Keyboard_Kivy
import Utilities

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.image import Image
from kivy.properties import NumericProperty,ReferenceListProperty,ObjectProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.core.window import Window, WindowBase
from kivy.graphics import *
from functools import partial
from random import randint
from kivy.config import Config
Config.set('modules', 'touchring', '')

class Background(Widget):
    def __init__(self,**kwargs):
        super(Background,self).__init__(**kwargs)
        self.size = Window.width, Window.height
        self.layout = FloatLayout()
        self.layout.size = self.size
        self.add_widget(self.layout)

class Game(Widget):

    def __init__(self, **kwargs):
        super(Game, self).__init__(**kwargs)
        self._keyboard = Window.request_keyboard(Keyboard_Kivy._keyboard_closed, self)
        self._keyboard.bind(on_key_up=Keyboard_Kivy._on_keyboard_up)

    def update(self, dt):
        if Player.player.gameover == True:
            #need some sort of gameover screen. Wait on user to start new game.
            MainFunctions.resetGame()
            Player.player.gameover = False

        ##update path when appropriate
        if Map.mapvar.updatePath == True:
            MainFunctions.updatePath(Map.mapvar.openPath)

        if Player.player.next_wave == True:
            Player.player.bonus_score += localclasses.wavetimer.timer * Player.player.wavenum
            EventFunctions.nextWave(Sender, 0)
            Player.player.next_wave = False


        starttime = time.time()
        Player.player.frametime = 1 / 60.0  # broke the pause and speed change functions with this change
        Player.player.pausetime = 0
        MainFunctions.workSenders()
        ##Check each tower and shoot at an enemy if one is in range
        MainFunctions.workTowers()
        ##Display explosions from any enemies killed in during previous frame
        MainFunctions.dispExplosions()
        ##Check if enemy is slowed and move the enemy
        MainFunctions.workEnemies()
        ##check for keyboard/Mouse input and take action based on those inputs
        MainFunctions.workShots()

        selected = None
        if Player.player.paused == True:
            localdefs.pauseGame()
        ##update the wave timer
        #if localclasses.wavetimer.updateTimer():
        #    EventFunctions.nextWave(Sender, starttime)
        ##if an icon is selected then display the tower + circle around it where the mouse is located
        if Player.player.towerSelected is not None:
            selected = Player.player.towerSelected
        ##if a tower is selected then display the circle around it
        if selected and Towers.Tower in selected.__class__.__bases__:
            MainFunctions.selectedTower(selected)





#the game's main loop
class Main(App):
    #instantiate required classes and variables
    def build(self):
        pygame.init()
        game = Game()

        #general appearance updates
        background = Background()
        game.add_widget(background)
        map = Map.mapvar.loadMap("Pathfinding")
        background.add_widget(map)

        ##create a list of available towers to add to the bottom tower buttons
        MainFunctions.makeIcons()

        #create toolbars
        #background.add_widget(GUI_Kivy.createBottomBar())
        background.add_widget(GUI_Kivy.createTopBar())

        ##update path at start
        if Map.mapvar.updatePath == True:
            MainFunctions.updatePath(Map.mapvar.openPath)

        #this runs the game.update loop, which is used for handling the entire game
        Clock.schedule_interval(game.update,1/60)
        return game

if __name__ == '__main__':
    Window.size = (Map.winwid,Map.winhei)
    Main().run()