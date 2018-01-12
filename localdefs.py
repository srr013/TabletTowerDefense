import os.path
import math
import os
import sys
import pygame
import threading
import time
from sys import exit as sysexit
from pygame.locals import *
import pathfinding


winwid = 1300 #window width
winhei = 900
scrwid = 1020 #Playable screen width.
scrhei = 760 #Playable screen height.
squsize = 30
mapoffset = (1,2) #offset of the playing field(including walls) in tiles
squwid = scrwid/squsize + mapoffset[0] #playable field is 33 squ wide (including border)
squhei = scrhei/squsize + mapoffset[1] #playable field is 24 squ high
border = 30
squborder = border/squsize
playerhealth = 20
playermoney = 50

wallrectlist = list()
def gen_border_walls():
    walls = []
    x = mapoffset[0]-1
    while x < squwid:
        y=mapoffset[1]
        walls.append((x,y))
        y = squhei
        walls.append((x,y))
        x += 1
    y = mapoffset[1]-1
    while y <= squhei:
        x=mapoffset[0]
        walls.append((x,y))
        x = squwid-1
        walls.append((x,y))
        y += 1
    for wall in walls:
        image = pygame.Surface((border,border))
        rect = image.get_rect(left=wall[0]*squsize,top=wall[1]*squsize)
        wallrectlist.append(rect)
    return walls

class Path():
    def __init__(self):
        if mapvar.pointmovelist is not None:
            self.movelist = mapvar.pointmovelists[0][:]
        self.border_walls = gen_border_walls()
        self.wall_list = list(self.border_walls)

    def get_wall_list(self):
        self.wall_list = list(self.border_walls)
        for tower in towerlist:
            for wall in tower.towerwalls:
                self.wall_list.append(wall)
        return self.wall_list

    def is_open_path(self):
        global openPath
        f = open(os.path.join('mapfiles', str(mapvar.current), 'movefile.txt'))
        lines = f.readlines()
        if lines[2] != "IGNORE":
            self.is_open = False
            return False
        else:
            self.is_open = True
            return True

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
        ##zero out the lists to start fresh. Otherwise the append allows multiple lists.
        self.pointmovelists = []
        self.pathrectlists = []
        for movelist in self.movelists:
            ##translate tiles to pixels. SQU represents a tile width or height
            pointmovelist = list([(point[0]*squsize+int(squsize/2.0),point[1]*squsize+int(squsize/2.0)) for point in movelist])
            ##create a rect for each set of points to connect the path from one point to another
            pathrectlist = list([pygame.Rect(pointmovelist[ind],(pointmovelist[ind+1][0]-pointmovelist[ind][0],pointmovelist[ind+1][1]-pointmovelist[ind][1])) for ind in range(len(pointmovelist)-2)])
            for rec in pathrectlist:
                rec.normalize()
            self.pointmovelists.append(pointmovelist)
            self.pathrectlists.append(pathrectlist)
            print "Move List Generated"

    def getmovelist(self):
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
        print "Map Properties Created"

    def backgroundGen(self):
        dp = imgLoad(os.path.join('backgroundimgs','roadsquare.png'))
        ##blit background to screen then each path rect
        self.backgroundimg = imgLoad(os.path.join('backgroundimgs','backgroundgrid1024x768.jpeg'))
        self.background = pygame.Surface((winwid, winhei))
        self.background.fill((0, 0, 0))
        self.background.blit(self.backgroundimg, (mapoffset[0]*squsize, mapoffset[1]*squsize+10))
        #2 movelists are passed in currently. Only print tiles for the first, the ground move list. The flying move list should be the last list.
        for pathnum in range(1 if len(self.movelists)==1 else len(self.movelists)-1):
            pathrectlist = self.pathrectlists[pathnum]
            #pointmovelist = self.pointmovelists[pathnum]
            for rec in [pygame.Rect(x,y,squsize,squsize) for x in range(0,scrwid,squsize) for y in range(0,scrhei,squsize)]:
                collideindex = rec.collidelist(pathrectlist)
                if collideindex!=-1:
                    self.background.blit(dp,rec.move(0,0))
        self.baseimg = imgLoad(os.path.join('backgroundimgs','Base.png'))
        ##offsetting base and rect to make it seem like the mobs are going into the base at the end.
        self.baserect = self.baseimg.get_rect(center=(self.basepoint[0]*squsize + 45,self.basepoint[1]*squsize + .5*90/squsize))
        self.baseimg = pygame.transform.rotate(self.baseimg, -120)
        self.background.blit(mapvar.baseimg, mapvar.baserect)

        print "Background Generated"
        return self.background

    def loadMap(self,mapname):
        #called by main. Uses functions to load the map and map properties
        self.current = mapname
        if os.path.exists(os.path.join('mapfiles',str(self.current))):
            self.getmovelist()
            self.getmapproperties()
            return self.backgroundGen()
        else:
            print "You Won!!!"
            pygame.quit()
            sysexit(1)

    def getPathProperties(self):
        self.openPath = path.is_open_path()
        self.updatePath = self.openPath

mapvar = Map()
path = Path()
newPath = pathfinding.GridWithWeights(squwid, squhei, squborder)

class Player():
    def __init__(self):
        self.name = "player"
        self.health = playerhealth
        self.money = playermoney
        self.abilities = list()
        self.wavenum = 0
        self.gameover = False
        self.towerSelected = None
        self.wavestart = 999
        self.next_wave = False
        self.game_speed = 3
        self.screen = None
        self.pausetime = 0
        self.paused = False
        self.restart = False
        self.kill_score = 0
        self.bonus_score = 0


        #Legacy code handling player access to towers and attributes.
        self.modDict = dict()
        self.modDict['towerCostMod'] = 0
        self.modDict['towerRangeMod'] = 0
        self.modDict['towerDamageMod'] = 0
        self.modDict['towerSpeedMod'] = 0

        self.modDict['fighterCostMod'] = 0
        self.modDict['fighterRangeMod'] = 0
        self.modDict['fighterDamageMod'] = 0
        self.modDict['fighterSpeedMod'] = 0

        self.modDict['archerCostMod'] = 0
        self.modDict['archerRangeMod'] = 0
        self.modDict['archerDamageMod'] = 0
        self.modDict['archerSpeedMod'] = 0

        self.modDict['mineCostMod'] = 0
        self.modDict['mineRangeMod'] = 0
        self.modDict['mineDamageMod'] = 0
        self.modDict['mineSpeedMod'] = 0

        self.modDict['slowCostMod'] = 0
        self.modDict['slowRangeMod'] = 0
        self.modDict['slowDamageMod'] = 0
        self.modDict['slowSpeedMod'] = 0

        self.modDict['antiairCostMod'] = 0
        self.modDict['antiairRangeMod'] = 0
        self.modDict['antiairDamageMod'] = 0
        self.modDict['antiairSpeedMod'] = 0

        self.modDict['towerAbilities'] = set()
        self.modDict['towerSellMod'] = 0
        self.modDict['towerAccess'] = list(('Fighter','Archer','Mine','Slow',"AntiAir"))

        self.modDict['towerAbilities'].add("Sell")
        self.modDict['towerAbilities'].add("AddFighter")
        self.modDict['towerAbilities'].add("RemoveFighter")
        self.modDict['towerAbilities'].add("ExtraDamage1")
        self.modDict['towerAbilities'].add("ExtendRange1")

    #Saves the game when the player dies. Should update.
    def die(self):
        self.gameover = True



player = Player()

enemylist = list()
towerlist = list()
bulletlist = list()
iconlist = list()
menulist = list()
explosions = list()
senderlist = list()
timerlist = list()
shotlist = list()
alertQueue = list()

def pauseGame():
    timepaused = time.time()
    totaltimepaused = 0

    font = pygame.font.Font(None, 48)
    text = font.render("Game Paused. Press Space to start.", 1, (255,0,0))
    textpos = text.get_rect(center=(scrwid / 2, scrhei / 2))

    while totaltimepaused == 0:
        player.screen.blit(text, textpos)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                keyinput = pygame.key.get_pressed()
                if keyinput[K_SPACE]:
                    totaltimepaused = time.time() - timepaused
                    player.paused = False
    player.pausetime =  totaltimepaused

def imgLoad(img):
    file = os.path.join(img)
    image = pygame.image.load(file)
    return image



##Use this if the sprite comes in a single PNG
def split_sheet(sheet, size, columns, rows):
    """
    Divide a loaded sprite sheet into subsurfaces.
    Sheet = the sheet to load
    Size = (w,h) of each frame
    Columns and rows are the number of cells horizontally and vertically.
    """
    subsurfaces = []
    for y in range(rows):
        row = []
        for x in range(columns):
            rect = pygame.Rect((x * size[0], y * size[1]), size)
            row.append(sheet.subsurface(rect))
        subsurfaces.append(row)
    return subsurfaces

def distance(first,second):
    return (math.sqrt((second.centerx-first.centerx)**2+(second.centery-first.centery)**2))

class SlowTimer():
    def __init__(self,percent,time):
        self.percent = percent
        self.time = time


#code not currently in use. Keeping as a source for enemy overhaul
#class PoisonTimer(threading.Thread):
#    def __init__(self,enemy,damage,seconds):
#        threading.Thread.__init__(self)
#        self.runtime = seconds
#        self.dam = damage
#        self.target = enemy
#        enemy.poisontimer=self
#        self.kill = False
#    def run(self):
#        sec = self.runtime*1.0
#        while(sec>0):
#            sec-=0.1
#            time.sleep(0.1)
#            if self.target.poisontimer == self or self.kill == True:
#                if self.target.health>0:
#                    self.target.health-=self.dam
#                    if self.target.health<=0:
#                        self.target.die()
#                        return
#                else:
#                    return
#            else:
#                return
#        if self.target.poisontimer == self:
#            self.target.poisontimer = None

#EnemyImageArray = list()
#def genEnemyImageArray():
#    for type in ["none","enemy","Speedy","Healthy","Armor"]:
#        ia = list()
#        try:enemyimage = imgLoad(os.path.join('enemyimgs',type+'.png'))
#        except:print "enemy image failed to load"
#        ia.append(enemyimage)
#        ia.append(pygame.transform.rotate(enemyimage,90))
#        ia.append(pygame.transform.flip(enemyimage,True,False))
#        ia.append(pygame.transform.rotate(enemyimage,-90))
#        EnemyImageArray.append(ia)
