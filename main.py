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

import pygame
import MainFunctions
import EventFunctions
import time
import Map
import Player
import Towers
import GUI_Kivy
import Keyboard_Kivy


from kivy.app import App
from kivy.uix.widget import Widget

from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.core.window import Window, WindowBase
from kivy.config import Config
Config.set('modules', 'touchring', '')

import cProfile
import pstats

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
        self.mainMenu = None
        self.pauseMenu = None
        self.wavetime = Map.waveseconds

    def menuFuncs(self, obj):
        if obj.text == 'Play':
            Player.player.state = 'Playing'
            self.remove_widget(self.mainMenu)
        if obj.text == 'Restart':
            MainFunctions.resetGame()
            Player.player.state = 'Playing'
            self.remove_widget(self.mainMenu)
        if obj.id == 'unpause':
            Player.player.state = 'Playing'
            self.remove_widget(self.pauseMenu)



    def dispMainMenu(self):
        if self.mainMenu == None:
            self.mainMenu = GUI_Kivy.mainMenu()
            for button in self.mainMenu.walk(restrict=True):
                button.bind(on_release=self.menuFuncs)
            self.add_widget(self.mainMenu)
        elif self.mainMenu.parent == None:
            self.add_widget(self.mainMenu)

    def dispPauseMenu(self):
        if self.pauseMenu == None:
            self.pauseMenu = GUI_Kivy.pauseMenu()
            for button in self.pauseMenu.walk(restrict=True):
                button.bind(on_release=self.menuFuncs)
            self.add_widget(self.pauseMenu)
        elif self.pauseMenu.parent == None:
            self.add_widget(self.pauseMenu)




    def update(self, dt):
        starttime = time.time()
        if Player.player.state == 'Menu':
            self.dispMainMenu()
            MainFunctions.updateGUI(self.wavetime)
        if Player.player.state == 'Paused':
            self.dispPauseMenu()
            MainFunctions.updateGUI(self.wavetime)
        if Player.player.state == 'Playing':
            Player.player.frametime = 5 / 60.0
            if Player.player.gameover:
                #need some sort of gameover screen. Wait on user to start new game.
                MainFunctions.resetGame()
                Player.player.gameover = False

            ##update path when appropriate
            if Map.mapvar.updatePath:
                MainFunctions.updatePath(Map.mapvar.openPath)

            if Player.player.next_wave:
                Player.player.bonus_score += self.wavetime * Player.player.wavenum
                EventFunctions.nextWave()
                Player.player.next_wave = False

            MainFunctions.workSenders()
            ##Check each tower and shoot at an enemy if one is in range
            MainFunctions.workTowers()
            ##Display explosions from any enemies killed in during previous frame
            MainFunctions.dispExplosions()
            ##Check if enemy is slowed and move the enemy
            MainFunctions.workEnemies()
            ##check for keyboard/Mouse input and take action based on those inputs
            MainFunctions.workShots()

            #MainFunctions.updateGUI(self.wavetime)
            selected = None

            ##if an icon is selected then display the tower + circle around it where the mouse is located
            if Player.player.towerSelected is not None:
                selected = Player.player.towerSelected
            ##if a tower is selected then display the circle around it
            if selected and Towers.Tower in selected.__class__.__bases__:
                MainFunctions.selectedTower(selected)

            if Player.player.wavenum > 0:
                self.wavetime -= Player.player.frametime

            if self.wavetime < .05:
                self.wavetime = Map.waveseconds
                Player.player.next_wave=True


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
        MainFunctions.makeUpgradeIcons()

        #create toolbars
        game.topBar = GUI_Kivy.gui.createTopBar()
        background.add_widget(game.topBar)
        background.add_widget(GUI_Kivy.gui.createTopSideBar())
        background.add_widget(GUI_Kivy.gui.createBottomSideBar())

        ##update path at start
        if Map.mapvar.updatePath == True:
            MainFunctions.updatePath(Map.mapvar.openPath)

        #this runs the game.update loop, which is used for handling the entire game
        Clock.schedule_interval(game.update,5/60)

        return game

if __name__ == '__main__':
    Window.size = (Map.winwid,Map.winhei)
    Main().run()
    # cProfile.run('Main().run()', 'cprofile_results')
    #
    # p = pstats.Stats('cprofile_results')
    # # sort by cumulative time in a function
    # p.sort_stats('cumulative').print_stats(10)
    # # sort by time spent in a function
    # p.sort_stats('time').print_stats(10)
