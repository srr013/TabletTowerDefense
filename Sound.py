import os
import random
from kivy.core.audio import SoundLoader
import Player

class MySound():
    def __init__(self, sound, music):
        self.sound = sound
        self.music = music
        self.musicIndex = 0
        self.gameMusic1 = self.loadSound(os.path.join("sounds","Submarine.ogg"))
        self.gameMusic2 = self.loadSound(os.path.join("sounds", "Raw_Power.ogg"))
        self.gameMusic1.bind(on_stop=self.playMusic)
        self.gameMusic2.bind(on_stop=self.playMusic)
        self.musicList = [self.gameMusic1, self.gameMusic2]
        self.gameMusic1.volume = .6
        self.gameMusic2.volume = .6
        self.waveBeep = self.loadSound(os.path.join("sounds", "WaveBeep.wav"))
        self.gameOver = self.loadSound(os.path.join("sounds", "GameOver.wav"))
        self.hitBase = self.loadSound(os.path.join("sounds","hit.ogg"))

    def loadSound(self, path):
        #loads the sound to memory
        sound = SoundLoader.load(path)
        return sound

    def on_sound(self, instance, value):
        self.sound = value
        Player.player.soundOn = value
        Player.player.storeSettings()

    def on_music(self, instance, value):
        self.music = value
        self.playMusic()
        Player.player.musicOn = value
        Player.player.storeSettings()

    def playSound(self, sound, start=0):
        if self.sound:
            sound.play()
            if start != 0:
                sound.seek(start)

    def playMusic(self, *args):
        if self.music:
            if self.musicIndex == 0:
                self.musicIndex =  random.randint(0, 1)
            else:
                self.musicIndex = 1 if self.musicIndex == 0 else 0
            self.musicList[self.musicIndex].play()

        if not self.music:
            if self.musicList[self.musicIndex].state == 'play':
                self.musicList[self.musicIndex].stop()