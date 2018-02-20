import os
import Localdefs
import math
import operator
import re

import Utilities
import Player
import Map
import Shot
import TowerGroup
import GUI

from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.graphics import *
from kivy.animation import Animation



class Tower(Widget):
    def __init__(self,pos,**kwargs):
        super(Tower, self).__init__(**kwargs)
        self.pos=pos
        self.targetTimer= 0
        Player.player.money-=self.cost
        GUI.gui.myDispatcher.Money = str(Player.player.money)
        Localdefs.towerlist.append(self)
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
        self.adjacentRoadPos = Utilities.adjacentRoadPos(self.pos)
        self.adjacentRoads = list()
        self.adjacentRoadFlag = False
        self.totalspent = self.cost
        self.abilities = list()
        self.buttonlist = list()
        self.upgrades = list()
        self.attackair = True
        self.attackground = True
        self.attacktype = 'single'
        self.updateModifiers()
        self.hasTurret = False
        # self.shotcloud = None
        self.shotcount = 0
        self.allowedshots = 1
        self.level = 1

        self.totalUpgradeTime = 0
        self.upgradeTimeElapsed = 0
        self.percentComplete = 0

        #Update tower group dict so it's accurate based on new tower
        for towergroup in Localdefs.towerGroupDict[self.type]:
            towergroup.updateTowerGroup()

    def getNeighbors(self):
        neighbors = {}
        sidecount = 0
        neighborlist = []

        for tower in Localdefs.towerlist:
            if tower.rect_x == self.rect_x - 2 * Map.squsize and tower.rect_y == self.rect_y and (
                    tower.type == self.type):
                neighbors['l0'] = tower
                neighborlist.append('l0')
            elif tower.rect_x == self.rect_x + 2 * Map.squsize and tower.rect_y == self.rect_y and (
                    tower.type == self.type):
                neighbors['r0'] = tower
                neighborlist.append('r0')
            elif tower.rect_y == self.rect_y + 2 * Map.squsize and tower.rect_x == self.rect_x and (
                    tower.type == self.type):
                neighbors['u0'] = tower
                neighborlist.append('u0')
            elif tower.rect_y == self.rect_y - 2 * Map.squsize and tower.rect_x == self.rect_x and (
                    tower.type == self.type):
                neighbors['d0'] = tower
                neighborlist.append('d0')
            elif tower.rect_x == self.rect_x - 2 * Map.squsize and \
                    (tower.type == self.type):
                if tower.rect_y == (self.rect_y + Map.squsize):
                    neighbors['l1'] = tower
                    neighborlist.append('l1')
                elif tower.rect_y == (self.rect_y - Map.squsize):
                    neighbors['l2'] = tower
                    neighborlist.append('l2')
            elif tower.rect_x == self.rect_x + 2 * Map.squsize and \
                    (tower.type == self.type):
                if tower.rect_y == (self.rect_y + Map.squsize):
                    neighbors['r1'] = tower
                    neighborlist.append('r1')
                elif tower.rect_y == (self.rect_y - Map.squsize):
                    neighbors['r2'] = tower
                    neighborlist.append('r2')
            elif tower.rect_y == self.rect_y + 2 * Map.squsize and \
                    (tower.type == self.type):
                if tower.rect_x == (self.rect_x - Map.squsize):
                    neighbors['u1'] = tower
                    neighborlist.append('u1')
                elif tower.rect_x == (self.rect_x + Map.squsize):
                    neighbors['u2'] = tower
                    neighborlist.append('u2')
            elif tower.rect_y == self.rect_y - 2 * Map.squsize and \
                    (tower.type == self.type):
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
            self.towerGroup =  TowerGroup.TowerGroup(self)
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
                PopMatrix()#tower positioning and rotation


    def updateModifiers(self):
        self.damage = self.initdamage * self.towerGroup.dmgModifier
        self.reload = self.initreload * self.towerGroup.reloadModifier
        self.range = self.initrange * self.towerGroup.rangeModifier
        if self.type == 'Wind':
            self.push = self.initpush * self.towerGroup.pushModifier
        if self.type == 'Ice':
            self.slowtime = self.initslowtime * self.towerGroup.slowTimeModifier
            self.slowpercent = self.initslowpercent * self.towerGroup.slowPercentModifier
        if self.type == 'Gravity':
            self.stuntime = self.initstuntime * self.towerGroup.stunTimeModifier

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

    def upgrade(self):
        self.priorimage = str(self.image.source)
        self.remove_widget(self.turret)
        #self.image.source = os.path.join('iconimgs','Upgrade.png')
        with self.image.canvas: #draw upgrade bars
            Color(1,1,1,1)
            self.statusbar = Line(points = [self.x+8, self.y+6, self.x+self.width-8, self.y+6], width = 4, cap='none')
            Color(0,0,0,1)
            self.remainingtime = Line(points = [self.x+8, self.y+6, self.x+9, self.y+6], width = 3.4, cap='none')
        self.upgradeTimeElapsed = 0
        self.totalUpgradeTime = self.level*5

    def updateUpgradeStatusBar(self):
        self.percentComplete = self.upgradeTimeElapsed/self.totalUpgradeTime
        if self.percentComplete >= 1:
            self.image.canvas.remove(self.remainingtime)
            self.image.canvas.remove(self.statusbar)
            self.totalUpgradeTime = 0
            self.upgradeTimeElapsed = 0
            self.percentComplete = 0
            self.add_widget(self.turret)
            return
        self.remainingtime.points = [self.x+8, self.y+6, self.x+(self.width-8)*self.percentComplete, self.y+6]

    def takeTurn(self):
        '''Maintain reload wait period and call target() once period is over
        Frametime: the amount of time elapsed per frame'''
        if self.totalUpgradeTime == 0:
            self.targetTimer -= Player.player.frametime
            ##if the rest period is up then shoot again
            if self.targetTimer<=0:
                self.target()
        if self.totalUpgradeTime > 0:
            self.upgradeTimeElapsed+= Player.player.frametime
            self.updateUpgradeStatusBar()

    def target(self):
        '''Create a sorted list of enemies based on distance from the tower. If enemy is within tower range then hit enemy'''
        sortedlist = sorted(Map.mapvar.enemycontainer.children, key=operator.attrgetter("distBase"))
        in_range_air = 0
        in_range_ground = 0

        for enemy in sortedlist:
            if Utilities.in_range(self,enemy):
                if enemy.isair and self.attackair:
                    in_range_air +=1
                    if self.attacktype == 'single':
                        self.moveTurret(enemy)
                        self.shotcount +=1
                        Shot.Shot(self, enemy)
                if not enemy.isair and self.attackground:
                    in_range_ground +=1
                    if self.attacktype == 'single':
                        self.moveTurret(enemy)
                        self.shotcount +=1
                        Shot.Shot(self, enemy)
                if self.shotcount > 0:
                    self.targetTimer = self.reload

            if self.shotcount >= self.allowedshots:
                return

    def moveTurret(self, enemy):
        angle = 180+Utilities.get_rotation(self, enemy)
        #print ("angle:", angle)
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
    initreload = .2
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
        self.active = True
        self.shotimage = "flame.png"
        self.hasTurret = True
        self.loadTurret()

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
        self.shotimage = "cannonball.png"
        self.hasTurret = True
        self.active = True
        self.loadTurret()

    #Life has 2 attribute paths - damage and collaboration. Collaboration gives boosts to other towergroups.
    #Damage path - machine gun and sniper paths?

class GravityTower(Tower):
    type = "Gravity"
    cost = 15
    initrange = 60
    initdamage = 8
    initreload = 5
    initstuntime = 3
    initpush = 10
    imagestr = os.path.join('towerimgs', 'Gravity', 'icon.png')
    def __init__(self,pos,**kwargs):
        Tower.__init__(self, pos, **kwargs)
        self.pos = pos
        self.cost = GravityTower.cost
        self.initrange = GravityTower.initrange
        self.initdamage = GravityTower.initdamage
        self.initreload = GravityTower.initreload
        self.initstuntime = GravityTower.initstuntime
        self.initpush = GravityTower.initpush
        self.type = GravityTower.type
        self.attackair=True
        self.attacktype = "multi"
        # self.shotcloud = ShotCloud.ShotCloud(self)
        self.active = False
        self.allowedshots = 999
        self.stuntime = self.initstuntime
        self.push = -10
        with self.canvas:
            self.color = Color(0, 0, 0, 1)
            self.rect = Image(source=os.path.join('towerimgs', 'Gravity', "attack.png"), size=(45, 45),
                              pos=(self.center[0] - 22, self.center[1] - 22))
        self.closeanimation = Animation(size=(45, 45), pos=(self.center[0] - 22, self.center[1] - 22),
                                     duration=.3)
            #Gravity tower pulls enemies towards it. On random occasions it can stun and pull strongly. Works on air.

class IceTower(Tower):
    type = "Ice"
    cost = 20
    initrange = 60
    initdamage = 1
    initreload = 2
    initslowtime = 3
    initslowpercent = .8
    imagestr = os.path.join('towerimgs', 'Ice', 'icon.png')
    def __init__(self,pos, **kwargs):
        Tower.__init__(self, pos, **kwargs)
        self.pos = pos
        self.cost = IceTower.cost
        self.initrange = IceTower.initrange
        self.initdamage = IceTower.initdamage
        self.initreload = IceTower.initreload
        self.initslowtime = IceTower.initslowtime
        self.initslowpercent = IceTower.initslowpercent
        self.type = IceTower.type
        self.slowtime = 3
        self.slowpercent = .8
        self.attackair = True
        self.attacktype = 'multi'
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
        self.push = 20
        self.type = WindTower.type
        self.attackair = True
        self.attackground = False
        self.attacktype = 'multi'
        self.shotimage = "gust.png"
        self.hasTurret = True
        self.loadTurret()
        if self.towerGroup.active:
                self.turret.source = os.path.join('towerimgs', self.type, "turret.gif")
        self.active = False
        self.allowedshots = 1

available_tower_list =[FireTower, IceTower, GravityTower, WindTower, LifeTower]
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
        Localdefs.iconlist.append(self)
        try:
            self.imgstr = tower[5]
            self.img = Utilities.imgLoad(self.imgstr)

        except:
            self.imgstr = str(os.path.join('towerimgs','0.png'))
            self.img = Utilities.imgLoad(self.imgstr)
        self.rect = Utilities.createRect(self.img.pos, self.img.size, self)