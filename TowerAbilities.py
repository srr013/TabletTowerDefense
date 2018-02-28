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
        self.cost = ability['cost']
        self.func = ability['func']
        Localdefs.towerabilitylist.append(self)
        try:
            self.img = Utilities.imgLoad(os.path.join('iconimgs',self.type+'.png'))
            self.imgstr = str(os.path.join('iconimgs',self.type+'.png'))
        except:
            print("upgrade icon image not loaded")
        self.rect = Utilities.createRect(self.img.pos, self.img.size, self)

baseAbilityList = [{'type':'Sell','cost':0, 'func':'apply'},{'type':'Upgrade', 'cost':0, 'func':'apply'}]

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
    name = "15% +Damage"
    shortname = "ExtraDamage1"
    @classmethod
    def cost(cls,tower):
        return 10
    @classmethod
    def doesFit(cls,tower):
        return (cls not in tower.upgrades)
    @classmethod
    def apply(cls,**kwargs):
        tower = Player.player.towerSelected
        if Player.player.money>=cls.cost(tower):
            Player.player.money-=cls.cost(tower)
            GUI.gui.myDispatcher.Money = str(Player.player.money)
            tower.upgrade()
        return False

