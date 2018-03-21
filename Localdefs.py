import Player
import Map

from kivy.graphics import *

enemylist = list()
flyinglist = list()
towerlist = list()
bulletlist = list()
iconlist = list()
menulist = list()
explosions = list()
senderlist = list()
timerlist = list()
shotlist = list()
alertQueue = list()
towerabilitylist = list()
roadlist = list()
activeiceroadlist = list()
towerGroupDict = {'Life':[], 'Fire':[], 'Ice':[], 'Gravity':[], 'Wind':[]}


topBar_ElementList = [("Wave: ", "WaveNum", str(Player.player.wavenum),"enemyimgs/Crowd.png"),
                                    ("Score: ", "Score", int(Player.player.score), "iconimgs/100.png"),
                                    ("Money: ", "Money", Player.player.money,"iconimgs/coin20x24.png"),
                                    ("Gems: ", "Gems", Player.player.gems, "iconimgs/reddiamond.png"),
                                    ("Health: ", "Health", Player.player.health,"iconimgs/heart24x24.png"),
                                    ("Timer: ", "Timer", int(Map.mapvar.waveseconds), "iconimgs/clock.png")]



