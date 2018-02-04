
import os
import localdefs
import math, operator
import re

import Utilities
import Player
import Map
import Shot
import TowerGroup
import GUI
import ShotCloud

from kivy.uix.widget import Widget
from kivy.graphics import *
from kivy.animation import Animation



class Tower(Widget):
    def __init__(self,pos,**kwargs):
        super(Tower, self).__init__(**kwargs)
        self.pos=pos
        self.targetTimer= 0
        Player.player.money-=self.cost
        GUI.gui.myDispatcher.Money = str(Player.player.money)
        localdefs.towerlist.append(self)
        self.size = (Map.squsize*2-1, Map.squsize*2-1)
        self.rect = Utilities.createRect(self.pos, self.size, instance=self)
        self.squareheight = 2
        self.squarewidth = 2
        self.towerwalls = self.genWalls()
        self.imageNum = 0
        self.imagestr = os.path.join('towerimgs', self.type, str(self.imageNum) + '.png')
        self.image = Utilities.imgLoad(self.imagestr)
        self.image.pos = self.pos
        self.image.size = self.size
        self.currentRotation = 0
        self.add_widget(self.image)
        self.currentPointerAngle = 0
        self.turretpointpos = [self.center[0] + 12, self.center[1]]
        self.lastNeighborCount = 0
        self.neighborFlag = 'update'
        self.neighborList = []
        self.neighbors = self.getNeighbors() #neighbors is a directional dict 'left':towerobj
        self.towerGroup = None
        self.getGroup()
        self.totalspent = self.cost
        self.abilities = list()
        self.buttonlist = list()
        self.upgrades = list()
        self.attackair = True
        self.attackground = True
        self.attacktype = 'single'
        self.updateModifiers()
        self.hasTurret = False
        self.shotcloud = None
        self.shotcount = 0
        self.allowedshots = 1
        #Update tower group dict so it's accurate based on new tower
        for towergroup in localdefs.towerGroupDict[self.type]:
            towergroup.updateTowerGroup()

    def getNeighbors(self):
        neighbors = {}
        sidecount = 0
        neighborlist = []

        for tower in localdefs.towerlist:
            if tower.rect_x == self.rect_x - 2 * Map.squsize and tower.rect_y == self.rect_y and (
                    tower.type == self.type or tower.type == 'Life' or self.type == 'Life'):
                neighbors['l0'] = tower
                neighborlist.append('l0')
            elif tower.rect_x == self.rect_x + 2 * Map.squsize and tower.rect_y == self.rect_y and (
                    tower.type == self.type or tower.type == 'Life' or self.type == 'Life'):
                neighbors['r0'] = tower
                neighborlist.append('r0')
            elif tower.rect_y == self.rect_y + 2 * Map.squsize and tower.rect_x == self.rect_x and (
                    tower.type == self.type or tower.type == 'Life' or self.type == 'Life'):
                neighbors['u0'] = tower
                neighborlist.append('u0')
            elif tower.rect_y == self.rect_y - 2 * Map.squsize and tower.rect_x == self.rect_x and (
                    tower.type == self.type or tower.type == 'Life' or self.type == 'Life'):
                neighbors['d0'] = tower
                neighborlist.append('d0')

            elif tower.rect_x == self.rect_x - 2 * Map.squsize and \
                    (tower.type == self.type or tower.type == 'Life' or self.type == 'Life'):
                if tower.rect_y == (self.rect_y + Map.squsize):
                    neighbors['l1'] = tower
                    neighborlist.append('l1')
                elif tower.rect_y == (self.rect_y - Map.squsize):
                    neighbors['l2'] = tower
                    neighborlist.append('l2')
            elif tower.rect_x == self.rect_x + 2 * Map.squsize and \
                    (tower.type == self.type or tower.type == 'Life' or self.type == 'Life'):
                if tower.rect_y == (self.rect_y + Map.squsize):
                    neighbors['r1'] = tower
                    neighborlist.append('r1')
                elif tower.rect_y == (self.rect_y - Map.squsize):
                    neighbors['r2'] = tower
                    neighborlist.append('r2')
            elif tower.rect_y == self.rect_y + 2 * Map.squsize and \
                    (tower.type == self.type or tower.type == 'Life' or self.type == 'Life'):
                if tower.rect_x == (self.rect_x - Map.squsize):
                    neighbors['u1'] = tower
                    neighborlist.append('u1')
                elif tower.rect_x == (self.rect_x + Map.squsize):
                    neighbors['u2'] = tower
                    neighborlist.append('u2')
            elif tower.rect_y == self.rect_y - 2 * Map.squsize and \
                    (tower.type == self.type or tower.type == 'Life' or self.type == 'Life'):
                if tower.rect_x == (self.rect_x - Map.squsize):
                    neighbors['d1'] = tower
                    neighborlist.append('d1')
                elif tower.rect_x == (self.rect_x + Map.squsize):
                    neighbors['d2'] = tower
                    neighborlist.append('d2')

        totalNeighbors = 0
        sideList = set()
        for neighbor in neighborlist:
            totalNeighbors += 1
            sideList.add(neighbor[0])

        if totalNeighbors != self.lastNeighborCount:
            self.neighborFlag = 'update'
            self.neighborList = neighborlist
            self.lastNeighborCount = totalNeighbors
            self.neighborSideCount = len(sideList) #1-4 to be used in getImage
            self.neighborSideList = list(sideList)

        return neighbors

    def getGroup(self):
        if not self.neighbors:
            self.towerGroup =  TowerGroup.TowerGroup(self.type)
        else:
            letter = self.neighborList[0]
            self.getImage()
            if len(self.neighborList) >= 1:
                self.towerGroup = self.neighbors[letter].towerGroup
                x = 0
                while  x < len(self.neighborList):
                    letter = self.neighborList[x]
                    self.getData(letter)
                    x += 1

    def getData(self,string):
        tower = self.neighbors[string]
        tower.neighbors = tower.getNeighbors()
        tower.getImage()
        for element in tower.towerGroup.towerSet:
            element.towerGroup = self.towerGroup

    def getImage(self):
        if not self.neighbors:
            return
        if self.neighborSideCount == 4:
            self.imageNum = 4

        elif self.neighborSideCount == 3:
            self.imageNum = 3

        elif self.neighborSideCount == 2:
            list = sorted(self.neighborSideList)
            if list[0][0] == 'd' and list[1][0] == 'u':
                self.imageNum = '2_1'
            elif list[0][0] == 'l' and list[1][0] == 'r':
                self.imageNum = '2_1'
            else:
                self.imageNum = '2_2'

        elif self.neighborSideCount == 1:
            self.imageNum = 1

        self.updateImage()

    def getRotation(self):
        rotation = 0
        desiredRotation = 0
        list = sorted(self.neighborSideList)
        count = self.neighborSideCount
        if self.neighborFlag == 'update':
            if count == 1:
                if list[0][0]=='d':
                    desiredRotation = 270
                elif list[0][0]== 'l':
                    desiredRotation = 180
                elif list[0][0]== 'r':
                    desiredRotation = 0
                elif list[0][0]== 'u':
                    desiredRotation = 90
            if count == 2:
                if list[0][0] == 'd' and list[1][0] == 'u':
                    desiredRotation = 90
                elif list[0][0] == 'd' and list[1][0] == 'l':
                    desiredRotation = 180
                elif list[0][0] == 'd' and list[1][0] == 'r':
                    desiredRotation = 270
                elif list[0][0] == 'l' and list[1][0] == 'r':
                    desiredRotation = 0
                elif list[0][0] == 'l' and list[1][0] == 'u':
                    desiredRotation = 90
                elif list[0][0] == 'r' and list[1][0] == 'u':
                    desiredRotation = 0
            if count == 3:
                if list[0][0] == 'd' and list[1][0] == 'l' and list[2][0]=='r':
                    desiredRotation = 270
                elif list[0][0] == 'd' and list[1][0] == 'l' and list[2][0]=='u':
                    desiredRotation = 180
                elif list[0][0] == 'd' and list[1][0] == 'r' and list[2][0]=='u':
                    desiredRotation = 0
                elif list[0][0] == 'l' and list[1][0] == 'r' and list[2][0]=='u':
                    desiredRotation = 90
            if count == 4:
                desiredRotation = 0
            rotation = abs(self.currentRotation - desiredRotation)
            if self.currentRotation > desiredRotation:
                rotation = -rotation
            self.currentRotation = desiredRotation

            return rotation

        else:
            return 0

    def updateImage(self):
        #rotation is counter-clockwise in Kivy
        rotation = self.getRotation()
        if self.neighborFlag == 'update':
            self.imagestr = os.path.join('towerimgs', self.type, str(self.imageNum) + '.png')
            self.image.source = self.imagestr
            self.neighborFlag = ''
        if rotation != 0 :

            with self.image.canvas.before:
                PushMatrix()
                self.rot = Rotate(axis=(0,0,1), origin=self.image.center, angle = rotation)
            with self.image.canvas.after:
                PopMatrix()


    def updateModifiers(self):
        self.damage = self.initdamage * self.towerGroup.dmgModifier
        self.reload = self.initreload * self.towerGroup.reloadModifier
        self.range = self.initrange * self.towerGroup.rangeModifier
        if self.type == 'Wind':
            self.push = self.initpush * self.towerGroup.pushModifier

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

    def takeTurn(self):
        '''Maintain reload wait period and call target() once period is over
        Frametime: the amount of time elapsed per frame'''
        self.targetTimer -= Player.player.frametime
        ##if the rest period is up then shoot again
        if self.targetTimer<=0:
            self.target()

    def target(self):
        '''Create a sorted list of enemies based on distance from the tower. If enemy is within tower range then hit enemy'''
        sortedlist = sorted(Map.mapvar.enemycontainer.children, key=operator.attrgetter("distBase"))
        in_range_air = 0
        in_range_ground = 0
        for enemy in sortedlist:
            if math.sqrt((self.rect_centerx-enemy.rect_centerx)**2+(self.rect_centery-enemy.rect_centery)**2)<=self.range:
                if enemy.isair and self.attackair:
                    in_range_air +=1
                    if self.type == 'Wind':
                        if not self.active:
                            self.turret.source = os.path.join('towerimgs', self.type, "turret.gif")
                        self.shotcount += 1
                        Shot.Shot(self, enemy)

                    elif self.hasTurret:
                        self.moveTurret(enemy)
                        self.shotcount +=1
                        Shot.Shot(self, enemy)

                    elif self.shotcloud:
                        self.shotcloud.hitEnemy(enemy)
                        self.shotcount +=1
                        if not self.active:
                            self.shotcloud.enable()

                if not enemy.isair and self.attackground:
                    in_range_ground +=1
                    if self.hasTurret:
                        self.moveTurret(enemy)
                        self.shotcount +=1
                        Shot.Shot(self, enemy)
                    if self.shotcloud:
                        self.shotcloud.hitEnemy(enemy)
                        if not self.active:
                            self.shotcloud.enable()
                if self.shotcount > 0:
                    self.targetTimer = self.reload

            if self.shotcount >= self.allowedshots:
                return

        if in_range_air == 0 and self.type == 'Wind' and self.active:
            self.deactivateTower('Wind')
        if in_range_ground == 0 and self.type == 'Ice' and self.active:
            self.deactivateTower('Ice')


    def deactivateTower(self, tower):
        if tower == 'Ice':
            if self.active:
                self.shotcloud.disable()
        if tower == "Wind":
            self.active = False
            self.turret.source = os.path.join('towerimgs', self.type, "turret.png")

    def moveTurret(self, enemy):
        angle = 180+ Utilities.get_rotation(self, enemy)
        self.turret.anim = Animation(angle=angle, d=.1)
        self.turret.anim.start(self.turret_rot)


    def loadTurret(self):
        self.turretstr = os.path.join('towerimgs',self.type, 'turret.png')
        self.turret = Utilities.imgLoad(self.turretstr)
        self.turret.size = (30,30)
        self.turret.center = self.center
        self.add_widget(self.turret)
        with self.turret.canvas.before:
            PushMatrix()
            self.turret_rot=Rotate()
            self.turret_rot.origin=self.turret.center
            self.turret_rot.axis=(0,0,1)
            self.turret_rot.angle=0
        with self.turret.canvas.after:
            PopMatrix()



class FireTower(Tower):
    type = "Fire"
    cost = 20
    initdamage = 10
    initrange = 100
    initreload = .4
    imagestr = os.path.join('towerimgs', 'Fire', 'icon.png')
    def __init__(self,pos,**kwargs):
        Tower.__init__(self, pos, **kwargs)
        self.pos = pos
        self.cost = FireTower.cost
        self.initrange = FireTower.initrange
        self.initdamage = FireTower.initdamage
        self.initreload = FireTower.initreload
        self.type = FireTower.type
        self.attacktype = 'single'
        self.attackair = False
        self.shotimage = "flame.png"

    #Firetower attribute - flame spreads to enemies around doing small amount of damage over time.
    #fire and ice effects cancel each other

class LifeTower(Tower):
    type = "Life"
    cost = 15
    initrange = 150
    initdamage = 30
    initreload = 1.0
    imagestr = os.path.join('towerimgs', 'Life', 'icon.png')
    def __init__(self,pos, **kwargs):
        Tower.__init__(self, pos, **kwargs)
        self.pos = pos
        self.cost = LifeTower.cost
        self.initrange = LifeTower.initrange
        self.initdamage = LifeTower.initdamage
        self.initreload = LifeTower.initreload
        self.type = LifeTower.type
        self.attacktype = 'single'
        self.attackair = True
        self.shotimage = "arrow.png"
        self.hasTurret = True
        self.loadTurret()

    #Life has 2 attribute paths - damage and collaboration. Collaboration gives boosts to other towergroups.
    #Damage path - machine gun and sniper paths?

class GravityTower(Tower):
    type = "Gravity"
    cost = 15
    initrange = 90
    initdamage = 4
    initreload = 4
    imagestr = os.path.join('towerimgs', 'Gravity', 'icon.png')
    def __init__(self,pos,**kwargs):
        Tower.__init__(self, pos, **kwargs)
        self.pos = pos
        self.cost = GravityTower.cost
        self.initrange = GravityTower.initrange
        self.initdamage = GravityTower.initdamage
        self.initreload = GravityTower.initreload
        self.type = GravityTower.type
        self.shotimage = "waves.png"
        self.attackair=True
        self.attacktype = "multi"

    #Gravity tower pulls enemies towards it. On random occasions it can stun and pull strongly. Works on air.

class IceTower(Tower):
    type = "Ice"
    cost = 20
    initrange = 120
    initdamage = 3
    initreload = 1
    imagestr = os.path.join('towerimgs', 'Ice', 'icon.png')
    def __init__(self,pos, **kwargs):
        Tower.__init__(self, pos, **kwargs)
        self.pos = pos
        self.cost = IceTower.cost
        self.initrange = IceTower.initrange
        self.initdamage = IceTower.initdamage
        self.initreload = IceTower.initreload
        self.type = IceTower.type
        self.attackair = False
        self.attacktype = 'slow'
        self.shotcloud = ShotCloud.ShotCloud(self)
        self.active = False
        self.allowedshots = 999

    #freezes and slows the enemy

class WindTower(Tower):
    type = "Wind"
    cost = 20
    initrange = 200
    initdamage = 2
    initreload = 5
    initpush = 10
    imagestr = os.path.join('towerimgs', 'Wind', 'icon.png')
    def __init__(self,pos, **kwargs):
        Tower.__init__(self, pos, **kwargs)
        self.pos = pos
        self.cost = WindTower.cost
        self.initrange = WindTower.initrange
        self.initdamage = WindTower.initdamage
        self.initreload = WindTower.initreload
        self.initpush = WindTower.initpush
        self.push = 10
        self.type = WindTower.type
        self.attackair = True
        self.attackground = False
        self.attacktype = 'wind'
        self.shotimage = "gust.png"
        self.hasTurret = True
        self.loadTurret()
        self.active = False

available_tower_list =[LifeTower, FireTower, IceTower, GravityTower, WindTower]
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
            self.imgstr = str(os.path.join('towerimgs','0.png'))
            self.img = Utilities.imgLoad(self.imgstr)
        self.rect = Utilities.createRect(self.img.pos, self.img.size, self)


