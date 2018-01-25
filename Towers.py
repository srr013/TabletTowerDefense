import pygame
import os
from pygame.locals import *
import localdefs
import math, operator
import Utilities
import Player
import Map
import Shot

from kivy.uix.widget import Widget
from kivy.graphics import *



class Tower(Widget):
    def __init__(self,pos,**kwargs):
        super(Tower, self).__init__(**kwargs)
        self.pos=pos #tower's position
        self.range= 5*Map.squsize #range a tower can shoot
        self.damage = 10 #damage per shot
        self.reload = 2 #seconds before a tower can shoot again
        self.targetTimer= int(self.reload)
        self.cost = 10 #cost of the tower
        Player.player.money-=self.cost
        self.size = (Map.squsize*2-1, Map.squsize*2-1)
        self.rect = Utilities.createRect(self.pos, self.size, instance=self)
        self.squareheight = 2
        self.squarewidth = 2
        self.towerwalls = self.genWalls()
        localdefs.towerlist.append(self)
        self.totalspent = self.cost
        self.abilities = list()
        self.buttonlist = list()
        self.upgrades = list()
        self.type = "tower"
        self.attackair = True
        self.attackground = True
        self.attacktype = 'single'
        #self.buttons = gui.createTowerButtons(self)



    def genWalls(self):
        '''Generating the rects for the tower used in collision and path generation'''
        walls = []
        h = self.squareheight
        k = 0
        while h > 0:
            j = 0
            w = self.squarewidth
            while w > 0:
                wall = (int((self.rect_x) / Map.squsize)+j, int((self.rect_y) / Map.squsize)+k)
                walls.append(wall)
                w -= 1
                j += 1
            k += 1
            h -= 1
        #not permanent. Just ensuring right location of walls
        for wall in walls:
            with self.canvas.before:
                Color(0, 0, 0,.1)
                Rectangle(size=(30,30), pos=(wall[0]*30, wall[1]*30))
        return walls

    def genButtons(self):
        '''Called when a tower is selected via mouse. Places the buttons around the tower.'''
        font = pygame.font.Font(None,20)
        ##generate a list of abilities from the currently hardcoded list in Towers.py
        ##doesFit() returns true if the tower is not in tower.upgrades list, which keeps track of whether the tower has been upgraded yet
        abilitylist = [i for i in TowerAbilityList if (i.doesFit(self) and (i.shortname in Player.player.modDict['towerAbilities']))]
        ##buttonnum could change w/ tower abilities (=len(abilitylist) but this makes for inconsistent ability placement on the circle
        buttonnum = 5 ##UPDATE this number if additional functions are added that apply to all towers
        if buttonnum:
            inddeg = (2.0*math.pi)/buttonnum
            self.buttonlist = list()
            radius = 50
            ##generate the list of abilities per tower
            for ind,ta in enumerate(abilitylist):
                try:taimg = Utilities.imgLoad(os.path.join("upgradeicons",ta.shortname+".jpg"))
                except:
                    taimg = pygame.Surface((20,20))
                    taimg.fill((90,90,255))
                tarect = pygame.Rect((0,0),(20,20))
                tarect.center=(self.rect.centerx,self.rect.centery)
                tarect.move_ip(radius*math.cos((ind+1)*inddeg),radius*math.sin((ind+1)*inddeg))
                ##setup text to the side of the upgradeicon
                info = font.render("%s: -%dcr" % (ta.name,ta.cost(self)),1,(0,0,0))
                infopos = info.get_rect(center=(self.rect.centerx+(radius+info.get_width()+10)*math.cos((ind+1)*inddeg),self.rect.centery+(radius+info.get_height()+10)*math.sin((ind+1)*inddeg)))
                infopos.left=max(0,infopos.left)
                infopos.right=min(Map.scrwid,infopos.right)
                infopos.top=max(0,infopos.top)
                infopos.bottom=min(Map.scrhei,infopos.bottom)
                self.buttonlist.append((taimg,tarect,info,infopos,ta.apply))

    def takeTurn(self):
        '''Maintain reload wait period and call target() once period is over
        Frametime: the amount of time elapsed per frame'''
        self.targetTimer -= Player.player.frametime
        ##if the rest period is up then shoot again
        if self.targetTimer<=0:
            self.targetTimer = self.reload
            self.target()

    def target(self):
        '''Create a sorted list of enemies based on distance from the tower. If enemy is within tower range then hit enemy'''
        tower=self
        sortedlist = sorted(Map.mapvar.enemycontainer.children, key=operator.attrgetter("distBase"))

        ##the distance attribute here isn't reliable. it's set above by movement.
        for enemy in sortedlist:
            if math.sqrt((self.rect_centerx-enemy.rect_centerx)**2+(self.rect_centery-enemy.rect_centery)**2)<=self.range:
                if enemy.isair and tower.attackair:
                    # create a shot and add it to the Shotlist for tracking
                    Shot.Shot(tower, enemy)
                    # if tower attacks one enemy at a time then break the loop after first
                    if tower.attacktype == "single":
                        return
                if not enemy.isair and tower.attackground:
                    #create a shot and add it to the Shotlist for tracking
                    Shot.Shot(tower, enemy)
                    #if tower attacks one enemy at a time then break the loop after first
                    if tower.attacktype == "single":
                        return
                    #if tower attacks all enemies in range then loop through all in list within range
                    elif tower.attacktype == "multi" or tower.attacktype == 'slow':
                        pass
        return

class FighterTower(Tower):
    type = "Fighter"
    cost = 5
    damage = 5
    range = 3*30
    reload = 2
    def __init__(self,pos,**kwargs):
        Tower.__init__(self, pos, **kwargs)
        self.pos = pos
        self.cost = FighterTower.cost
        self.range = FighterTower.range
        self.damage = FighterTower.damage
        self.reload = FighterTower.reload
        self.type = FighterTower.type
        self.attacktype = 'single'
        self.image = Utilities.imgLoad(os.path.join('towerimgs','Fighter','1.png'))
        self.imagestr = os.path.join('towerimgs','Fighter','1.png')
        self.image.size = self.size
        self.image.pos = self.pos
        self.add_widget(self.image)
        self.attackair = False
        self.shotimage = "cannonball.png"

class ArcherTower(Tower):
    type = "Archer"
    cost = 10
    range = 10*30
    damage = 6
    reload = 1.0
    def __init__(self,pos, **kwargs):
        Tower.__init__(self, pos, **kwargs)
        self.pos = pos
        self.cost = ArcherTower.cost
        self.range = ArcherTower.range
        self.damage = ArcherTower.damage
        self.reload = ArcherTower.reload
        self.type = ArcherTower.type
        self.attacktype = 'single'
        self.image = Utilities.imgLoad(os.path.join('towerimgs', 'Archer', '1.png'))
        self.imagestr = os.path.join('towerimgs', 'Archer', '1.png')
        self.image.pos = self.pos
        self.image.size = self.size
        self.add_widget(self.image)
        self.attackair = True
        self.shotimage = "arrow.png"

class MineTower(Tower):
    type = "Mine"
    cost = 15
    range = 3*30
    damage = 4
    reload = 4
    def __init__(self,pos,**kwargs):
        Tower.__init__(self, pos, **kwargs)
        self.pos = pos
        self.cost = MineTower.cost
        self.range = MineTower.range
        self.damage = MineTower.damage
        self.reload = MineTower.reload
        self.type = MineTower.type
        self.image = Utilities.imgLoad(os.path.join('towerimgs', 'Mine', '1.png'))
        self.imagestr = os.path.join('towerimgs', 'Mine', '1.png')
        self.image.pos = self.pos
        self.image.size = self.size
        self.add_widget(self.image)
        self.shotimage = "waves.png"
        self.attackair=False
        self.attacktype = "multi"

class SlowTower(Tower):
    type = "Slow"
    cost = 10
    range = 2
    damage = 0
    reload = 1.0
    def __init__(self,pos, **kwargs):
        Tower.__init__(self, pos, **kwargs)
        self.pos = pos
        self.cost = SlowTower.cost
        self.range = SlowTower.range
        self.damage = SlowTower.damage
        self.reload = SlowTower.reload
        self.type = SlowTower.type
        self.image = Utilities.imgLoad(os.path.join('towerimgs', 'Slow', '1.png'))
        self.imagestr = os.path.join('towerimgs', 'Slow', '1.png')
        self.image.pos = self.pos
        self.image.size = self.size
        self.add_widget(self.image)
        self.attackair = True
        self.shotimage = "freeze.png"
        self.attacktype = 'multi'

class AntiAirTower(Tower):
    type = "AntiAir"
    cost = 35
    range = 6
    damage = 8
    reload = 1.0
    def __init__(self,pos, **kwargs):
        Tower.__init__(self, pos, **kwargs)
        self.pos = pos
        self.cost = AntiAirTower.cost
        self.range = AntiAirTower.range
        self.damage = AntiAirTower.damage
        self.reload = AntiAirTower.reload
        self.type = "AntiAir"
        self.imagestr = os.path.join('towerimgs', 'AntiAir', '1.png')
        self.image = Utilities.imgLoad(os.path.join('towerimgs', 'AntiAir', '1.png'))
        self.image.pos = self.pos
        self.image.size = self.size
        self.add_widget(self.image)
        self.attackair = True
        self.attackground = False
        self.shotimage = "bolt.png"

available_tower_list =[ArcherTower, FighterTower,SlowTower, MineTower, AntiAirTower]
baseTowerList = [(tower.type,tower.cost, tower.damage, tower.range, tower.reload) for tower in available_tower_list]



class Icon():
    def __init__(self,tower):
        '''Instantiate an Icon with the tower information it represents'''
        self.type = tower[0]
        self.base = "Tower"
        self.basecost = tower[1]
        self.basedamage = tower[2]
        self.baserange = tower[3]
        self.basetime = tower[4]
        localdefs.iconlist.append(self)
        try:
            self.img = Utilities.imgLoad(os.path.join('towerimgs',self.type,'1.png'))
            self.imgstr = str(os.path.join('towerimgs',self.type,'1.png'))
        except:
            self.img = Utilities.imgLoad(os.path.join('towerimgs','Basic','1.png'))
            self.imgstr = str(os.path.join('towerimgs',self.type,'1.png'))
        self.rect = Utilities.createRect(self.img.pos, self.img.size, self)


