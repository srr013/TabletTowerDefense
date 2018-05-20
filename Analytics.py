from kivy.event import EventDispatcher
from kivy.properties import NumericProperty
from kivy.storage.dictstore import DictStore


class Analytics(EventDispatcher):
    gameEnemies = NumericProperty()
    gameDamage = NumericProperty()
    towersBought = NumericProperty()
    towersSold = NumericProperty()
    towerUpgrades = NumericProperty()
    maxTowerLevel = NumericProperty()
    finalWave = NumericProperty()
    gameTimeEnd = NumericProperty()
    moneyEarned = NumericProperty()
    moneySpent = NumericProperty()

    def on_gameEnemies(self, instance, value):
        self.numEnemies = value

    def on_gameDamage(self, instance, value):
        self.gameDamage = value

    def on_towersBought(self, instance, value):
        self.towersBought = value

    def on_towersSold(self, instance, value):
        self.towersSold = value

    def on_towerUpgrades(self, instance, value):
        self.towerUpgrades = value

    def on_maxTowerLevel(self, instance, value):
        self.maxTowerLevel = value

    def on_finalWave(self, instance, value):
        self.finalWave = value

    def on_gameTimeEnd(self, instance, value):
        self.gameLength = self.gameTimeEnd - self.gameTimeStart
        if self.gameLength >= 60:
            self.gameLength = (self.gameLength / 60, self.gameLength % 60)
        else:
            self.gameLength = (0, self.gameLength)

    def on_moneyEarned(self, instance, value):
        self.moneyEarned = value

    def on_moneySpent(self, instance, value):
        self.moneySpent = value

    def __init__(self):
        super(Analytics, self).__init__()
        self.gameTimeStart = 0
        self.gameTimeEnd = 0
        self.playerData = DictStore('player_data.txt')
        if self.playerData.exists('lastgame'):
            self.numEnemies = self.playerData.get('lastgame')['numEnemies']
            self.gameDamage = self.playerData.get('lastgame')['gameDamage']
            self.towersBought = self.playerData.get('lastgame')['towersBought']
            self.towersSold = self.playerData.get('lastgame')['towersSold']
            self.towerUpgrades = self.playerData.get('lastgame')['towerUpgrades']
            self.maxTowerLevel = self.playerData.get('lastgame')['maxTowerLevel']
            self.finalWave = self.playerData.get('lastgame')['finalWave']
            self.moneyEarned = self.playerData.get('lastgame')['moneyEarned']
            self.moneySpent = self.playerData.get('lastgame')['moneySpent']
            self.gameLength = self.playerData.get('lastgame')['gameLength']
            self.score = self.playerData.get('lastgame')['score']
        else:
            self.numEnemies = 0
            self.gameDamage = 0
            self.towersBought = 0
            self.towersSold = 0
            self.towerUpgrades = 0
            self.maxTowerLevel = 1
            self.finalWave = 1
            self.moneyEarned = 0
            self.moneySpent = 0
            self.gameLength = (0, 0)
            self.score = 0
        if self.playerData.exists('totals'):
            self.totalGames = self.playerData.get('totals')['totalGames']
            self.totalEnemies = self.playerData.get('totals')['totalEnemies']
            self.totalDamage = self.playerData.get('totals')['totalDamage']
            self.totalBought = self.playerData.get('totals')['totalBought']
            self.totalSold = self.playerData.get('totals')['totalSold']
            self.totalUpgraded = self.playerData.get('totals')['totalUpgraded']
            self.highestTowerLevel = self.playerData.get('totals')['highestTowerLevel']
            self.latestWave = self.playerData.get('totals')['latestWave']
            self.totalEarned = self.playerData.get('totals')['totalEarned']
            self.totalSpent = self.playerData.get('totals')['totalSpent']
            self.timePlayed = self.playerData.get('totals')['timePlayed']
        else:
            self.totalGames = 0
            self.totalEnemies = 0
            self.totalDamage = 0
            self.totalBought = 0
            self.totalSold = 0
            self.totalUpgraded = 0
            self.highestTowerLevel = 1
            self.latestWave = 1
            self.totalEarned = 0
            self.totalSpent = 0
            self.timePlayed = {'hours':0, 'minutes': 0, 'seconds': 0}

    def _print(self):
        if self.gameEnemies != 0:
            print [
                "Num Enemies: ", self.numEnemies,
                "Total Damage: ", int(self.gameDamage),
                "Towers Bought: ", self.towersBought,
                "Towers Sold: ", self.towersSold,
                "Tower Upgrades: ", self.towerUpgrades,
                "Max Tower Level: ", self.maxTowerLevel,
                "Final Wave: ", self.finalWave,
                "Game Length: ", str(int(self.gameLength[0])) + " minutes " + str(int(self.gameLength[1])) + " seconds",
                "Money Earned: ", self.moneyEarned,
                "Money Spent: ", self.moneySpent,
                "total Enemies: ", self.totalEnemies,
                "total Damage: ", self.totalDamage,
                "total Bought: ", self.totalBought,
                "total Sold: ", self.totalSold,
                "total Upgraded: ", self.totalUpgraded,
                "highest Level: ", self.highestTowerLevel,
                "latest Wave: ", self.latestWave,
                "total Earned: ", self.totalEarned,
                "total Spent: ", self.totalSpent,
                "total time played: ", self.timePlayed,
                "total games: ", self.totalGames]

    def updateData(self):
        self.totalGames += 1
        self.totalEnemies += self.numEnemies
        self.totalDamage += int(self.gameDamage)
        self.totalBought += self.towersBought
        self.totalSold += self.towersSold
        self.totalUpgraded += self.towerUpgrades
        if self.highestTowerLevel < self.maxTowerLevel:
            self.highestTowerLevel = self.maxTowerLevel
        if self.latestWave < self.finalWave:
            self.latestWave = self.finalWave
        self.totalEarned += self.moneyEarned
        self.totalSpent += self.moneySpent
        self.timePlayed['minutes'] += int(self.gameLength[0])
        self.timePlayed['seconds'] += int(self.gameLength[1])
        if self.timePlayed['seconds'] > 60:
            self.timePlayed['seconds'] = int(self.timePlayed['seconds'] % 60)
            self.timePlayed['minutes'] += 1
        if self.timePlayed['minutes'] > 60:
            self.timePlayed['minutes'] = int(self.timePlayed['minutes'] % 60)
            self.timePlayed['hours'] += 1


    def store_data(self):
        self.playerData.put('lastgame', numEnemies=self.numEnemies, gameDamage=self.gameDamage,
                            towersBought=self.towersBought,
                            towersSold=self.towersSold, towerUpgrades=self.towerUpgrades,
                            maxTowerLevel=self.maxTowerLevel, finalWave=self.finalWave,
                            gameLength=self.gameLength, moneyEarned=self.moneyEarned, moneySpent=self.moneySpent, score = self.score)
        self.playerData.put('totals', totalGames = self.totalGames, totalEnemies=self.totalEnemies, totalDamage=self.totalDamage,
                            totalBought=self.totalBought,
                            totalSold=self.totalSold, totalUpgraded=self.totalUpgraded,
                            highestTowerLevel=self.highestTowerLevel, latestWave=self.latestWave,
                            timePlayed=self.timePlayed, totalEarned=self.totalEarned, totalSpent=self.totalSpent)
        # self.playerData.put('highscores', numEnemies=self.gameEnemies, totalDamage=self.gameDamage,
        #                     towersBought=self.towersBought,
        #                     towersSold=self.towersSold, towerUpgrades=self.towerUpgrades,
        #                     maxTowerLevel=self.maxTowerLevel, finalWave=self.finalWave,
        #                     gameLenght=self.gameLength, moneyEarned=self.moneyEarned, moneySpent=self.moneySpent)

