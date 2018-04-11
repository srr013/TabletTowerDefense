import os
from kivy.graphics import *

import Localdefs
import Map
import Utilities


class Road():
    def __init__(self, pos, index, pathnum):
        self.image = Utilities.imgLoad(source=os.path.join('backgroundimgs', 'roadarrow.png'), pos=(pos[0], pos[1]))
        self.image.active = False
        self.image.allow_stretch = True
        self.image.size = (Map.mapvar.squsize, Map.mapvar.squsize)
        self.image.squpos = (self.image.pos[0] / Map.mapvar.squsize, self.image.pos[1] / Map.mapvar.squsize)
        self.pos = self.image.pos
        self.size = self.image.size
        Map.mapvar.roadcontainer.add_widget(self.image)
        Localdefs.roadlist.append(self)
        self.iceNeighbor = False
        self.active = False
        self.imagestr = self.getRoadColor()
        self.image.source = self.imagestr
        self.image.bind(size=self.bindings)
        self.direction = Map.mapvar.dirmovelists[pathnum][index]
        self.center = (self.pos[0] + .5 * self.size[0], self.pos[1] + .5 * self.size[1])
        self.setDirection()

    def getRoadColor(self):
        if self.iceNeighbor:
            return os.path.join('backgroundimgs', 'blueroadarrow.png')
        redlist = list(Map.mapvar.startpoint)
        for road in redlist:
            if road == (1,9):
                redlist.append((2,9))
            if road == (10,16):
                redlist.append((10,15))
            if road == (10,1):
                redlist.append((10,2))
        if self.image.squpos in redlist:
            return os.path.join('backgroundimgs', 'redroadarrow.png')

        else:
            return os.path.join('backgroundimgs', 'roadarrow.png')

    def getIceNeighbor(self):
        for group in Localdefs.towerGroupDict['Ice']:
            if self in group.adjacentRoads:
                self.iceNeighbor = True
                return
        self.iceNeighbor = False

    def bindings(self):
        self.image.size = (Map.mapvar.squsize, Map.mapvar.squsize)
        self.image.squpos = (self.image.pos[0] / Map.mapvar.squsize, self.image.pos[1] / Map.mapvar.squsize)
        self.size = self.image.size
        self.center = (self.pos[0] + .5 * self.size[0], self.pos[1] + .5 * self.size[1])

    def setDirection(self):
        angle = 0
        if self.direction == 'u':
            angle = 90
        if self.direction == 'l':
            angle = 180
        if self.direction == 'd':
            angle = 270
        if angle != 0:
            with self.image.canvas.before:
                PushMatrix()
                Rotate(axis=(0, 0, 1), origin=self.center, angle=angle)
            with self.image.canvas.after:
                PopMatrix()
