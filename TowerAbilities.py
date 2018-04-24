import os

import GUI
import Localdefs
import Map
import Player
import Utilities


class TowerAbility:
    def __init__(self, ability):
        '''Instantiate an Icon with the tower information it represents'''
        self.type = ability['type']
        self.func = ability['func']
        self.cost = None
        Localdefs.towerabilitylist.append(self)
        try:
            self.img = Utilities.imgLoad(os.path.join('iconimgs', self.type + '.png'))
            self.imgstr = str(os.path.join('iconimgs', self.type + '.png'))
        except:
            print("upgrade icon image not loaded")
        self.rect = Utilities.createRect(self.img.pos, self.img.size, self)


baseAbilityList = [{'type': 'Sell', 'func': 'apply'}, {'type': 'Upgrade', 'func': 'apply'},
                   {'type': 'Rotate', 'func': 'apply'}]


class Sell(TowerAbility):
    name = "Sell"
    shortname = "Sell"

    @classmethod
    def cost(cls, tower):
        Player.player.money += (tower.totalspent)

    @classmethod
    def apply(cls, **kwargs):
        Player.player.analytics.towersSold += 1
        tower = Player.player.towerSelected
        if tower:
            Player.player.money += (tower.totalspent)
            GUI.gui.myDispatcher.Money = str(Player.player.money)
            tower.remove(sell = True)
            Player.player.towerSelected = None
            Map.mapvar.updatePath = True
            return True


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
                GUI.gui.myDispatcher.Gems = str(Player.player.gems)
            else:
                return
        Player.player.analytics.towersUpgraded += 1
        Player.player.analytics.moneySpent += cost
        if Player.player.money >= cost:
            Player.player.money -= cost
            tower.totalspent += cost
            GUI.gui.myDispatcher.Money = str(Player.player.money)
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