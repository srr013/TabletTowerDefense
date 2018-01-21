import Utilities, localdefs, pathfinding
import os, sys
import pygame
import MainFunctions
import GUI_Kivy
import Player
import EventFunctions
import math
import Towers

from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.core.window import Window, WindowBase

from kivy.graphics import *

winwid = 1300 #window width
winhei = 830
scrwid = 1020 #Playable screen width.
scrhei = 760 #Playable screen height.
squsize = 30
mapoffset = (0,0) #offset of the playing field(including walls) in tiles
squwid = int(scrwid/squsize + mapoffset[0]) #playable field is 33 squ wide (including border)
squhei = int(scrhei/squsize + mapoffset[1]) #playable field is 24 squ high
border = 30
squborder = border/squsize

wallrectlist = list()
def gen_border_walls():
    '''generates a list of walls around the border of the map'''
    walls = []
    x = mapoffset[0]
    while x < squwid:
        y=mapoffset[1]
        walls.append((x,y))
        y = squhei
        walls.append((x,y))
        x += 1
    y = mapoffset[1]
    while y <= squhei:
        x=mapoffset[0]
        walls.append((x,y))
        x = squwid-1
        walls.append((x,y))
        y += 1
    for wall in walls:
        rect = Utilities.createRect(wall[0],wall[1], squsize, squsize)
        wallrectlist.append(rect)
    return walls

class playField(ScatterLayout):
    def __init__(self,**kwargs):
        super(playField,self).__init__(**kwargs)

        ##scatter properties to allow partial scaling and no rotation
        self.scale = 1
        self.scale_max = 1.5
        self.scale_min = 1
        self.do_rotation=False
        self.do_translation = False
        self.size = scrwid,scrhei
        self.pos = mapoffset[0]*30,mapoffset[1]*30
        self.do_collide_after_children = True

    def on_touch_down(self, touch):
        squarepos = Utilities.getPos(touch.pos)
        if not Player.player.tbbox:
            GUI_Kivy.builderMenu(squarepos)
            return True

        elif Player.player.tbbox and Player.player.tbbox.collide_point(*touch.pos):
            return super(playField, self).on_touch_down(touch)

        elif Player.player.tbbox and not Player.player.tbbox.collide_point(*touch.pos):
            mapvar.backgroundimg.remove_widget(Player.player.tbbox)
            Player.player.tbbox = None

        #returning this super argument allows the touch to propogate to children.
        return super(playField, self).on_touch_down(touch)


    def on_pressed(self, instance, pos):
        print('pressed at {pos}'.format(pos=pos))

class Map():
    def __init__(self):
        self.current = "Pathfinding"
        self.pathrectlist = None
        self.pointmovelist = None
        self.endrect = None
        self.mapdict = dict()
        self.pointmovelists = list()
        self.pathrectlists = list()
        self.wavesSinceLoss = 0
        self.total_waves = 0
        self.movelists = list()
        self.movelistnum = -1
        self.updatePath = True
        self.openPath = True

    def genmovelists(self):
        '''Generate the movement list for enemys and path blitting'''
        ##zero out the lists to start fresh. Otherwise the append allows multiple lists.
        self.pointmovelists = []
        self.pathrectlists = []
        for movelist in self.movelists:
            ##translate tiles to pixels. SQU represents a tile width or height
            pointmovelist = list([(point[0]*squsize,point[1]*squsize) for point in movelist])
            ##create a rect for each set of points to connect the path from one point to another
            pathrectlist = list([Utilities.createRect(pointmovelist[ind],(pointmovelist[ind+1][0]-pointmovelist[ind][0],pointmovelist[ind+1][1]-pointmovelist[ind][1])) for ind in range(len(pointmovelist)-2)])
            #for rec in pathrectlist:
                #if rec[2] < 0:
                #    rec[2] = abs(rec[2])
                #if rec[3] < 0:
                #    rec[3] = abs(rec[3])
            self.pointmovelists.append(pointmovelist)
            self.pathrectlists.append(pathrectlist)

    def getmovelist(self):
        '''Get the mvoe list from file if it is a pre-set path'''
        ##pulls data from movefile.txt for the appropriate level to create the map.
        f = open(os.path.join('mapfiles',str(self.current),'movefile.txt'))
        line = f.readline().strip().split(',')
        self.basepoint = (int(line[0])+mapoffset[0],int(line[1])+mapoffset[1])
        line = f.readline().strip().split(',')
        self.startpoint = (int(line[0])+mapoffset[0], int(line[1])+mapoffset[1])
        lines = f.readlines()
        f.close()


        ##hook for use of new pathinfinding vs set path. IGNORE should be second line in movefile.txt
        if lines[0] == "IGNORE":
            pass

        else:
            for line in lines:
                ##creates a list for each "path" indicated in the movefile. A negative value in x or y indicates a new path/list
                ##the values in the file are in "tiles". the number in the file represents # of tiles between the tile and origin
                line = line.strip().split(',')
                ##use set path
                if int(line[0])<0 or int(line[1])<0 or int(line[0])>(scrwid) or int(line[1])>(scrhei/squsize):
                    self.movelists.append(list())
                    self.movelistnum+=1
                self.movelists[self.movelistnum].append((int(line[0]),int(line[1])))
        self.genmovelists()


    def getmapproperties(self):
        '''Open file and create dict of wave data'''
        def mapPropertiesGen(self):
            self.total_waves = 0
            ##hardcoded to use on Pathfinding map for the time being
            ##Using the wave# as dict keys, create a dict for the level indicating what troops to send
            f = open(os.path.join('mapfiles',self.current,'mapproperties.txt'))
            for line in f.readlines():
                if line[0]!='*':
                    self.total_waves += 1
                    line = line.strip().split('=')
                    linepro = line[1].strip().split(',')
                    yield line[0],[float(each.strip()) for each in linepro]
        self.mapdict = dict(mapPropertiesGen(self))

    def backgroundInit(self):
        self.backgroundimg = Utilities.imgLoad(source=os.path.join('backgroundimgs','backgroundgrid1024x768.jpeg'))
        self.background = playField()
        self.backgroundimg.size = self.background.size
        self.backgroundimg.pos = self.background.pos
        self.background.add_widget(self.backgroundimg)

        self.towercontainer = Utilities.container()
        self.backgroundimg.add_widget(self.towercontainer)

        self.roadcontainer = Utilities.container()
        self.backgroundimg.add_widget(self.roadcontainer)

        self.enemycontainer = Utilities.container()
        self.backgroundimg.add_widget(self.enemycontainer)

        self.shotcontainer = Utilities.container()
        self.backgroundimg.add_widget(self.shotcontainer)

        self.explosioncontainer = Utilities.container()
        self.backgroundimg.add_widget(self.explosioncontainer)

        return self.background

    def roadGen(self):
        self.roadcontainer.clear_widgets()
        '''Generate the path and base and blit them'''
        #2 movelists are passed in currently. Only print tiles for the first, the ground move list. The flying move list should be the last list.
        for pathnum in range(1 if len(self.movelists)==1 else len(self.movelists)-1):
            for square in self.pathrectlists[pathnum]:
                image = Utilities.imgLoad(source=os.path.join('backgroundimgs','roadsquare.png'), pos=(square[0],square[1]))
                image.size = (30,30)
                #print ("roadpos:", image.pos)
                self.roadcontainer.add_widget(image)

        self.baseimg = Utilities.imgLoad(source=os.path.join('backgroundimgs', 'Base.png'))
        self.baseimg.size = (90,90)
        self.baseimg.pos = (self.basepoint[0] * squsize-(self.baseimg.size[0]/3), self.basepoint[1] * squsize-(self.baseimg.size[1]/3))
        self.backgroundimg.add_widget(self.baseimg)
        #Kivy hierarchy: background (scatter and float layouts)> backgroundimg (on float) > containers

        ##offsetting base and rect to make it seem like the mobs are going into the base at the end.
        #self.baserect = self.baseimg.get_rect(center=(self.basepoint[0]*squsize + 45,self.basepoint[1]*squsize + .5*90/squsize))
        #self.baseimg = pygame.transform.rotate(self.baseimg, -120)

    def loadMap(self,mapname):
        '''Load a particular map
        mapname: the name of the map selected
        This is a legacy function and not fully utilized'''
        #called by main. Uses functions to load the map and map properties
        self.current = mapname
        if os.path.exists(os.path.join('mapfiles',str(self.current))):
            self.getmovelist()
            self.getmapproperties()
            return self.backgroundInit()
        else:
            print ("You Won!!!")
            pygame.quit()
            sys.exit(1)

    def getPathProperties(self):
        #self.openPath = localclasses.path.is_open_path()
        self.updatePath = self.openPath

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
        for tower in localdefs.towerlist:
            for wall in tower.towerwalls:
                self.wall_list.append(wall)
        #print (self.wall_list)
        return self.wall_list

    def is_open_path(self):
        '''Determines if path is set or fluid'''
        f = open(os.path.join('mapfiles', str(mapvar.current), 'movefile.txt'))
        lines = f.readlines()
        if lines[2] != "IGNORE":
            self.is_open = False
            return False
        else:
            self.is_open = True
            return True


path = Path()
newPath = pathfinding.GridWithWeights(squwid, squhei, squborder)