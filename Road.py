import os
from kivy.graphics import *
from kivy.uix.image import Image
from kivy.animation import Animation

import Localdefs
import Map


class Road(Image):
    def __init__(self, localized,globalized, index, pathnum, **kwargs):
        super(Road, self).__init__(**kwargs)
        self.pos = (localized[0], localized[1])
        self.globalized = (globalized[0], globalized[1])
        self.allow_stretch = True
        self.size = (Map.mapvar.squsize, Map.mapvar.squsize)
        self.squpos = ((self.globalized[0] / Map.mapvar.squsize), (self.globalized[1] / Map.mapvar.squsize))
        Map.mapvar.roadcontainer.add_widget(self)
        Localdefs.roadlist.append(self)
        self.iceNeighbor = False
        self.active = False
        self.imagestr = self.getRoadColor()
        self.source = self.imagestr
        self.direction = Map.mapvar.roaddirlists[pathnum][index]
        self.center = (self.pos[0] + .5 * self.size[0], self.pos[1] + .5 * self.size[1])
        self.setDirection()
        self.bind(size=self.bindings)

    def getRoadColor(self):
        if self.iceNeighbor:
            return os.path.join('backgroundimgs', 'blueroadarrow.png')
        redlist = list(Map.mapvar.startpoint)
        for road in redlist:
            if road == (1, 9):
                redlist.append((2, 9))
            elif road == (10, 1):
                redlist.append((10, 2))
        if self.squpos in redlist:
            return os.path.join('backgroundimgs', 'redroadarrow.png')

        else:
            return os.path.join('backgroundimgs', 'roadarrow.png')

    def getIceNeighbor(self):
        for group in Localdefs.towerGroupDict['Ice']:
            if self in group.adjacentRoads:
                self.iceNeighbor = True
                return
        self.iceNeighbor = False

    def createIceRoad(self):
        self.iceNeighbor = True
        self.imagestr = self.getRoadColor()
        self.source = self.imagestr
        with self.canvas.before:
            self.rgba = Color(1, 1, 1, 0)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.animation = Animation(rgba=[0, 1, 1, .5], duration=.5)
        self.closeanimation = Animation(rgba=[1, 1, 1, 0], duration=.1)

    def createBurnRoad(self, shot):
        self.burnDmg = shot.burnDmg
        with self.canvas.before:
            self.rgba = Color(1, 0, 0, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.animation = Animation(rgba=[1,.7,0,1], duration = 2.5) + Animation(rgba=[1, .4, 0, .4], duration= 2.5) + Animation(rgba=[1,1,1,0], duration = .1)
        self.animation.bind(on_complete = self.removeBurnRoad)
        self.animation.start(self.rgba)
        Localdefs.burnroadlist.append(self)

    def removeBurnRoad(self, *args):
        Localdefs.burnroadlist.remove(self)
        with self.canvas.before:
            self.rgba = Color(1, 1, 1, 0)
            self.rect = Rectangle(size=self.size, pos=self.pos)

    def bindings(self):
        self.size = (Map.mapvar.squsize, Map.mapvar.squsize)
        self.squpos = (self.pos[0] / Map.mapvar.squsize, self.pos[1] / Map.mapvar.squsize)
        self.center = (self.pos[0] + .5 * self.size[0], self.pos[1] + .5 * self.size[1])

    def burnEnemy(self,enemy):
        if enemy.burntime <= 0:
            enemy.burntime = 5
            enemy.color = [1,.5,0,1]
            enemy.burnDmg = self.burnDmg

    def setDirection(self):
        angle = 0
        if self.direction == 'u':
            angle = 90
        if self.direction == 'l':
            angle = 180
        if self.direction == 'd':
            angle = 270
        if angle != 0:
            with self.canvas.before:
                PushMatrix()
                Rotate(axis=(0, 0, 1), origin=self.center, angle=angle)
            with self.canvas.after:
                PopMatrix()
