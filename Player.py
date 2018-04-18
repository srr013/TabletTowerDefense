from kivy.storage.dictstore import DictStore
import Map
import Wavegen
import Analytics

playerhealth = 20
playermoney = 10000


class Player():
    def __init__(self):
        # self.name = "player"
        self.health = playerhealth
        self.money = playermoney
        self.gems = 5
        self.upgPathSelectLvl = 2
        self.abilities = list()
        self.wavenum = 0
        self.gameover = False
        self.towerSelected = None
        self.tbbox = None
        self.layout = None
        self.wavestart = 999
        self.next_wave = False
        # self.game_speed = 3
        # self.screen = None
        self.pausetime = 0
        self.state = "Menu"
        self.restart = False
        self.score = 0
        self.newMoveList = False
        self.wavetime = None
        self.wavetimeInt = None
        self.analytics = Analytics.Analytics()
        self.store = DictStore('settings.txt')
        if self.store.exists('audio'):
            self.soundOn = self.store.get('audio')['soundOn']
            self.musicOn = self.store.get('audio')['musicOn']
        else:
            self.soundOn = True
            self.musicOn = True

    def die(self):
        '''Set gameover to True to reset the game'''
        self.gameover = True

    def genWaveList(self):
        self.waveList, self.waveTypeList = Wavegen.wavegen()  # [{'wavenum': 1, 'setnum': 1, 'enemytype': 'b', 'enemymods': []}, dict repeats]
        self.wavetime = Map.mapvar.waveseconds
        self.wavetimeInt = int(Map.mapvar.waveseconds)

    def storeSettings(self):
        self.store.put('audio', soundOn=self.soundOn,musicOn=self.musicOn)

player = Player()
