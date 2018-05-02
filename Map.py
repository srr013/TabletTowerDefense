import os
from kivy.core.window import Window
from kivy.graphics import *
from kivy.uix.widget import Widget
from kivy.uix.image import Image

import GUI
import GUI_Templates
import Localdefs
import Pathfinding
import Playfield
import Road
import Utilities
import Wall
import __main__

wallrectlist = list()


def gen_border_walls():
    '''generates a list of walls around the border of the map'''
    x = 0
    while x < mapvar.squwid:
        y = 0
        Wall.Wall(squpos=(x, y))
        y = (mapvar.playhei/mapvar.squsize)
        Wall.Wall(squpos=(x, y))
        y = 1
        Wall.Wall(squpos=(x, y))
        y = (mapvar.playhei/mapvar.squsize) + 1
        Wall.Wall(squpos=(x, y))
        y = (mapvar.playhei/mapvar.squsize) + 2
        Wall.Wall(squpos=(x, y))
        x += 1
    y = 0
    while y <= mapvar.squhei:
        x = 0
        Wall.Wall(squpos=(x, y))
        x = mapvar.squwid - 1
        Wall.Wall(squpos=(x, y))
        x = 1
        Wall.Wall(squpos=(x, y))
        x = mapvar.squwid
        Wall.Wall(squpos=(x, y))
        y += 1


class Map():
    def __init__(self):
        self.numpaths = 1
        self.difficulty = 'easy'
        self.pathrectlist = None
        self.pointmovelist = None
        self.endrect = None
        self.mapdict = dict()
        self.pointmovelists = list()
        self.pointflymovelists = list()
        self.pathrectlists = list()
        self.dirmovelists = list()
        self.enemymovelists = list()
        self.roaddirlists = list()
        self.total_waves = 0
        self.movelists = list()
        self.flymovelists = list()
        self.flylistgenerated = False
        self.movelistnum = -1
        self.blockedSquare = None
        # The following variables control game and field sizing
        self.scrwid = Window.width
        self.scrhei = Window.height
        self.squsize = self.scrwid / 34
        self.playhei = self.squsize * 16 # the top line of the play area should always be 16 squsize from the bottom
        self.playwid = self.squsize * 32
        self.border = 2 * self.squsize
        self.squborder = self.border / self.squsize
        self.waveseconds = 20.5
        self.squwid = int(self.scrwid / self.squsize) - 1  # Window is 33 squ wide
        self.squhei = int(self.scrhei / self.squsize) - 1  # Window is 20 squ high

    def genmovelists(self):
        '''Generate the movement list for enemys and path blitting'''
        ##zero out the lists to start fresh. Otherwise the append allows multiple lists.
        self.pointmovelists = []
        self.pathrectlists = []
        self.dirmovelists = []
        self.enemymovelists = []
        self.roaddirlists = []

        for movelist in self.movelists:
            ##translate tiles to pixels. SQU represents a tile width or height
            pointlist = list([(point[0] * self.squsize, point[1] * self.squsize) for point in movelist[0]])
            enemymovelist = list([(point[0] * self.squsize, point[1] * self.squsize) for point in movelist[2]])
            ##create a rect for each set of points to connect the path from one point to another
            pathrectlist = list([Utilities.createRect(pointlist[ind], (
                pointlist[ind + 1][0] - pointlist[ind][0], pointlist[ind + 1][1] - pointlist[ind][1])) for ind in
                                 range(len(pointlist) - 2)])
            self.pointmovelists.append(pointlist)
            self.enemymovelists.append(enemymovelist)
            self.pathrectlists.append(pathrectlist)
            self.roaddirlists.append(movelist[1])
            self.dirmovelists.append(movelist[3])

        if not self.flylistgenerated:
            self.pointflymovelists = []
            self.dirflymovelists = []
            self.enemyflymovelists = []
            for movelist in self.flymovelists:
                pointmovelist = list([(point[0] * self.squsize, point[1] * self.squsize) for point in movelist[0]])
                enemymovelist = list([(point[0] * self.squsize, point[1] * self.squsize) for point in movelist[2]])
                self.pointflymovelists.append(pointmovelist)
                self.enemyflymovelists.append(enemymovelist)
                self.dirflymovelists.append(movelist[3])
                self.flylistgenerated = True


    def backgroundInit(self):
        self.backgroundimg = Widget()
        self.background = Playfield.playField()
        self.backgroundimg.size = self.background.size
        self.backgroundimg.pos = self.background.pos
        self.enemypanel = GUI_Templates.EnemyPanel()
        self.towerpanel = GUI_Templates.TowerPanel()
        self.baseimg = None
        self.triangle = None
        self.towerRange = None
        self.towerRangeExclusion = None
        self.alertStreamer = GUI.gui.createAlertStreamer()
        self.startpoint = None
        self.waveOrder = 'standard'
        with self.backgroundimg.canvas:
            Color(.8,.8,.8,.3)
            self.shaderRect = Rectangle(size=__main__.Window.size, pos=(0,0))
            Color(1,1,1,1)
            self.playfieldRect = Rectangle(size=(self.playwid - self.border, self.playhei-self.border), pos= (self.border, self.border))
            Color(0, 0, 0, .6)
            self.borderLine = Line(points=[self.squsize * self.squborder, self.squsize * self.squborder,
                                           self.squsize * self.squborder,
                                           self.playhei,
                                           self.playwid,
                                           self.playhei,
                                           self.playwid, self.squsize * self.squborder,
                                           self.squsize * self.squborder, self.squsize * self.squborder], width=1.3)

        self.background.bind(size=self.bindings)

        self.background.add_widget(self.backgroundimg)
        self.backgroundimg.add_widget(self.alertStreamer)

        self.towercontainer = Utilities.container()
        self.backgroundimg.add_widget(self.towercontainer)

        self.roadcontainer = Utilities.container()
        self.backgroundimg.add_widget(self.roadcontainer)

        self.enemycontainer = Utilities.container()
        self.backgroundimg.add_widget(self.enemycontainer)

        self.shotcontainer = Utilities.container()
        self.backgroundimg.add_widget(self.shotcontainer)

        self.wallcontainer = Utilities.container()
        self.backgroundimg.add_widget(self.wallcontainer)

        self.towerdragimagecontainer = Utilities.container()
        self.backgroundimg.add_widget(self.towerdragimagecontainer)
        self.bindings()
        return self.background

    def bindings(self, *args):
        self.backgroundimg.size = self.background.size
        with self.backgroundimg.canvas.before:
            self.shaderRect = Rectangle(size=self.backgroundimg.size, pos=self.backgroundimg.pos)
        self.scrhei = __main__.Window.height
        self.scrwid = __main__.Window.width
        self.squsize = self.scrwid / 34
        self.playhei = self.squsize * 16
        self.playwid = self.squsize * 32
        self.border = 2 * self.squsize
        self.squborder = self.border / self.squsize
        self.squwid = int(self.scrwid / self.squsize) - 1
        self.squhei = int(self.scrhei / self.squsize) - 1
        self.playfieldRect.size = (self.playwid - self.border, self.playhei-self.border)
        self.playfieldRect.pos = (self.border, self.border)
        self.borderLine.points = [self.squsize * self.squborder, self.squsize * self.squborder,
                                           self.squsize * self.squborder,
                                           self.playhei,
                                           self.playwid,
                                           self.playhei,
                                           self.playwid, self.squsize * self.squborder,
                                           self.squsize * self.squborder, self.squsize * self.squborder]
        self.backgroundimg.remove_widget(self.baseimg)
        GUI.gui.alertStreamerBinding()
        GUI.gui.bindings()
        self.genmovelists()
        if self.baseimg:
            self.roadGen()
        # print "Mapvar squsize", self.squsize, self.borderLine.points, self.scrwid, self.scrhei

    def checkDupRoad(self, square):
        for child in self.roadcontainer.children:
            if child.pos[0] == square[0] and child.pos[1] == square[1]:
                return True

        return False

    def roadGen(self):
        self.roadcontainer.clear_widgets()
        Localdefs.roadlist = list()
        for pathnum in range(0, len(self.movelists)):
            x = 0
            for square in self.pathrectlists[pathnum]:
                if pathnum > 0:
                    if self.checkDupRoad(square):
                        break
                Road.Road(square, x, pathnum)
                x += 1

        if not self.baseimg:
            self.baseimg = Image(source=os.path.join('backgroundimgs', 'Base.png'),
                                 allow_stretch = True, size = (self.squsize * 3-1, self.squsize * 3-1))
            self.baseimg.pos = (
                self.basepoint[0] * self.squsize, self.basepoint[1] * self.squsize - (self.baseimg.size[1] / 3))
            self.backgroundimg.add_widget(self.baseimg)
        else:
            self.baseimg.pos = (
                self.basepoint[0] * self.squsize, self.basepoint[1] * self.squsize - (self.baseimg.size[1] / 3))
        # Kivy hierarchy: background (scatter and float layouts)> backgroundimg (on float) > containers

    def loadMap(self):
        '''Load a particular map
        mapname: the name of the map selected
        This is a legacy function and not fully utilized'''
        # called by main. Uses functions to load the map and map properties
        self.genmovelists()
        self.getStartPoints()
        return self.backgroundInit()

    def getStartPoints(self):
        if self.numpaths == 1:
            self.startpoint = [(1, 9)]
            self.basepoint = (26, 9)
        elif self.numpaths == 2:
            self.startpoint = [(1, 9), (10, 16)]
            self.basepoint = (24, 9)
        else:
            self.startpoint = [(1, 9), (10, 16), (10, 1)]
            self.basepoint = (23, 9)  # update newPath/flyPath below too


mapvar = Map()


class Path():
    def __init__(self):
        pass

    def createPath(self):
        if mapvar.pointmovelist is not None:
            self.movelist = mapvar.pointmovelists[0][:]
        gen_border_walls()
        self.border_walls = list([(child.squpos[0], child.squpos[1]) for child in mapvar.wallcontainer.children])
        self.wall_list = None

    def get_wall_list(self):
        walls = list([(child.squpos[0], child.squpos[1]) for child in mapvar.wallcontainer.children])
        return walls


path = Path()
# newPath = Pathfinding.GridWithWeights(mapvar.squwid, mapvar.squhei - 1, 0, (28, 9))
flyPath = Pathfinding.neighborGridwithWeights(mapvar.squwid, mapvar.squhei - 1, 0, (28, 9))
myGrid = Pathfinding.neighborGridwithWeights(mapvar.squwid, mapvar.squhei - 1, 0, (28, 9))

