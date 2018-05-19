##########################################################################
# This code is the work of Scott Rossignol (srr0132@gmail.com)
# Additional credits for artwork and algorithms are in the Content Sources document
############################################################################
import time
# import cProfile
# import pstats

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.utils import platform
from kivy.graphics import *
from kivy.properties import NumericProperty, ObjectProperty

import EventFunctions
import MainFunctions
import Map
import Player
import Sound
import Messenger

global app, ids

class Game(Widget):
    '''The Game class handles menu actions and includes the game's main Update loop'''
    score = NumericProperty(0)
    scrwid = NumericProperty(0)
    squsize = NumericProperty(0)
    playhei = NumericProperty(0)
    playwid = NumericProperty(0)
    border = NumericProperty(0)
    squborder = NumericProperty(0)
    playfield = ObjectProperty(None)
    menuBtn = ObjectProperty(None)
    pauseBtn = ObjectProperty(None)
    playBtn = ObjectProperty(None)

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
        self.shaderRect = None
        self.scrwid = Window.width
        self.scrhei = Window.height
        self.size = (self.scrwid, self.scrhei)
        self.squsize = self.scrwid / 34
        self.playhei = self.squsize * 16  # the top line of the play area should always be 16 squsize from the bottom
        self.playwid = self.squsize * 32
        self.border = 2 * self.squsize
        self.squborder = 1
        self.test = 0

    def bindings(self, *args):
        self.size = Window.size
        self.scrwid = Window.width
        self.scrhei = Window.height
        self.size = (self.scrwid, self.scrhei)
        self.squsize = self.scrwid / 34
        self.playhei = self.squsize * 16  # the top line of the play area should always be 16 squsize from the bottom
        self.playwid = self.squsize * 32
        self.border = 2 * self.squsize
        self.squborder = 1


    def startFuncs(self):
        global app, ids
        app = App.get_running_app()
        ids = self.ids
        if Player.player.state == 'Restart':
            self.pause_game()
            self.clock = self.Clock.schedule_interval(self.update, self.frametime)
        Player.player.state = 'Playing'
        Player.player.analytics.gameTimeStart = time.time()
        Map.mapvar.getStartPoints()
        Messenger.messenger.createAlertStreamer()
        Player.player.genWaveList()
        ids.wavestreamer.createWaveStreamer()
        Map.path.createPath()
        MainFunctions.buildNodeDicts()
        MainFunctions.updatePath()
        Messenger.messenger.removeAlert()
        Player.player.setResources()
        Player.player.setupCoinAnim()
        Player.player.storeSettings()

    def start_game(self):
        self.screenmanager.current = 'game'
        self.startFuncs()

    def togglePauseShader(self):
        if Player.player.state == 'Paused':
            if not self.shaderRect:
                with Map.mapvar.background.canvas.before:
                    Color(.2,.2,.2,.2)
                    self.shaderRect = Rectangle(size=(Map.mapvar.playwid-Map.mapvar.squsize*2, Map.mapvar.playhei-Map.mapvar.squsize*2),
                              pos = (0,0))
                self.pauseLabel = Label(text='Game Paused. Press Resume.', font_size = self.scrwid * .05, color = (1,0,0,1), pos = (0,self.scrhei*-.3))
            Map.mapvar.background.add_widget(self.pauseLabel)
        elif Player.player.state == 'Playing' or Player.player.state == 'Start' or Player.player.state == 'Restart':
            if self.shaderRect:
                Map.mapvar.background.canvas.before.remove(self.shaderRect)
                self.shaderRect = None
                Map.mapvar.background.remove_widget(self.pauseLabel)

    def pause_game(self, pause = False):
        if Player.player.state == 'Playing' or pause:
            Player.player.state = 'Paused'
            if self.screenmanager.current_screen.name == 'game':
                ids.play.disabled = True
                ids.play.opacity = 0
                ids.pause.text = 'Resume'
        elif Player.player.state == 'Restart':
            if self.screenmanager.current_screen.name == 'game':
                ids.play.disabled = False
                ids.play.opacity = 1
                ids.pause.text = 'Pause'
        else: #unpause
            if self.screenmanager.current_screen.name == 'game':
                Player.player.state = 'Playing'
                self.clock = self.Clock.schedule_interval(self.update, self.frametime)
                MainFunctions.startAllAnimation()
                ids.pause.text = 'Pause'
                if ids.play.disabled == True:
                    ids.play.disabled = False
                    ids.play.opacity = 1
        self.togglePauseShader()

    def change_screens(self, to_screen):
        current_screen = self.screenmanager.current_screen.name
        if current_screen == to_screen:
            return
        if current_screen == 'game':
            if Player.player.state == 'Playing':
                self.pause_game()
            self.screenmanager.current = to_screen
        if to_screen == 'game':
            if Player.player.state == 'Start' or Player.player.state == 'Restart':
                self.start_game()
                return
        self.screenmanager.current = to_screen
        if to_screen == 'info':
            if current_screen == 'game':
                Map.mapvar.background.removeAll()
            self.screenmanager.current_screen.ids.infopanel.switch_to(
                self.screenmanager.current_screen.ids.infopanel.getDefaultTab())
        elif to_screen == 'mainmenu':
            if Player.player.state != 'Start':
                self.screenmanager.current_screen.ids.startbutton.text = 'Resume'
                self.screenmanager.current_screen.ids.restartbutton.disabled = False
                self.screenmanager.current_screen.ids.restartbutton.opacity = 1
            else:
                self.screenmanager.current_screen.ids.startbutton.text = 'Play'
                self.screenmanager.current_screen.ids.restartbutton.disabled = True
                self.screenmanager.current_screen.ids.restartbutton.opacity = 0

    def nextWave(self):
        if ids.play.text == 'Start':
            ids.play.text = 'Next Wave'
        ids.wavestreamer.nextWave()


    def update(self, dt):
        #print self.Clock.get_fps()
        if Player.player.state == 'Paused':
            self.clock.cancel()
            MainFunctions.stopAllAnimation()
        elif Player.player.state == 'Playing':
            if Player.player.gameover:
                Player.player.state = 'Start'
                Player.player.sound.playSound(Player.player.sound.gameOver)
                Player.player.analytics.finalWave = Player.player.wavenum
                Player.player.analytics.score = Player.player.score
                Player.player.analytics.gameTimeEnd = time.time()
                self.mainMenu = None
                self.change_screens('mainmenu')
                Player.player.analytics.updateData()
                Player.player.analytics.store_data()
                Player.player.analytics._print()
                MainFunctions.resetGame()
            if Map.mapvar.updatePath:
                MainFunctions.updatePath()
            if Player.player.next_wave:
                EventFunctions.nextWave()
            MainFunctions.workSenders()
            MainFunctions.workTowers()
            MainFunctions.workEnemies()
            MainFunctions.workShots()
            MainFunctions.workDisp()
            if Player.player.wavenum > 0:
                Player.player.wavetime -= Player.player.frametime
                Player.player.wavetimeInt = int(Player.player.wavetime)
                Player.player.myDispatcher.Timer = str(Player.player.wavetimeInt)
            if Player.player.wavetime < .05:
                Player.player.wavetime = int(Map.mapvar.waveseconds)
                Player.player.myDispatcher.Timer = str(Player.player.wavetime)
                Player.player.next_wave = True


class Main(App):
    """Instantiate required classes and variables and launch the game.update loop"""
    def on_pause(self):
        if Player.player.sound.music:
            Player.player.sound.music.stop()
        if Player.player.state == 'Playing':
            Map.mapvar.background.removeAll()
            self.root.pause_game(pause = True)
            print "pausing on suspend"
        return True
    def on_resume(self):
        print "Resuming game",self.root.shaderRect

    def build(self):
        game = Game()
        if platform == 'linux':
            #Window.size = (600,300) #phone
            Window.size = (1280,720) #tablet
        else:
            Window.fullscreen = 'auto'
        Window.bind(size=game.bindings)
        Map.mapvar.background = game.ids.playfield
        Map.mapvar.loadMap()
        MainFunctions.makeIcons()
        MainFunctions.makeUpgradeIcons()
        game.bindings()
        game.screenmanager = game.ids.sm
        Player.player.sound = Sound.MySound(Player.player.soundOn, Player.player.musicOn)
        Player.player.sound.playMusic()
        # This runs the game.update loop, which is used for handling the entire game
        game.Clock = Clock
        game.clock = game.Clock.schedule_interval(game.update, game.frametime)
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
