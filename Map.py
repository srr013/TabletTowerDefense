import Utilities
import localdefs
import pathfinding
import os
import Playfield

from kivy.uix.image import Image
from kivy.graphics import *

winwid = 1020 #window width
winhei = 600
scrwid = winwid #Playable screen width.
scrhei = winhei #Playable screen height.
squsize = 30
mapoffset = (0,0) #offset of the playing field(including walls) in tiles
border = 60
squborder = border/squsize
waveseconds = 20.5
squwid = int(scrwid/squsize + mapoffset[0])+squborder*2 #playable field is 33 squ wide (including border)
squhei = int(scrhei/squsize + mapoffset[1])+squborder #playable field is 24 squ high


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
        y = mapoffset[1]+1
        walls.append((x, y))
        y = squhei-1
        walls.append((x, y))
        x += 1
    y = mapoffset[1]
    while y <= squhei:
        x=mapoffset[0]
        walls.append((x,y))
        x = squwid-1
        walls.append((x,y))
        x = mapoffset[0]+1
        walls.append((x, y))
        x = squwid
        walls.append((x, y))
        y += 1
    for wall in walls:
        rect = Utilities.createRect(wall[0],wall[1], squsize, squsize)
        wallrectlist.append(rect)
    return walls

class Map():
    def __init__(self):
        self.current = "Pathfinding"
        self.pathrectlist = None
        self.pointmovelist = None
        self.endrect = None
        self.mapdict = dict()
        self.pointmovelists = list()
        self.pathrectlists = list()
        self.dirmovelists = list()
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
        self.dirmovelists = []

        for movelist in self.movelists:
            ##translate tiles to pixels. SQU represents a tile width or height
            pointlist = list([(point[0]*squsize,point[1]*squsize) for point in movelist[0]])
            #change movelist[0] to [2] for enemies to move along abbreviated list. Issues with enemy pathing when path changes if so.
            enemymovelist = list([(point[0]*squsize,point[1]*squsize) for point in movelist[0]])
            dirmovelist = movelist[1]
            ##create a rect for each set of points to connect the path from one point to another
            pathrectlist = list([Utilities.createRect(pointlist[ind],(pointlist[ind+1][0]-pointlist[ind][0],pointlist[ind+1][1]-pointlist[ind][1])) for ind in range(len(pointlist)-2)])
            self.pointmovelists.append(enemymovelist)
            self.pathrectlists.append(pathrectlist)
            self.dirmovelists.append(dirmovelist)

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
        self.backgroundimg = Image()
        self.background = Playfield.playField()
        self.backgroundimg.size = self.background.size
        self.backgroundimg.pos = self.background.pos
        with self.backgroundimg.canvas:
            Color(.05,.05,.05,.05)
            Rectangle(size=self.backgroundimg.size, pos=self.backgroundimg.pos)
            Color(0,0,0,.6)
            Line(points=[squsize*squborder,squsize*squborder, squsize*squborder,scrhei-squsize*squborder, scrwid-squsize*squborder,
            scrhei-squsize*squborder,scrwid-squsize*squborder,squsize*squborder, squsize*squborder,squsize*squborder], width=1)

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

    def roadGen(self):
        self.roadcontainer.clear_widgets()
        '''Generate the path and base and blit them'''
        #2 movelists are passed in currently. Only print tiles for the first, the ground move list. The flying move list should be the last list.
        for pathnum in range(1 if len(self.movelists)==1 else len(self.movelists)-1):

            for square in self.pathrectlists[pathnum]:
                image = Utilities.imgLoad(source=os.path.join('backgroundimgs','roadarrow.png'), pos=(square[0],square[1]))
                if image.pos == [30,270] or image.pos == [60,270]:
                    image.source = os.path.join('backgroundimgs','redroadarrow.png')
                image.size = (30,30)
                self.roadcontainer.add_widget(image)
            x=-1
            for square in self.roadcontainer.walk(restrict=True):
                angle = 0
                if self.dirmovelists[0][x] == 'u':
                    angle = 90
                if self.dirmovelists[0][x] == 'l':
                    angle = 180
                if self.dirmovelists[0][x] == 'd':
                    angle = 270
                if angle != 0:
                    with square.canvas.before:
                        PushMatrix()
                        Rotate(axis=(0, 0, 1), origin=square.center, angle=angle)
                    with square.canvas.after:
                        PopMatrix()
                x+=1

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
newPath = pathfinding.GridWithWeights(squwid, squhei, squborder,(29,9))
flyPath = pathfinding.GridWithWeights(squwid, squhei, squborder,(29,9))