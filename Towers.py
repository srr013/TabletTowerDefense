
import os
import localdefs
import math, operator
import re

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
        localdefs.towerlist.append(self)

        self.size = (Map.squsize*2-1, Map.squsize*2-1)
        self.rect = Utilities.createRect(self.pos, self.size, instance=self)
        self.squareheight = 2
        self.squarewidth = 2
        self.towerwalls = self.genWalls()

        self.imageNum = 0
        self.imagestr = os.path.join('towerimgs', "Blue"+str(self.imageNum) + '.png')
        self.image = Utilities.imgLoad(self.imagestr)
        self.image.pos = self.pos
        self.image.size = self.size
        self.currentRotation = 0
        self.add_widget(self.image)

        self.lastNeighborCount = 0
        self.neighborFlag = 'update'
        self.neighbors = self.getNeighbors() #neighbors is a directional dict 'left':towerobj
        self.towerGroup = None
        self.getGroup()

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

        print (localdefs.towerGroupDict[self.type])

    def getNeighbors(self):
        neighbors = {}
        count = 0
        list = ''
        for tower in localdefs.towerlist:
            if tower.rect_x == self.rect_x - 2 * Map.squsize and tower.rect_y == self.rect_y and tower.type == self.type:
                neighbors['left'] = tower
                count+=1
                list +='l'
            if tower.rect_x == self.rect_x + 2 * Map.squsize and tower.rect_y == self.rect_y and tower.type == self.type:
                neighbors['right'] = tower
                count+=1
                list +='r'
            if tower.rect_y == self.rect_y + 2 * Map.squsize and tower.rect_x == self.rect_x and tower.type == self.type:
                neighbors['up'] = tower
                count += 1
                list+='u'
            if tower.rect_y == self.rect_y - 2 * Map.squsize and tower.rect_x == self.rect_x and tower.type == self.type:
                neighbors['down'] = tower
                count += 1
                list += 'd'


        if count > 0:
            if count != self.lastNeighborCount:
                print ("count:",count, self.lastNeighborCount, self)
                self.neighborFlag = 'update'
            neighbors['count'] = count
            self.lastNeighborCount = count
            neighbors['list'] = list


        return neighbors

    def getGroup(self):
        if not self.neighbors:
            self.towerGroup =  TowerGroup.TowerGroup(self.type)
        else:
            numAdjacent = self.neighbors['count']
            towerAdjacent = self.neighbors['list']
            letter = towerAdjacent[0]
            image = numAdjacent

            if image >= 1:
                if letter == 'd':
                    self.towerGroup = self.neighbors['down'].towerGroup

                elif letter == 'u':
                    self.towerGroup = self.neighbors['up'].towerGroup

                elif letter == 'r':
                    self.towerGroup = self.neighbors['right'].towerGroup

                elif letter == 'l':
                    self.towerGroup = self.neighbors['left'].towerGroup


                self.getImage()
                x = 0
                while  x < len(towerAdjacent):
                    letter = towerAdjacent[x]
                    if letter == 'l':
                        self.neighbors['left'].neighbors = self.neighbors['left'].getNeighbors()
                        self.neighbors['left'].getImage()
                        for tower in self.neighbors['left'].towerGroup.towerSet:
                            tower.towerGroup = self.towerGroup
                    elif letter == 'r':
                        self.neighbors['right'].neighbors = self.neighbors['right'].getNeighbors()
                        self.neighbors['right'].getImage()
                        for tower in self.neighbors['right'].towerGroup.towerSet:
                            tower.towerGroup = self.towerGroup
                    elif letter == 'u':
                        self.neighbors['up'].neighbors = self.neighbors['up'].getNeighbors()
                        self.neighbors['up'].getImage()
                        for tower in self.neighbors['up'].towerGroup.towerSet:
                            tower.towerGroup = self.towerGroup
                    elif letter == 'd':
                        self.neighbors['down'].neighbors = self.neighbors['down'].getNeighbors()
                        self.neighbors['down'].getImage()
                        for tower in self.neighbors['down'].towerGroup.towerSet:
                            tower.towerGroup = self.towerGroup
                    x += 1

    def getImage(self):
        if not self.neighbors:
            return

        if self.neighbors['count'] == 4:
            self.imageNum = 4

        elif self.neighbors['count'] == 3:
            self.imageNum = 3

        elif self.neighbors['count'] == 2:
            if self.neighbors['list'] == 'lr' or self.neighbors['list'] == 'rl' \
                    or self.neighbors['list'] == 'ud' or self.neighbors['list'] == 'du':
                self.imageNum = '2_1'

            else:
                self.imageNum = '2_2'

        elif self.neighbors['count'] == 1:
            self.imageNum = 1

        self.updateImage()

    def getRotation(self):
        rotation = 0
        desiredRotation = 0
        if self.neighborFlag == 'update':
            print ("finding new rotation")
            if self.neighbors['list'] == 'l':
                desiredRotation = 180
            elif self.neighbors['list'] == 'u':
                desiredRotation = 90
            elif self.neighbors['list'] == 'd':
                desiredRotation = 270
            elif self.neighbors['list'] == 'r':
                desiredRotation = 0

            elif self.neighbors['list'] == 'lr' or self.neighbors['list'] == 'rl':
                desiredRotation = 0
            elif self.neighbors['list'] == 'ud' or self.neighbors['list'] == 'du':
                desiredRotation = 90


            elif self.neighbors['list'] == 'ur' or self.neighbors['list'] == 'ru':
                desiredRotation = 0
            elif self.neighbors['list'] == 'ul' or self.neighbors['list'] == 'lu':
                desiredRotation = 90
            elif self.neighbors['list'] == 'ld' or self.neighbors['list'] == 'dl':
                desiredRotation = 180
            elif self.neighbors['list'] == 'rd' or self.neighbors['list'] == 'dr':
                desiredRotation = 270

            elif self.neighbors['list'] == 'urd' or self.neighbors['list'] == 'rud' or self.neighbors['list'] == 'dur' \
                    or self.neighbors['list'] == 'udr' or self.neighbors['list'] == 'rdu' or self.neighbors['list'] == 'dru':
                desiredRotation = 0
            elif self.neighbors['list'] == 'lrd' or self.neighbors['list'] == 'rld' or self.neighbors['list'] == 'dlr'\
                    or self.neighbors['list'] == 'ldr' or self.neighbors['list'] == 'rdl' or self.neighbors['list'] == 'drl':
                desiredRotation = 270
            elif self.neighbors['list'] == 'dlu' or self.neighbors['list'] == 'uld' or self.neighbors['list'] == 'lud' \
                    or self.neighbors['list'] == 'dul' or self.neighbors['list'] == 'udl' or self.neighbors['list'] == 'ldu':
                desiredRotation = 180
            elif self.neighbors['list'] == 'lur' or self.neighbors['list'] == 'rlu' or self.neighbors['list'] == 'ulr' \
                    or self.neighbors['list'] =='lru' or self.neighbors['list']=='rul' or self.neighbors['list']=='url':
                desiredRotation = 90
            print ("current/desired rotation:",  self.currentRotation, desiredRotation,self.neighbors['list'])
            rotation = abs(self.currentRotation - desiredRotation)
            if self.currentRotation > desiredRotation:
                rotation = -rotation
            self.currentRotation = desiredRotation

            return rotation

        else:
            return 0

    def updateImage(self):
        rotation = self.getRotation()
        print("num, rot", self.imageNum, rotation, "flag, count:", self.neighborFlag, self.lastNeighborCount)
        if self.neighborFlag == 'update':
            print ("new image")
            self.imagestr = os.path.join('towerimgs', "Blue"+str(self.imageNum) + '.png')
            self.image.source = self.imagestr
            self.neighborFlag = ''
        if rotation != 0 :
            print ("rotate image")
            with self.image.canvas.before:
                PushMatrix()
                self.rot = Rotate(axis=(0,0,1), origin=self.image.center, angle = rotation)
            with self.image.canvas.after:
                PopMatrix()


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

    # def genButtons(self):
    #     '''Called when a tower is selected via mouse. Places the buttons around the tower.'''
    #     font = pygame.font.Font(None,20)
    #     ##generate a list of abilities from the currently hardcoded list in Towers.py
    #     ##doesFit() returns true if the tower is not in tower.upgrades list, which keeps track of whether the tower has been upgraded yet
    #     abilitylist = [i for i in localdefs.towerabilitylist if (i.doesFit(self) and (i.shortname in Player.player.modDict['towerAbilities']))]
    #     ##buttonnum could change w/ tower abilities (=len(abilitylist) but this makes for inconsistent ability placement on the circle
    #     buttonnum = 5 ##UPDATE this number if additional functions are added that apply to all towers
    #     if buttonnum:
    #         inddeg = (2.0*math.pi)/buttonnum
    #         self.buttonlist = list()
    #         radius = 50
    #         ##generate the list of abilities per tower
    #         for ind,ta in enumerate(abilitylist):
    #             try:taimg = Utilities.imgLoad(os.path.join("upgradeicons",ta.shortname+".jpg"))
    #             except:
    #                 taimg = pygame.Surface((20,20))
    #                 taimg.fill((90,90,255))
    #             tarect = pygame.Rect((0,0),(20,20))
    #             tarect.center=(self.rect.centerx,self.rect.centery)
    #             tarect.move_ip(radius*math.cos((ind+1)*inddeg),radius*math.sin((ind+1)*inddeg))
    #             ##setup text to the side of the upgradeicon
    #             info = font.render("%s: -%dcr" % (ta.name,ta.cost(self)),1,(0,0,0))
    #             infopos = info.get_rect(center=(self.rect.centerx+(radius+info.get_width()+10)*math.cos((ind+1)*inddeg),self.rect.centery+(radius+info.get_height()+10)*math.sin((ind+1)*inddeg)))
    #             infopos.left=max(0,infopos.left)
    #             infopos.right=min(Map.scrwid,infopos.right)
    #             infopos.top=max(0,infopos.top)
    #             infopos.bottom=min(Map.scrhei,infopos.bottom)
    #             self.buttonlist.append((taimg,tarect,info,infopos,ta.apply))

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

class FireTower(Tower):
    type = "Fire"
    cost = 5
    initdamage = 30
    initrange = 3*30
    initreload = 2
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
        # self.imagestr = FighterTower.imagestr
        # self.image = Utilities.imgLoad(self.imagestr)
        # self.image.size = self.size
        # self.image.pos = self.pos
        # self.add_widget(self.image)
        self.attackair = False
        self.shotimage = "cannonball.png"

class LifeTower(Tower):
    type = "Life"
    cost = 10
    initrange = 10*30
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
        #self.imagestr = ArcherTower.imagestr
        #self.image = Utilities.imgLoad(self.imagestr)
        #self.add_widget(self.image)
        self.attackair = True
        self.shotimage = "arrow.png"

class GravityTower(Tower):
    type = "Gravity"
    cost = 15
    initrange = 3*30
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
        # self.imagestr = MineTower.imagestr
        # self.image = Utilities.imgLoad(self.imagestr)
        # self.image.pos = self.pos
        # self.image.size = self.size
        # self.add_widget(self.image)
        self.shotimage = "waves.png"
        self.attackair=False
        self.attacktype = "multi"

class WaterTower(Tower):
    type = "Water"
    cost = 10
    initrange = 2
    initdamage = 0
    initreload = 1.0
    imagestr = os.path.join('towerimgs', 'Water', 'icon.png')
    def __init__(self,pos, **kwargs):
        Tower.__init__(self, pos, **kwargs)
        self.pos = pos
        self.cost = WaterTower.cost
        self.initrange = WaterTower.initrange
        self.initdamage = WaterTower.initdamage
        self.initreload = WaterTower.initreload
        self.type = WaterTower.type
        # self.imagestr = SlowTower.imagestr
        # self.image = Utilities.imgLoad(self.imagestr)
        # self.image.pos = self.pos
        # self.image.size = self.size
        # self.add_widget(self.image)
        self.attackair = True
        self.shotimage = "freeze.png"
        self.attacktype = 'multi'

class WindTower(Tower):
    type = "Wind"
    cost = 35
    initrange = 6
    initdamage = 8
    initreload = 1.0
    imagestr = os.path.join('towerimgs', 'Wind', 'icon.png')
    def __init__(self,pos, **kwargs):
        Tower.__init__(self, pos, **kwargs)
        self.pos = pos
        self.cost = WindTower.cost
        self.initrange = WindTower.initrange
        self.initdamage = WindTower.initdamage
        self.initreload = WindTower.initreload
        self.type = "Wind"
        # self.imagestr = AntiAirTower.imagestr
        # self.image = Utilities.imgLoad(self.imagestr)
        # self.image.pos = self.pos
        # self.image.size = self.size
        # self.add_widget(self.image)
        self.attackair = True
        self.attackground = False
        self.shotimage = "bolt.png"

available_tower_list =[LifeTower, FireTower, WaterTower, GravityTower, WindTower]
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


