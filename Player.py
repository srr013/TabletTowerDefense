import Map
import wavegen


from kivy.uix.image import Image

playerhealth = 20
playermoney = 5000

class Player():
    def __init__(self):
        self.name = "player"
        self.health = playerhealth
        self.money = playermoney
        self.abilities = list()
        self.wavenum = 0
        self.gameover = False
        self.towerSelected = None
        self.tbbox = None
        self.wavestart = 999
        self.next_wave = False
        self.game_speed = 3
        self.screen = None
        self.pausetime = 0
        self.state = "Menu"
        self.restart = False
        self.score = 0
        self.newMoveList = False
        self.waveList = wavegen.wavegen() #[{'wavenum': 1, 'setnum': 1, 'enemytype': 'b', 'enemymods': []}, dict repeats]
        self.wavetime = Map.waveseconds
        self.wavetimeInt = int(Map.waveseconds)


    def die(self):
        '''Set gameover to True to reset the game'''
        self.gameover = True


player = Player()