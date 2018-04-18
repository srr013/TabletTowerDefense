from kivy.properties import NumericProperty
from kivy.event import EventDispatcher

import time

class Analytics(EventDispatcher):
    gameEnemies = NumericProperty()
    gameDamage = NumericProperty()
    towersBought = NumericProperty()
    towersSold = NumericProperty()
    towersUpgraded = NumericProperty()
    maxTowerLevel = NumericProperty()
    finalWave = NumericProperty()
    gameTimeEnd = NumericProperty()
    moneyEarned = NumericProperty()
    moneySpent = NumericProperty()

    def on_gameEnemies(self, instance, value):
        self.gameEnemies = value
    def on_totalHP(self, instance, value):
        self.totalHP = value
    def on_gameDamage(self, instance, value):
        self.gameDamage = value
    def on_towersBought(self, instance, value):
        self.towersBought = value
    def on_towersSold(self, instance, value):
        self.towersSold = value
    def on_towersUpgraded(self, instance, value):
        self.towersUpgraded = value
    def on_maxTowerLevel(self, instance, value):
        self.maxTowerLevel = value
    def on_finalWave(self, instance, value):
        self.finalWave = value
    def on_gameTimeEnd(self, instance, value):
        self.gameLength = self.gameTimeEnd - self.gameTimeStart
        if self.gameLength >= 60:
            self.gameLength = (self.gameLength/60, self.gameLength%60)
        else:
            self.gameLength = (0, self.gameLength)


    def on_moneyEarned(self, instance, value):
        self.moneyEarned = value
    def on_moneySpent(self, instance, value):
        self.moneySpent = value

    def __init__(self):
        super(Analytics, self).__init__()
        self.gameEnemies = 0
        self.totalHP = 0
        self.gameDamage = 0
        self.towersBought = 0
        self.towersSold = 0
        self.towersUpgraded = 0
        self.maxTowerLevel = 1
        self.finalWave = 1
        self.moneyEarned = 0
        self.moneySpent = 0
        self.gameTimeStart = 0
        self.gameTimeEnd = 0
        self.gameLength = ()


    def _print(self):
        if self.gameEnemies != 0:
            print [
            "Num Enemies: ", self.gameEnemies,
            "Total Damage: ",int(self.gameDamage),
            "Towers Bought: ",self.towersBought,
            "Towers Sold: ", self.towersSold,
            "Tower Upgrades: ", self.towersUpgraded,
            "Max Tower Level: ", self.maxTowerLevel,
            "Final Wave: ", self.finalWave,
            "Game Length: ", str(self.gameLength[0]) + " minutes " + str(int(self.gameLength[1])) +" seconds",
            "Money Earned: ", self.moneyEarned,
            "Money Spent: ", self.moneySpent]