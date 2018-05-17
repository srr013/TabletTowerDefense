import os
from kivy.uix.image import Image
import GUI
import Localdefs
import Map
import Player
import Utilities
import Kvgui

class TowerAbility:
    def __init__(self, ability):
        '''Instantiate an Icon with the tower information it represents'''
        self.type = ability['type']
        self.func = ability['func']
        self.cost = None
        Localdefs.towerabilitylist.append(self)
        try:
            self.img = Image(source = os.path.join('iconimgs', self.type + '.png'))
            self.imgstr = str(os.path.join('iconimgs', self.type + '.png'))
        except:
            print("upgrade icon image not loaded")
        self.rect = Utilities.createRect(self.img.pos, self.img.size, self)


baseAbilityList = [{'type': 'Sell', 'func': 'apply'}, {'type': 'Upgrade', 'func': 'apply'},
                   {'type': 'Rotate', 'func': 'apply'}]


class Sell(TowerAbility):
    name = "Sell"
    shortname = "Sell"

    # @classmethod
    # def cost(cls, tower):
    #     Player.player.money += (tower.totalspent)

    @classmethod
    def apply(cls, **kwargs):
        Player.player.analytics.towersSold += 1
        tower = Player.player.towerSelected
        if tower:
            Player.player.money += (tower.totalspent)
            Player.player.myDispatcher.Money = str(Player.player.money)
            tower.remove(sell = True)
            Player.player.towerSelected = None
            Map.mapvar.updatePath = True
            Map.mapvar.background.removeAll()
            return True

class UpgradeAll(TowerAbility):
    @classmethod
    def cost(cls, tower):
        return tower.upgradeDict['Cost'][tower.level]

    @classmethod
    def totalCost(cls, tower):
        low = 0
        total = 0
        for t in tower.towerGroup.towerLevels:
            if t[1] < low or low == 0:
                total = t[0].upgradeDict['Cost'][t[0].level]
                low = t[1]
            elif t[1] == low:
                total += t[0].upgradeDict['Cost'][t[0].level]
        return total

    @classmethod
    def upgradeAll(cls, tower):
        low = 0
        cls.list = []
        tower.towerGroup.needsUpdate = True
        for t in tower.towerGroup.towerLevels:
            if t[1] < low or low == 0:
                cls.list = [t[0]]
                low = t[1]
            elif t[1] == low:
                cls.list.append(t[0])
        for u in cls.list:
            cls.apply(tower = u)

    @classmethod
    def apply(cls, **kwargs):
        tower = kwargs['tower']
        cost = cls.cost(tower)
        Player.player.analytics.towerUpgrades += 1
        Player.player.analytics.moneySpent += cost
        if Player.player.money >= cost and tower.totalUpgradeTime == 0:
            Player.player.money -= cost
            tower.totalspent += cost
            Player.player.myDispatcher.Money = str(Player.player.money)
            Kvgui.disableTowerButtons()
            tower.upgrade()
        return False




class Upgrade(TowerAbility):
    @classmethod
    def cost(cls, tower):
        return tower.upgradeDict['Cost'][tower.level]

    @classmethod
    def doesFit(cls, tower):
        return (cls not in tower.upgrades)

    @classmethod
    def apply(cls, **kwargs):
        tower = Player.player.towerSelected
        cost = cls.cost(tower)
        if isinstance(cost, tuple):
            tower.upgradePath = kwargs['id']
            if tower.upgradePath == 'LeaderPath':
                if tower.towerGroup.leader == True:
                    return
                else:
                    tower.towerGroup.leader = tower
            newcost = cost[0]
            gems = cost[1]
            cost = newcost
            if Player.player.gems >= gems:
                Player.player.gems -= gems
                Player.player.myDispatcher.Gems = str(Player.player.gems)
            else:
                return
        Player.player.analytics.towerUpgrades += 1
        Player.player.analytics.moneySpent += cost
        if Player.player.money >= cost:
            Player.player.money -= cost
            tower.totalspent += cost
            Player.player.myDispatcher.Money = str(Player.player.money)
            if Player.player.tbbox:
                if Player.player.tbbox.type == 'Tower':
                    for button in Player.player.tbbox.enableList:
                        button.disabled = True
            tower.upgrade()
        return False


class Rotate(TowerAbility):
    @classmethod
    def cost(cls, tower):
        return 0

    @classmethod
    def doesFit(cls, tower):
        return (cls not in tower.upgrades)

    @classmethod
    def apply(cls, **kwargs):
        tower = Player.player.towerSelected
        if tower.towerGroup.facing == 'l':
            tower.towerGroup.facing = 'u'
        elif tower.towerGroup.facing == 'u':
            tower.towerGroup.facing = 'r'
        elif tower.towerGroup.facing == 'r':
            tower.towerGroup.facing = 'd'
        elif tower.towerGroup.facing == 'd':
            tower.towerGroup.facing = 'l'
        tower.updateTriangle()