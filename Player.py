from kivy.storage.dictstore import DictStore
from kivy.animation import Animation

import Map
import Wavegen
import Analytics
import EventDispatcher
import __main__

playerhealth = 20

class Player():
    def __init__(self):
        self.health = playerhealth
        self.money = 0
        self.gems = 0
        self.upgPathSelectLvl = 5
        self.abilities = list()
        self.wavenum = 0
        self.gameover = False
        self.towerSelected = None
        self.tbbox = None
        self.layout = None
        self.wavestart = 999
        self.next_wave = False
        self.pausetime = 0
        self.state = "Start"
        self.restart = False
        self.score = 0
        self.newMoveList = False
        self.wavetime = None
        self.wavetimeInt = None
        self.myDispatcher = EventDispatcher.EventDisp()
        self.analytics = Analytics.Analytics()
        self.store = DictStore('settings.txt')
        if self.store.exists('audio'):
            self.soundOn = self.store.get('audio')['soundOn']
            self.musicOn = self.store.get('audio')['musicOn']
        else:
            self.soundOn = True
            self.musicOn = True

    def setResources(self):
        if Map.mapvar.difficulty == 'easy':
            self.money = 2000
            self.gems = 3
            self.myDispatcher.Money = str(self.money)
            self.myDispatcher.Gems = str(self.gems)
        elif Map.mapvar.difficulty == 'medium':
            self.money = 1000
            self.gems = 3
            self.myDispatcher.Money = str(self.money)
            self.myDispatcher.Gems = str(self.gems)
        else:
            self.money = 300
            self.gems = 2
            self.myDispatcher.Money = str(self.money)
            self.myDispatcher.Gems = str(self.gems)
        self.myDispatcher.Score = str(self.score)
        self.myDispatcher.Timer = str(self.wavetimeInt)
        self.myDispatcher.Health = str(self.health)

    def setupCoinAnim(self):
        self.coinAnimating = False
        self.coinanim = Animation(pos=(__main__.ids.coinimage.x, __main__.ids.coinimage.y+20), duration=.1) + \
                         Animation(pos=(__main__.ids.coinimage.x, __main__.ids.coinimage.y), duration=.1)
        self.coinanim.on_complete(self.toggleCoinAnim)

    def toggleCoinAnim(self):
        self.coinAnimating = False

    def die(self):
        '''Set gameover to True to reset the game'''
        self.gameover = True

    def genWaveList(self):
        self.waveList, self.waveTypeList = Wavegen.wavegen()  # [{'wavenum': 1, 'setnum': 1, 'enemytype': 'b', 'enemymods': []}, dict repeats]
        self.wavetime = Map.mapvar.waveseconds
        self.wavetimeInt = int(Map.mapvar.waveseconds)

    def storeSettings(self):
        self.store.put('audio', soundOn=self.soundOn,musicOn=self.musicOn)
        self.store.put('gameplay', difficulty = Map.mapvar.difficulty, numpaths = Map.mapvar.numpaths, waveorder = Map.mapvar.waveOrder)


player = Player()
