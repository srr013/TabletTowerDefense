import Player
import Localdefs
import Map
import Utilities
import GUI

import os


class TowerAbility:
    def __init__(self,ability):
        '''Instantiate an Icon with the tower information it represents'''
        self.type = ability['type']
        self.func = ability['func']
        Localdefs.towerabilitylist.append(self)
        try:
            self.img = Utilities.imgLoad(os.path.join('iconimgs',self.type+'.png'))
            self.imgstr = str(os.path.join('iconimgs',self.type+'.png'))
        except:
            print("upgrade icon image not loaded")
        self.rect = Utilities.createRect(self.img.pos, self.img.size, self)

baseAbilityList = [{'type':'Sell','func':'apply'},{'type':'Upgrade','func':'apply'}, {'type':'Rotate','func':'apply'}]

class Sell(TowerAbility):
    name = "Sell"
    shortname = "Sell"
    @classmethod
    def cost(cls,tower):
        Player.player.money += (tower.totalspent)
    @classmethod
    def apply(cls,**kwargs):
        tower = Player.player.towerSelected
        Player.player.money+=(tower.totalspent)
        GUI.gui.myDispatcher.Money = str(Player.player.money)
        tower.towerGroup.towerSet.remove(tower)
        Localdefs.towerlist.remove(tower)
        Map.mapvar.towercontainer.remove_widget(tower)
        Player.player.towerSelected = None
        Map.mapvar.updatePath = True
        return True

class Upgrade(TowerAbility):
    @classmethod
    def cost(cls,tower):
        return tower.upgradeDict['Cost'][tower.level-1]
    @classmethod
    def doesFit(cls,tower):
        return (cls not in tower.upgrades)
    @classmethod
    def apply(cls,**kwargs):
        tower = Player.player.towerSelected
        cost = cls.cost(tower)
        if Player.player.money>=cost:
            Player.player.money-=cost
            tower.totalspent+=cost
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
        print tower.towerGroup.facing
