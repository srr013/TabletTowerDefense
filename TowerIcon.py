import os
from kivy.uix.image import Image
import FireTower
import LifeTower
import IceTower
import GravityTower
import WindTower
import Localdefs
import Utilities

available_tower_list = [FireTower.FireTower, IceTower.IceTower, GravityTower.GravityTower, WindTower.WindTower, LifeTower.LifeTower]
baseTowerList = [(tower.type, tower.cost, tower.initdamage, tower.initrange, tower.initreload, tower.imagestr, tower.attacks) for tower
                 in available_tower_list]

class Icon():
    def __init__(self, tower):
        '''Instantiate an Icon with the tower information it represents'''
        self.type = tower[0]
        self.base = "Tower"
        self.cost = tower[1]
        self.damage = tower[2]
        self.range = tower[3]
        self.reload = tower[4]
        self.attacks = tower[6]
        Localdefs.iconlist.append(self)
        try:
            self.imgstr = tower[5]
            self.img = Image(source = self.imgstr)

        except:
            self.imgstr = str(os.path.join('towerimgs', '0.png'))
            self.img = Image(source = self.imgstr)
        self.rect = Utilities.createRect(self.img.pos, self.img.size, self)