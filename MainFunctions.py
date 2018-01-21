import localdefs, localclasses, Map, Towers, pathfinding, Utilities
import pygame
from pygame.locals import *
import EventFunctions
import sys, os
import time
import Player
import Enemy


black = (0,0,0)
white = (255,255,255)
red = (255,0,0)

def makeIcons():
    '''Creates an Icon from the class for each tower'''
    for tower in Towers.baseTowerList:
        Towers.Icon(tower)

def tickAndClear(clock,background):
    '''Updates the game time and blits the background
    Clock: pygame.time.Clock instance
    background: the game's background image'''
    clock.tick(30)
    #Player.player.screen.blit(background,(0,0))

def workSenders(*args):
    '''Determines what enemys to create and where to place them.
    Frametime: the amount of time elapsed per frame'''
    for sender in localdefs.senderlist:
        sender.tick()

def workTowers():
    '''Towers target enemy(s) and create Shot instances
    Frametime: the amount of time elapsed per frame'''
    for tower in localdefs.towerlist:
        tower.takeTurn()

def updateFlyingList():
    '''Update movelist for flying enemies'''
    # only border walls for flying list. Flying list to be index 1.
    Map.newPath.walls = Map.path.border_walls
    Map.newPath.weights = {}
    came_from, cost_so_far = pathfinding.get_path(Map.newPath, Map.mapvar.startpoint, Map.mapvar.basepoint)
    Map.mapvar.movelists.append(pathfinding.reconstruct_path(came_from, Map.mapvar.startpoint, Map.mapvar.basepoint))
    Map.mapvar.genmovelists()

##mywork
def updatePath(openPath):
    '''Update the path using A* algorithm
    openPath = Boolean indicating if path is set or fluid'''
    if openPath == True:
        Map.newPath.walls = Map.path.get_wall_list()
        came_from, cost_so_far = pathfinding.get_path(Map.newPath, Map.mapvar.startpoint, Map.mapvar.basepoint)
        if len(Map.mapvar.movelists) == 0:
            Map.mapvar.movelists.append(pathfinding.reconstruct_path(came_from, Map.mapvar.startpoint, Map.mapvar.basepoint))
        else:
            Map.mapvar.movelists[0] = (pathfinding.reconstruct_path(came_from, Map.mapvar.startpoint, Map.mapvar.basepoint))
        if Map.mapvar.movelists[0] == "Path Blocked":
            addAlert("Path Blocked", 48, "center", (240, 0, 0))
            return False

        if len(Map.mapvar.movelists) < 2:
            updateFlyingList()
        Map.mapvar.genmovelists()
        Map.mapvar.updatePath = False

        Map.mapvar.roadGen()


##my work
def workShots():
    '''Update the shot location and hit the enemy'''
    for shot in localdefs.shotlist:
        shot.takeTurn()
        #Player.player.screen.blit(shot.image, shot.rect)

def dispText():
    '''Display any alerts in the queue, then remove them'''
    for alert in localdefs.alertQueue:
        if alert[2] <= time.time():
            localdefs.alertQueue.pop(0)
        else:
            pass
            #Player.player.screen.blit(alert[0], alert[1])

def dispExplosions():
    for explosion in localdefs.explosions:
        explosion[2].dispExplosions(explosion)

def addAlert(message, fontsize, location, color, length = 2):
    '''Add an alert to alertQueue
    Message: the text to display
    Fontsize: integer size of font
    Location: string indicating location to display message. [center]
    length: Default 2. Length of time to display message in seconds.'''
    if location == "center":
        location = (Map.scrwid+Map.mapoffset[0]/2, Map.scrhei+Map.mapoffset[1]/2)

    font = pygame.font.Font(None, fontsize)
    text = font.render(message, 1, color)
    textpos = text.get_rect(center=location)
    endtime = time.time() + length
    localdefs.alertQueue.append([text,textpos, endtime])


def workEnemies():
    '''Move, draw to screen, draw health bars of enemys.
    Frametime: the amount of time elapsed per frame'''
    for enemy in localdefs.enemylist:
        enemy.distBase = enemy.distToBase()
        enemy.takeTurn()

    ##health bars not working w/out pygame
        #pygame.draw.line(Player.player.screen, (0,0,0), (enemy.rect_x,enemy.rect_y-2), (enemy.rect_x+enemy.rect_w,enemy.rect_y-2), 3)
        #if enemy.poisontimer:
        #    pygame.draw.line(Player.player.screen, (0,255,0), (enemy.rect_x,enemy.rect_y-2), (enemy.rect_x+(enemy.health*1.0/enemy.starthealth*1.0)*enemy.rect_w,enemy.rect_y-2), 3)
        #else:
        #    pygame.draw.line(Player.player.screen, (255,0,0), (enemy.rect_x,enemy.rect_y-2), (enemy.rect_x+(enemy.health*1.0/enemy.starthealth*1.0)*enemy.rect_w,enemy.rect_y-2), 3)

def dispStructures():
    '''Display all the towers in towerlist'''
    for struct in (localdefs.towerlist):
        pass
        #Player.player.screen.blit(struct.image,struct.rect)

def towerButtonPressed(selected):
    '''receives a Button object from GUI_Kivy
    Display the tower and a circle for tower range if a button is pressed'''

    mouseat = Map.mapvar.backgroundimg.touch_pos
    if eval("Towers."+selected.type+"Tower").basecost*(1-Player.player.modDict[selected.type.lower()+"CostMod"])*(1-Player.player.modDict["towerCostMod"]) > Player.player.money:
        addAlert("Not Enough Money", 48, "center", (240, 0, 0))
        Player.player.towerSelected = None
        selected = None
        return selected

    selected.img.pos = mouseat
    Map.mapvar.backgroundimg.add_widget(selected.img)

    if selected.base == "Tower":
        rn = int(eval("Towers."+selected.type+"Tower").baserange*(1+Player.player.modDict['towerRangeMod'])*(1+Player.player.modDict[selected.type.lower()+'RangeMod']))
        area = pygame.Surface((2*rn,2*rn),SRCALPHA)
        pygame.draw.circle(area, (255, 255, 255, 75), (rn, rn), rn, 0)
        Player.player.screen.blit(area,mouseat.move((-1*rn,-1*rn)).center)
        return selected

def selectedTower(selected):
    '''Displays the buttons for a tower if one is selected
    Selected: variable set in gameloop by MainFunctions.WorkEvents indicating the tower or icon selected by a mouse click'''
    Player.player.towerSelected = selected
    #gui.showTowerButtons(selected)


def resetGame():
    '''Resets game variables so player can restart the game quickly.'''
    AllLists = [localdefs.towerlist,localdefs.enemylist, localdefs.bulletlist,localdefs.iconlist,localdefs.menulist, localdefs.explosions, localdefs.senderlist, localdefs.timerlist, localdefs.shotlist, localdefs.alertQueue]

    i=0
    for list in AllLists:
        while i < len(list):
            list.pop()

    Player.player.wavenum = 0
    Map.mapvar.getPathProperties()
    Player.player.wavestart = 999
    Player.player.money = Player.playermoney
    Player.player.health = Player.playerhealth
    Player.player.kill_score = 0
    Player.player.bonus_score = 0
