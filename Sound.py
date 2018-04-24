import os
import random
from kivy.core.audio import SoundLoader
import Player

class MySound():
    def __init__(self, sound, music):
        self.sound = sound
        self.music = music
        self.musicPlaying = False
        self.gameMusic1 = self.loadSound(os.path.join("sounds","Submarine.mp3"))
        self.gameMusic2 = self.loadSound(os.path.join("sounds", "Raw_Power.mp3"))
        self.gameMusic1.volume = .6
        self.gameMusic2.volume = .6
        self.waveBeep = self.loadSound(os.path.join("sounds", "WaveBeep.wav"))
        self.gameOver = self.loadSound(os.path.join("sounds", "GameOver.wav"))
        self.hitBase = self.loadSound(os.path.join("sounds","hit.mp3"))
        self.musicSelect = 0

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
            self.gameMusic1.bind(on_stop=self.playMusic)
            self.gameMusic2.bind(on_stop=self.playMusic)
            self.musicPlaying = True
            if not self.musicSelect:
                x = str(random.randint(1, 2))
                self.musicSelect = '1' if x == '2' else '1'
            else:
                x = self.musicSelect
            eval("self.gameMusic" + x + ".play()")

        if not self.music and self.musicPlaying:
            self.gameMusic1.unbind(on_stop=self.playMusic)
            self.gameMusic2.unbind(on_stop=self.playMusic)
            self.gameMusic1.stop()
            self.musicPlaying = False
