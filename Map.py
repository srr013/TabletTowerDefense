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
import Messenger
import InfoPanel
import Player

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
        self.background = None
        if Player.player.store.exists('gameplay'):
            self.waveOrder = Player.player.store.get('gameplay')['waveorder']
            self.numpaths = Player.player.store.get('gameplay')['numpaths']
            self.difficulty = Player.player.store.get('gameplay')['difficulty']
        else:
            self.numpaths = 1
            self.difficulty = 'easy'
            self.waveOrder = 'standard'
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
            enemymovelist = list([self.background.to_local(point[0] * self.squsize, point[1] * self.squsize) for point in movelist[2]])
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
                enemymovelist = list([self.background.to_local(point[0] * self.squsize, point[1] * self.squsize) for point in movelist[2]])
                self.pointflymovelists.append(pointmovelist)
                self.enemyflymovelists.append(enemymovelist)
                self.dirflymovelists.append(movelist[3])
                self.flylistgenerated = True

    def backgroundInit(self):
        self.baseimg = None
        self.triangle = None
        self.towerRange = None
        self.towerRangeExclusion = None
        self.alertStreamer = None
        self.startpoint = None

        self.background.bind(size=self.bindings)

        self.towercontainer = Utilities.Container("towercontainer")
        self.background.add_widget(self.towercontainer)
        self.roadcontainer = Utilities.Container("roadcontainer")
        self.background.add_widget(self.roadcontainer)
        self.enemycontainer = Utilities.Container("enemycontainer")
        self.background.add_widget(self.enemycontainer)
        self.shotcontainer = Utilities.Container("shotcontainer")
        self.background.add_widget(self.shotcontainer)
        self.wallcontainer = Utilities.Container("wallcontainer")
        self.background.add_widget(self.wallcontainer)
        self.towerdragimagecontainer = Utilities.Container("towerdragimagecontainer")
        self.background.add_widget(self.towerdragimagecontainer)
        self.towerplaceholdercontainer = Utilities.Container("towerplaceholercontainer")
        self.background.add_widget(self.towerplaceholdercontainer)
        self.popupcontainer = Utilities.Container("popupcontainer")
        self.background.add_widget(self.popupcontainer)
        self.bindings()

    def bindings(self, *args):
        self.scrhei = __main__.Window.height
        self.scrwid = __main__.Window.width
        self.squsize = self.scrwid / 34
        self.playhei = self.squsize * 16
        self.playwid = self.squsize * 32
        self.border = 2 * self.squsize
        self.squborder = self.border / self.squsize
        self.squwid = int(self.scrwid / self.squsize) - 1
        self.squhei = int(self.scrhei / self.squsize) - 1
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
                localized = (self.background.to_local(square[0], square[1]))
                localized = (localized[0],localized[1],square[2],square[3])
                if pathnum > 0:
                    if self.checkDupRoad(localized):
                        break
                Road.Road(localized, square, x, pathnum)
                x += 1

        if not self.baseimg:
            self.baseimg = Image(source=os.path.join('backgroundimgs', 'Base.png'),
                                 allow_stretch = True, size = (__main__.app.root.squsize * 3-3, __main__.app.root.squsize * 3-3), id = 'Base')
            pos = (
                self.basepoint[0] * __main__.app.root.squsize, self.basepoint[1] * __main__.app.root.squsize - (self.baseimg.size[1] / 3))
            pos = self.background.to_local(*pos)
            self.baseimg.pos = pos
            self.baseimg.type = 'Base'
            self.towercontainer.add_widget(self.baseimg)

        else:
            self.baseimg.pos = self.background.to_local(
                self.basepoint[0] * __main__.app.root.squsize, self.basepoint[1] * __main__.app.root.squsize - (self.baseimg.size[1] / 3))

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
        elif self.numpaths == 2:
            self.startpoint = [(1, 9), (10, 15)]
        else:
            self.startpoint = [(1, 9), (10, 15), (10, 1)]
        if self.difficulty == 'easy':
            self.basepoint = (26, 9)
        elif self.difficulty == 'medium':
            self.basepoint = (24, 9)
        else:
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

