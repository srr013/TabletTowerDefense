##########################################################################
# This code is the work of Scott Rossignol (srr0132@gmail.com)
# Additional credits for artwork and algorithms are in the Content Sources document
#
############################################################################

import pygame
import MainFunctions
import EventFunctions
import time
import Map
import Player
import Towers
import GUI
import Keyboard_Kivy


from kivy.app import App
from kivy.uix.widget import Widget

from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.core.window import Window, WindowBase
from kivy.config import Config
from kivy.properties import StringProperty

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
            self.mainMenu = GUI.mainMenu()
            for button in self.mainMenu.walk(restrict=True):
                button.bind(on_release=self.menuFuncs)
            self.add_widget(self.mainMenu)
        elif self.mainMenu.parent == None:
            self.add_widget(self.mainMenu)

    def dispPauseMenu(self):
        if self.pauseMenu == None:
            self.pauseMenu = GUI.pauseMenu()
            for button in self.pauseMenu.walk(restrict=True):
                button.bind(on_release=self.menuFuncs)
            self.add_widget(self.pauseMenu)
        elif self.pauseMenu.parent == None:
            self.add_widget(self.pauseMenu)




    def update(self, dt):
        if Player.player.state == 'Menu':
            self.dispMainMenu()
        if Player.player.state == 'Paused':
            self.dispPauseMenu()
        if Player.player.state == 'Playing':
            Player.player.frametime = 5 / 60.0
            if Player.player.gameover:
                #need some sort of gameover screen. Wait on user to start new game.
                MainFunctions.resetGame()
                Player.player.gameover = False

            ##update path when appropriate
            if Map.mapvar.updatePath:
                MainFunctions.updatePath()

            if Player.player.next_wave:
                EventFunctions.nextWave()

            MainFunctions.workSenders()
            MainFunctions.workTowers()
            MainFunctions.dispExplosions()
            MainFunctions.workEnemies()
            MainFunctions.workShots()

            if Player.player.wavenum > 0:
                Player.player.wavetime -= Player.player.frametime
                Player.player.wavetimeInt = int(Player.player.wavetime)
                GUI.gui.myDispatcher.Timer = str(Player.player.wavetimeInt)

            if Player.player.wavetime < .05:
                Player.player.wavetime = int(Map.waveseconds)
                GUI.gui.myDispatcher.Timer = str(Player.player.wavetime)
                Player.player.next_wave=True


#the game's main loop
class Main(App):
    #instantiate required classes and variables
    def build(self):
        #pygame.init()
        self.game = Game()

        #general appearance updates
        background = Background()
        self.game.add_widget(background)
        map = Map.mapvar.loadMap("Pathfinding")
        background.add_widget(map)

        ##create a list of available towers and icons for touch interaction
        MainFunctions.makeIcons()
        MainFunctions.makeUpgradeIcons()

        #create toolbars
        self.game.topBar = GUI.gui.createTopBar()
        map.add_widget(self.game.topBar)
        #map.add_widget(GUI_Kivy.gui.createTopSideBar())
        #map.add_widget(GUI_Kivy.gui.createBottomSideBar())

        ##update path at start
        if Map.mapvar.updatePath == True:
            MainFunctions.updatePath()

        #this runs the game.update loop, which is used for handling the entire game
        Clock.schedule_interval(self.game.update,5/60)

        return self.game

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
