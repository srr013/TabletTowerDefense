import os
from kivy.core.audio import SoundLoader
import Player

class MySound():
    def __init__(self, sound, music):
        self.sound = sound
        self.music = music
        self.musicPlaying = False
        self.gameMusic = self.loadSound(os.path.join("sounds","one.mp3"))
        self.waveBeep = self.loadSound(os.path.join("sounds", "WaveBeep.wav"))
        self.gameOver = self.loadSound(os.path.join("sounds", "GameOver.wav"))
        self.hitBase = self.loadSound(os.path.join("sounds","hit.mp3"))

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
        self.playMusic(self.gameMusic)
        Player.player.musicOn = value
        Player.player.storeSettings()

    def playSound(self, sound, start=0):
        if self.sound:
            sound.play()
            if start != 0:
                sound.seek(start)

    def playMusic(self,music):
        if self.music:
            self.musicPlaying = True
            music.play()
            music.loop = True
            music.volume = .6
        if not self.music and self.musicPlaying:
            self.gameMusic.stop()
            self.musicPlaying = False
