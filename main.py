##########################################################################
# This code is the work of Scott Rossignol (srr0132@gmail.com)
# Additional credits for artwork and algorithms are in the Content Sources document
############################################################################

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
from kivy.core.window import Window
from kivy.config import Config
from kivy.properties import StringProperty
from kivy.graphics import *

#Config.set('modules', 'touchring', '')

# import cProfile
# import pstats

class Background(Widget):
    def __init__(self,**kwargs):
        super(Background,self).__init__(**kwargs)
        self.size = Window.width, Window.height
        self.size_hint = (1,1)
        self.layout = FloatLayout()
        self.layout.size = self.size
        self.add_widget(self.layout)

    def bindings(self, *args):
        self.size=Window.size
        self.layout.size = Window.size

class Game(Widget):
    def __init__(self, **kwargs):
        super(Game, self).__init__(**kwargs)
        #self._keyboard = Window.request_keyboard(Keyboard_Kivy._keyboard_closed, self)
        #self._keyboard.bind(on_key_up=Keyboard_Kivy._on_keyboard_up)
        self.mainMenu = None
        self.pauseMenu = None
        self.size_hint=(1,1)
        self.framecount=-1
        self.frametime = 1/20.0
        Player.player.frametime = self.frametime

    def bindings(self, *args):
        self.size=Window.size
        for child in self.children:
            child.size = Window.size
        if self.mainMenu:
                 self.mainMenu.bindings()

    def startFuncs(self):
        if not Map.mapvar.startpoint:
            Map.mapvar.getStartPoints()
            Player.player.genWaveList()
            GUI.gui.createWaveStreamer()
            Map.path.createPath()
            MainFunctions.updatePath()
            GUI.gui.removeAlert()
            GUI.gui.menuButton.disabled = False
            GUI.gui.pauseButton.disabled = False
            GUI.gui.nextwaveButton.disabled = False
            GUI.gui.enemyInfoButton.disabled = False

    def menuFuncs(self, obj):
        if obj.id == 'Play':
            Player.player.state = 'Playing'
            if Player.player.wavenum == 0:
                self.startFuncs()
            else:
                self.Clock.schedule_interval(self.update,self.frametime)
                MainFunctions.startAllAnimation()
            self.remove_widget(self.mainMenu)
        elif obj.id == 'Restart':
            MainFunctions.resetGame()
            Player.player.state = 'Playing'
            self.Clock.schedule_interval(self.update,self.frametime)
            self.remove_widget(self.mainMenu)
        elif obj.id == 'unpause':
            Player.player.state = 'Playing'
            self.Clock.schedule_interval(self.update,self.frametime)
            MainFunctions.startAllAnimation()
            self.remove_widget(self.pauseMenu)
        elif obj.id == 'onepath':
            Map.mapvar.numpaths = 1
        elif obj.id == 'twopath':
            Map.mapvar.numpaths = 2
        elif obj.id == 'threepath':
            Map.mapvar.numpaths = 3
        elif obj.id == 'easy':
            Map.mapvar.difficulty = 'easy'
        elif obj.id == 'medium':
            Map.mapvar.difficulty = 'medium'
        elif obj.id == 'hard':
            Map.mapvar.difficulty = 'hard'
        elif obj.id == 'standard':
            Map.mapvar.waveOrder = 'standard'
        elif obj.id == 'random':
            Map.mapvar.waveOrder = 'random'

    def dispMainMenu(self):
        GUI.gui.menuButton.disabled = True
        GUI.gui.pauseButton.disabled = True
        GUI.gui.nextwaveButton.disabled = True
        GUI.gui.enemyInfoButton.disabled = True
        if self.mainMenu == None:
            self.mainMenu = GUI.mainMenu()
            for button in self.mainMenu.walk(restrict=True):
                button.bind(on_release=self.menuFuncs)
            self.mainMenu.restartButton.disabled = True
            self.add_widget(self.mainMenu)
        elif self.mainMenu.parent == None:
            self.mainMenu.restartButton.disabled = False
            self.mainMenu.restartButton.text = 'Start New'
            self.mainMenu.startButton.text = 'Resume'
            self.add_widget(self.mainMenu)
        MainFunctions.dispMessage()

    def dispPauseMenu(self):
        if self.pauseMenu == None:
            self.pauseMenu = GUI.pauseMenu()
            for button in self.pauseMenu.walk(restrict=True):
                button.bind(on_release=self.menuFuncs)
            self.add_widget(self.pauseMenu)
        elif self.pauseMenu.parent == None:
            self.add_widget(self.pauseMenu)

    def update(self, dt):
        #print self.Clock.get_fps()
        if self.framecount < 2 :
            self.framecount += 1
        if Player.player.state == 'Menu':
            if self.framecount == 0:
                GUI.gui.addAlert("Welcome to Tablet TD!", 'repeat')
            if Player.player.wavenum > 0:
                self.Clock.unschedule(self.update)
                MainFunctions.stopAllAnimation()
            self.dispMainMenu()
        elif Player.player.state == 'Paused':
            self.dispPauseMenu()
            self.Clock.unschedule(self.update)
            MainFunctions.stopAllAnimation()
        elif Player.player.state == 'Playing':
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
            # MainFunctions.dispExplosions()
            MainFunctions.workEnemies()
            MainFunctions.workShots()
            MainFunctions.workDisp()

            if Player.player.wavenum > 0:
                Player.player.wavetime -= Player.player.frametime
                Player.player.wavetimeInt = int(Player.player.wavetime)
                GUI.gui.myDispatcher.Timer = str(Player.player.wavetimeInt)

            if Player.player.wavetime < .05:
                Player.player.wavetime = int(Map.mapvar.waveseconds)
                GUI.gui.myDispatcher.Timer = str(Player.player.wavetime)
                Player.player.next_wave=True


#the game's main loop
class Main(App):
    #instantiate required classes and variables
    def build(self):
        game = Game()
        #Window.size = (Map.mapvar.winwid, Map.mapvar.winhei)
        Window.fullscreen = 'auto'
        Window.bind(size=game.bindings)


        #general appearance updates
        background = Background()
        game.add_widget(background)
        map = Map.mapvar.loadMap() # map is Map.mapvar.background
        background.add_widget(map)
        Window.bind(size=background.bindings)
        Window.bind(size=map.bindings)
        Window.bind(size=GUI.gui.bindings)

        ##create a list of available towers and icons for touch interaction
        MainFunctions.makeIcons()
        MainFunctions.makeUpgradeIcons()

        # #create toolbars
        game.topBar = GUI.gui.createTopBar()
        game.add_widget(game.topBar)
        game.add_widget(GUI.gui.rightSideButtons())
        game.bindings()

        #this runs the game.update loop, which is used for handling the entire game
        game.Clock = Clock
        game.Clock.schedule_interval(game.update,game.frametime)
        return game


if __name__ == '__main__':
    Main().run()
    # cProfile.run('Main().run()', 'cprofile_results')
    #
    # p = pstats.Stats('cprofile_results')
    # # sort by cumulative time in a function
    # p.sort_stats('cumulative').print_stats(20)
    # # sort by time spent in a function
    # p.sort_stats('time').print_stats(20)
