import pygame
import os
from pygame.locals import *
import localdefs
import math, operator
import Utilities
import Player
import Map
import Shot
import TowerGroup
import GUI_Kivy

from kivy.uix.widget import Widget
from kivy.graphics import *



class Tower(Widget):
    def __init__(self,pos,**kwargs):
        super(Tower, self).__init__(**kwargs)
        self.pos=pos #tower's position
        self.targetTimer= int(self.initreload)
        Player.player.money-=self.cost
        GUI_Kivy.gui.myDispatcher.Money = str(Player.player.money)
        self.size = (Map.squsize*2-1, Map.squsize*2-1)
        self.rect = Utilities.createRect(self.pos, self.size, instance=self)
        self.squareheight = 2
        self.squarewidth = 2
        self.towerwalls = self.genWalls()
        self.neighbors = self.getNeighbors() #neighbors is a directional dict 'left':towerobj
        self.towerGroup = None
        self.getGroup()
        localdefs.towerlist.append(self)
        self.totalspent = self.cost
        self.abilities = list()
        self.buttonlist = list()
        self.upgrades = list()
        #self.type = "tower"
        self.attackair = True
        self.attackground = True
        self.attacktype = 'single'
        self.updateModifiers()

        #Update tower group dict so it's accurate based on new tower
        for towergroup in localdefs.towerGroupDict[self.type]:
            towergroup.updateTowerGroup()

    def getNeighbors(self):
        neighbors = {}
        for tower in localdefs.towerlist:
            if tower.rect_x == self.rect_x - 2 * Map.squsize and tower.rect_y == self.rect_y and tower.type == self.type:
                neighbors['left'] = tower
            if tower.rect_x == self.rect_x + 2 * Map.squsize and tower.rect_y == self.rect_y and tower.type == self.type:
                neighbors['right'] = tower
            if tower.rect_y == self.rect_y + 2 * Map.squsize and tower.rect_x == self.rect_x and tower.type == self.type:
                neighbors['top'] = tower
            if tower.rect_y == self.rect_y - 2 * Map.squsize and tower.rect_x == self.rect_x and tower.type == self.type:
                neighbors['bottom'] = tower
        return neighbors

    def getGroup(self):
        towerGroupList = []
        if not self.neighbors:
            self.towerGroup =  TowerGroup.TowerGroup(self.type)
        else:
            for key,value in self.neighbors.items():
                towerGroupList.append([value,value.towerGroup])
            x = 0
            self.towerGroup = towerGroupList[0][1]
            while x < len(towerGroupList)-1:
                if towerGroupList[x][1] != towerGroupList[x+1][1]:
                    for tower in towerGroupList[x+1][0].towerGroup.towerSet:
                        tower.towerGroup = towerGroupList[x][0].towerGroup
                x +=1

    def updateModifiers(self):
        self.damage = self.initdamage * self.towerGroup.dmgModifier
        self.reload = self.initreload * self.towerGroup.reloadModifier
        self.range = self.initrange * self.towerGroup.rangeModifier

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
    initdamage = 30
    initrange = 3*30
    initreload = 2
    imagestr = os.path.join('towerimgs', 'Fighter', '1.png')
    def __init__(self,pos,**kwargs):
        Tower.__init__(self, pos, **kwargs)
        self.pos = pos
        self.cost = FighterTower.cost
        self.initrange = FighterTower.initrange
        self.initdamage = FighterTower.initdamage
        self.initreload = FighterTower.initreload
        self.type = FighterTower.type
        self.attacktype = 'single'
        self.imagestr = FighterTower.imagestr
        self.image = Utilities.imgLoad(self.imagestr)
        self.image.size = self.size
        self.image.pos = self.pos
        self.add_widget(self.image)
        self.attackair = False
        self.shotimage = "cannonball.png"

class ArcherTower(Tower):
    type = "Archer"
    cost = 10
    initrange = 10*30
    initdamage = 30
    initreload = 1.0
    imagestr = os.path.join('towerimgs', 'Archer', '1.png')
    def __init__(self,pos, **kwargs):
        Tower.__init__(self, pos, **kwargs)
        self.pos = pos
        self.cost = ArcherTower.cost
        self.initrange = ArcherTower.initrange
        self.initdamage = ArcherTower.initdamage
        self.initreload = ArcherTower.initreload
        self.type = ArcherTower.type
        self.attacktype = 'single'
        self.imagestr = ArcherTower.imagestr
        self.image = Utilities.imgLoad(self.imagestr)
        self.image.pos = self.pos
        self.image.size = self.size
        self.add_widget(self.image)
        self.attackair = True
        self.shotimage = "arrow.png"

class MineTower(Tower):
    type = "Mine"
    cost = 15
    initrange = 3*30
    initdamage = 4
    initreload = 4
    imagestr = os.path.join('towerimgs', 'Mine', '1.png')
    def __init__(self,pos,**kwargs):
        Tower.__init__(self, pos, **kwargs)
        self.pos = pos
        self.cost = MineTower.cost
        self.initrange = MineTower.initrange
        self.initdamage = MineTower.initdamage
        self.initreload = MineTower.initreload
        self.type = MineTower.type
        self.imagestr = MineTower.imagestr
        self.image = Utilities.imgLoad(self.imagestr)
        self.image.pos = self.pos
        self.image.size = self.size
        self.add_widget(self.image)
        self.shotimage = "waves.png"
        self.attackair=False
        self.attacktype = "multi"

class SlowTower(Tower):
    type = "Slow"
    cost = 10
    initrange = 2
    initdamage = 0
    initreload = 1.0
    imagestr = os.path.join('towerimgs', 'Slow', '1.png')
    def __init__(self,pos, **kwargs):
        Tower.__init__(self, pos, **kwargs)
        self.pos = pos
        self.cost = SlowTower.cost
        self.initrange = SlowTower.initrange
        self.initdamage = SlowTower.initdamage
        self.initreload = SlowTower.initreload
        self.type = SlowTower.type
        self.imagestr = SlowTower.imagestr
        self.image = Utilities.imgLoad(self.imagestr)
        self.image.pos = self.pos
        self.image.size = self.size
        self.add_widget(self.image)
        self.attackair = True
        self.shotimage = "freeze.png"
        self.attacktype = 'multi'

class AntiAirTower(Tower):
    type = "AntiAir"
    cost = 35
    initrange = 6
    initdamage = 8
    initreload = 1.0
    imagestr = os.path.join('towerimgs', 'AntiAir', '1.png')
    def __init__(self,pos, **kwargs):
        Tower.__init__(self, pos, **kwargs)
        self.pos = pos
        self.cost = AntiAirTower.cost
        self.initrange = AntiAirTower.initrange
        self.initdamage = AntiAirTower.initdamage
        self.initreload = AntiAirTower.initreload
        self.type = "AntiAir"
        self.imagestr = AntiAirTower.imagestr
        self.image = Utilities.imgLoad(self.imagestr)
        self.image.pos = self.pos
        self.image.size = self.size
        self.add_widget(self.image)
        self.attackair = True
        self.attackground = False
        self.shotimage = "bolt.png"

available_tower_list =[ArcherTower, FighterTower,SlowTower, MineTower, AntiAirTower]
baseTowerList = [(tower.type, tower.cost, tower.initdamage, tower.initrange, tower.initreload, tower.imagestr) for tower in available_tower_list]



class Icon():
    def __init__(self,tower):
        '''Instantiate an Icon with the tower information it represents'''
        self.type = tower[0]
        self.base = "Tower"
        self.cost = tower[1]
        self.damage = tower[2]
        self.range = tower[3]
        self.reload = tower[4]
        localdefs.iconlist.append(self)
        try:
            self.imgstr = tower[5]
            self.img = Utilities.imgLoad(self.imgstr)

        except:
            self.imgstr = str(os.path.join('towerimgs',self.type,'1.png'))
            self.img = Utilities.imgLoad(self.imgstr)
        self.rect = Utilities.createRect(self.img.pos, self.img.size, self)


