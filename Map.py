import Utilities
import Localdefs
import Pathfinding
import os
import Playfield
import Road
import GUI
import main

from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.graphics import *

# winwid = 1020 #window width
# winhei = 600
# scrwid = winwid #Playable screen width.
# scrhei = winhei #Playable screen height.
# squsize = winwid/34
# mapoffset = (0,0) #offset of the playing field(including walls) in tiles
# border = 2*squsize
# squborder = border/squsize
# waveseconds = 20.5
# squwid = int(scrwid/squsize + mapoffset[0])+squborder*2 #playable field is 34 squ wide (including border)
# squhei = int(scrhei/squsize + mapoffset[1])+squborder #playable field is 24 squ high


wallrectlist = list()
def gen_border_walls():
    '''generates a list of walls around the border of the map'''
    walls = []
    x = mapvar.mapoffset[0]
    while x < mapvar.squwid:
        y=mapvar.mapoffset[1]
        walls.append((x,y))
        y = mapvar.squhei
        walls.append((x,y))
        y = mapvar.mapoffset[1]+1
        walls.append((x, y))
        y = mapvar.squhei-1
        walls.append((x, y))
        x += 1
    y = mapvar.mapoffset[1]
    while y <= mapvar.squhei:
        x=mapvar.mapoffset[0]
        walls.append((x,y))
        x = mapvar.squwid-1
        walls.append((x,y))
        x = mapvar.mapoffset[0]+1
        walls.append((x, y))
        x = mapvar.squwid
        walls.append((x, y))
        y += 1
    for wall in walls:
        rect = Utilities.createRect(wall[0],wall[1], mapvar.squsize, mapvar.squsize)
        wallrectlist.append(rect)
    return walls

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
        self.total_waves = 0
        self.movelists = list()
        self.flymovelists = list()
        self.flylistgenerated = False
        self.movelistnum = -1
        self.updatePath = True
        self.openPath = True
        self.winwid = 1020  # window width
        self.winhei = 600
        self.scrwid = self.winwid  # Playable screen width.
        self.scrhei = self.winhei  # Playable screen height.
        self.squsize = self.winwid / 34
        self.mapoffset = (0, 0)  # offset of the playing field(including walls) in tiles
        self.border = 2 * self.squsize
        self.squborder = self.border / self.squsize
        self.waveseconds = 20.5
        self.squwid = int(
            self.scrwid / self.squsize + self.mapoffset[0]) + self.squborder * 2  # playable field is 34 squ wide (including border)
        self.squhei = int(self.scrhei / self.squsize + self.mapoffset[1]) + self.squborder  # playable field is 24 squ high

    def genmovelists(self):
        '''Generate the movement list for enemys and path blitting'''
        ##zero out the lists to start fresh. Otherwise the append allows multiple lists.
        self.pointmovelists = []
        self.pathrectlists = []
        self.dirmovelists = []

        for movelist in self.movelists:
            ##translate tiles to pixels. SQU represents a tile width or height
            pointlist = list([(point[0]*self.squsize,point[1]*self.squsize) for point in movelist[0]])
            #change movelist[0] to [2] for enemies to move along abbreviated list. Issues with enemy pathing when path changes if so.
            enemymovelist = list([(point[0]*self.squsize,point[1]*self.squsize) for point in movelist[0]])
            dirmovelist = movelist[1]
            ##create a rect for each set of points to connect the path from one point to another
            pathrectlist = list([Utilities.createRect(pointlist[ind],(pointlist[ind+1][0]-pointlist[ind][0],pointlist[ind+1][1]-pointlist[ind][1])) for ind in range(len(pointlist)-2)])
            self.pointmovelists.append(enemymovelist)
            self.pathrectlists.append(pathrectlist)
            self.dirmovelists.append(dirmovelist)

        if not self.flylistgenerated:
            for movelist in self.flymovelists:
                ##translate tiles to pixels. SQU represents a tile width or height
                # pointlist = list([(point[0]*self.squsize,point[1]*self.squsize) for point in movelist[0]])
                #change movelist[0] to [2] for enemies to move along abbreviated list. Issues with enemy pathing when path changes if so.
                enemymovelist = list([(point[0]*self.squsize,point[1]*self.squsize) for point in movelist[0]])
                # dirmovelist = movelist[1]
                ##create a rect for each set of points to connect the path from one point to another
                # pathrectlist = list([Utilities.createRect(pointlist[ind],(pointlist[ind+1][0]-pointlist[ind][0],pointlist[ind+1][1]-pointlist[ind][1])) for ind in range(len(pointlist)-2)])
                self.pointflymovelists.append(enemymovelist)
                self.flylistgenerated = True
                # self.pathrectlists.append(pathrectlist)
                #self.dirmovelists.append(dirmovelist)

    # def getmovelist(self):
    #     '''Get the mvoe list from file if it is a pre-set path'''
    #     ##pulls data from movefile.txt for the appropriate level to create the map.
    #     f = open(os.path.join('mapfiles',str(self.current),'movefile.txt'))
    #     line = f.readline().strip().split(',')
    #     self.basepoint = (int(line[0])+self.mapoffset[0],int(line[1])+self.mapoffset[1])
    #     line = f.readline().strip().split(',')
    #     self.startpoint = (int(line[0])+self.mapoffset[0], int(line[1])+self.mapoffset[1])
    #     lines = f.readlines()
    #     f.close()
    #
    #
    #     ##hook for use of new pathinfinding vs set path. IGNORE should be second line in movefile.txt
    #     if lines[0] == "IGNORE":
    #         pass
    #
    #     else:
    #         for line in lines:
    #             ##creates a list for each "path" indicated in the movefile. A negative value in x or y indicates a new path/list
    #             ##the values in the file are in "tiles". the number in the file represents # of tiles between the tile and origin
    #             line = line.strip().split(',')
    #             ##use set path
    #             if int(line[0])<0 or int(line[1])<0 or int(line[0])>(self.scrwid) or int(line[1])>(self.scrhei/self.squsize):
    #                 self.movelists.append(list())
    #                 self.movelistnum+=1
    #             self.movelists[self.movelistnum].append((int(line[0]),int(line[1])))
    #     self.genmovelists()


    # def getmapproperties(self):
    #     '''Open file and create dict of wave data'''
    #     def mapPropertiesGen(self):
    #         self.total_waves = 0
    #         ##hardcoded to use on Pathfinding map for the time being
    #         ##Using the wave# as dict keys, create a dict for the level indicating what troops to send
    #         f = open(os.path.join('mapfiles',self.current,'mapproperties.txt'))
    #         for line in f.readlines():
    #             if line[0]!='*':
    #                 self.total_waves += 1
    #                 line = line.strip().split('=')
    #                 linepro = line[1].strip().split(',')
    #                 yield line[0],[float(each.strip()) for each in linepro]
    #     self.mapdict = dict(mapPropertiesGen(self))
    #     print self.mapdict



    def backgroundInit(self):
        self.backgroundimg = Widget()
        self.background = Playfield.playField()
        self.backgroundimg.size = self.background.size
        self.backgroundimg.pos = self.background.pos
        self.enemypanel = GUI.EnemyPanel()
        self.baseimg = None
        self.rect = None
        self.triangle = None
        self.towerRange = None
        with self.backgroundimg.canvas:
            Color(1,1,1,1)
            self.rect = Rectangle(size=self.backgroundimg.size, pos=self.backgroundimg.pos)
            Color(0,0,0,.6)
            self.borderLine = Line(points=[self.squsize * self.squborder, self.squsize * self.squborder,
                            self.squsize * self.squborder, self.scrhei - self.squsize * self.squborder,
                            self.scrwid - self.squsize * self.squborder, self.scrhei - self.squsize * self.squborder,
                            self.scrwid - self.squsize * self.squborder,self.squsize * self.squborder,
                            self.squsize * self.squborder, self.squsize * self.squborder], width=1)

        self.background.bind(size=self.bindings)

        self.background.add_widget(self.backgroundimg)

        self.towercontainer = Utilities.container()
        self.backgroundimg.add_widget(self.towercontainer)

        self.roadcontainer = Utilities.container()
        self.backgroundimg.add_widget(self.roadcontainer)

        self.enemycontainer = Utilities.container()
        self.backgroundimg.add_widget(self.enemycontainer)

        self.shotcontainer = Utilities.container()
        self.backgroundimg.add_widget(self.shotcontainer)

        self.cloudcontainer = Utilities.container()
        self.backgroundimg.add_widget(self.cloudcontainer)

        self.explosioncontainer = Utilities.container()
        self.backgroundimg.add_widget(self.explosioncontainer)

        return self.background

    def bindings(self, *args):
        self.backgroundimg.size = self.background.size
        self.rect.size = self.backgroundimg.size
        self.scrhei = main.Window.height
        self.scrwid = main.Window.width
        self.squsize = self.scrwid/34
        self.border = 2*self.squsize
        self.squborder = self.border/self.squsize
        self.squwid = int(self.scrwid / self.squsize + self.mapoffset[0]) + self.squborder * 2
        self.squhei = int(self.scrhei / self.squsize + self.mapoffset[1]) + self.squborder
        self.borderLine.points=[self.squsize * self.squborder, self.squsize * self.squborder,
                            self.squsize * self.squborder, self.scrhei - self.squsize * self.squborder,
                            self.scrwid - self.squsize * self.squborder, self.scrhei - self.squsize * self.squborder,
                            self.scrwid - self.squsize * self.squborder,self.squsize * self.squborder,
                            self.squsize * self.squborder, self.squsize * self.squborder]
        self.backgroundimg.remove_widget(self.baseimg)
        self.genmovelists()
        self.baseimg=None
        self.roadGen()
        #print "Mapvar squsize", self.squsize, self.borderLine.points, self.scrwid, self.scrhei

    def checkDupRoad(self,square):
        for child in self.roadcontainer.children:
            if child.pos[0] == square[0] and child.pos[1] == square[1]:
                return True

        return False

    def roadGen(self):
        self.roadcontainer.clear_widgets()
        Localdefs.roadlist = list()
        '''Generate the path and base and blit them'''
        #2 movelists are passed in currently. Only print tiles for the first, the ground move list. The flying move list should be the last list.
        for pathnum in range(0,len(self.movelists)):
            x=0
            for square in self.pathrectlists[pathnum]:
                if pathnum > 0:
                    if self.checkDupRoad(square):
                        break
                Road.Road(square,x,pathnum)
                x+=1

        if not self.baseimg:
            self.baseimg = Utilities.imgLoad(source=os.path.join('backgroundimgs', 'Base.png'))
            self.baseimg.allow_stretch = True
            self.baseimg.size = (self.squsize*3,self.squsize*3)
            self.baseimg.pos = (self.basepoint[0] * self.squsize-(self.baseimg.size[0]/3), self.basepoint[1] * self.squsize-(self.baseimg.size[1]/3))
            self.backgroundimg.add_widget(self.baseimg)
        #Kivy hierarchy: background (scatter and float layouts)> backgroundimg (on float) > containers


    def loadMap(self):
        '''Load a particular map
        mapname: the name of the map selected
        This is a legacy function and not fully utilized'''
        #called by main. Uses functions to load the map and map properties
        self.genmovelists()
        self.getStartPoints()
        return self.backgroundInit()

        # if os.path.exists(os.path.join('mapfiles',str(self.current))):
        #     # self.getmovelist()
        #     # self.getmapproperties()
        #     return self.backgroundInit()
        # else:
        #     print ("You Won!!!")
    def getStartPoints(self):
        if self.numpaths == 1:
            self.startpoint = [(1,9)]
        elif self.numpaths == 2:
            self.startpoint = [(1,9), (10,17)]
        else:
            self.startpoint = [(1,9), (10,18), (10,1)]
        self.basepoint = (29,9)

mapvar = Map()

class Path():
    def __init__(self):
        if mapvar.pointmovelist is not None:
            self.movelist = mapvar.pointmovelists[0][:]
        self.border_walls = gen_border_walls()
        self.wall_list = list(self.border_walls)

    def get_wall_list(self):
        '''Combines border walls and walls from towers placed on the map'''
        self.wall_list = list(self.border_walls)
        for tower in Localdefs.towerlist:
            for wall in tower.towerwalls:
                self.wall_list.append(wall)
        #print self.wall_list
        return self.wall_list

    # def is_open_path(self):
    #     '''Determines if path is set or fluid'''
    #     # f = open(os.path.join('mapfiles', str(mapvar.current), 'movefile.txt'))
    #     # lines = f.readlines()
    #     # if lines[2] != "IGNORE":
    #     #     self.is_open = False
    #     #     return False
    #     # else:
    #     self.is_open = True
    #     return True


path = Path()
newPath = Pathfinding.GridWithWeights(mapvar.squwid, mapvar.squhei, mapvar.squborder, (29, 9))
flyPath = Pathfinding.GridWithWeights(mapvar.squwid, mapvar.squhei, mapvar.squborder, (29, 9))