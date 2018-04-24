##########################################################################
# This code is the work of Scott Rossignol (srr0132@gmail.com)
# Additional credits for artwork and algorithms are in the Content Sources document
############################################################################

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.utils import platform
from kivy.graphics import *

import EventFunctions
import GUI
import MainFunctions
import Map
import Player
import Sound

import sys
import time
# import cProfile
# import pstats

class Background(Widget):
    '''the Background widget contains the basic Playfield'''

    def __init__(self, **kwargs):
        super(Background, self).__init__(**kwargs)
        self.size = Window.width, Window.height
        self.size_hint = (1, 1)
        self.layout = FloatLayout()
        self.layout.size = self.size
        self.add_widget(self.layout)

    def bindings(self, *args):
        self.size = Window.size
        self.layout.size = Window.size


class Game(Widget):
    '''The Game class handles menu actions and includes the games main Update loop'''

    def __init__(self, **kwargs):
        super(Game, self).__init__(**kwargs)
        # self._keyboard = Window.request_keyboard(Keyboard_Kivy._keyboard_closed, self)
        # self._keyboard.bind(on_key_up=Keyboard_Kivy._on_keyboard_up)
        self.mainMenu = None
        self.pauseMenu = None
        self.size_hint = (1, 1)
        self.framecount = -1
        self.frametime = 1 / 20.0
        Player.player.frametime = self.frametime

    def bindings(self, *args):
        self.size = Window.size
        if self.mainMenu:
            self.mainMenu.bindings()
            Map.mapvar.shaderRect.size = self.size

    def startFuncs(self):
        Player.player.analytics.gameTimeStart = time.time()
        Map.mapvar.getStartPoints()
        Player.player.genWaveList()
        GUI.gui.createWaveStreamer()
        Map.path.createPath()
        MainFunctions.buildNodeDicts()
        MainFunctions.updatePath()
        GUI.gui.removeAlert()

    def menuFuncs(self, obj):
        if obj.id == 'Play':
            Player.player.state = 'Playing'
            if Player.player.wavenum == 0 and obj.text == 'Play':
                self.startFuncs()
            else:
                self.Clock.schedule_interval(self.update, self.frametime)
                MainFunctions.startAllAnimation()
            GUI.gui.toggleButtons()
            self.remove_widget(self.mainMenu)
        elif obj.id == 'Restart':
            MainFunctions.resetGame()
            Player.player.state = 'Playing'
            self.Clock.schedule_interval(self.update, self.frametime)
            self.remove_widget(self.mainMenu)
            GUI.gui.toggleButtons()
            self.startFuncs()
        elif obj.id == 'Quit':
            Player.player.analytics.finalWave= Player.player.wavenum
            Player.player.analytics.gameTimeEnd = time.time()
            print Player.player.analytics._print()
            Main.get_running_app().stop()
            sys.exit()
        elif obj.id == 'pause':
            if Player.player.state == 'Paused':
                self.shaderRect.size = (0,0)
                Player.player.state = 'Playing'
                self.Clock.schedule_interval(self.update, self.frametime)
                MainFunctions.startAllAnimation()
                GUI.gui.toggleButtons()
                self.remove_widget(self.pauseMenu)
            else:
                Player.player.state = 'Paused'
        elif obj.id == 'menu':
            Player.player.state = 'Menu'
            self.dispMainMenu()
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
        return

    def dispMainMenu(self):
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
        if self.pauseMenu != None:
            if self.pauseMenu.parent:
                self.remove_widget(self.pauseMenu)
        GUI.gui.toggleButtons(active=False)
        MainFunctions.dispMessage()

    def dispPauseMenu(self):
        GUI.gui.toggleButtons(active=False, pause=True)
        if self.pauseMenu == None:
            self.pauseMenu = GUI.pauseMenu()
            for button in self.pauseMenu.walk(restrict=True):
                button.bind(on_release=self.menuFuncs)
            self.add_widget(self.pauseMenu)
        elif self.pauseMenu.parent == None:
            self.add_widget(self.pauseMenu)
        with Map.mapvar.background.canvas:
            Color(.2,.2,.2,.2)
            self.shaderRect = Rectangle(size=(Map.mapvar.playwid-Map.mapvar.squsize*2, Map.mapvar.playhei-Map.mapvar.squsize*2),
                      pos = (Map.mapvar.squsize*2, Map.mapvar.squsize*2))

    def update(self, dt):
        #print self.Clock.get_fps()
        if Player.player.state == 'Menu':
            if Player.player.wavenum == 0 and not GUI.gui.alertQueue:
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
                Player.player.sound.playSound(Player.player.sound.gameOver)
                Player.player.analytics.finalWave = Player.player.wavenum
                Player.player.analytics.gameTimeEnd = time.time()
                self.mainMenu = None
                Player.player.state = 'Menu'
                GUI.gui.addAlert("You Lose!", 'repeat')
                print Player.player.analytics._print()
                MainFunctions.resetGame()
                Player.player.gameover = False
            # Update path when appropriate
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
                GUI.gui.nextwaveButton.text = 'Next Wave'
                GUI.gui.nextwaveButton.color = [1,1,0,1]
                Player.player.wavetime -= Player.player.frametime
                Player.player.wavetimeInt = int(Player.player.wavetime)
                GUI.gui.myDispatcher.Timer = str(Player.player.wavetimeInt)
            if Player.player.wavetime < .05:
                Player.player.wavetime = int(Map.mapvar.waveseconds)
                GUI.gui.myDispatcher.Timer = str(Player.player.wavetime)
                Player.player.next_wave = True


class Main(App):
    """Instantiate required classes and variables and launch the game.update loop"""
    def on_pause(self):
        if Player.player.sound.music:
            Player.player.sound.music.stop()
        Player.player.state = 'Menu'

        return True

    def build(self):
        game = Game()
        if platform == 'linux':
            #Window.size = (1334,750) #tablet
            Window.size = (1280,720) #phone
        else:
            Window.fullscreen = 'auto'
        Window.bind(size=game.bindings)
        # general appearance updates
        background = Background()
        game.add_widget(background)
        map = Map.mapvar.loadMap()  # map is Map.mapvar.background
        background.add_widget(map)
        Window.bind(size=background.bindings)
        Window.bind(size=map.bindings)
        Window.bind(size=GUI.gui.bindings)
        ##create a list of available towers and icons for touch interaction
        MainFunctions.makeIcons()
        MainFunctions.makeUpgradeIcons()
        GUI.gui.initTopBar()
        GUI.gui.pauseButton.bind(on_release=game.menuFuncs)
        GUI.gui.menuButton.bind(on_release=game.menuFuncs)
        Map.mapvar.backgroundimg.add_widget(GUI.gui.rightSideButtons())
        game.bindings()
        Player.player.sound = Sound.MySound(Player.player.soundOn, Player.player.musicOn)
        Player.player.sound.playMusic()
        # This runs the game.update loop, which is used for handling the entire game
        game.Clock = Clock
        game.Clock.schedule_interval(game.update, game.frametime)
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
