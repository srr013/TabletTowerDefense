import localdefs, localclasses, Map, Towers, pathfinding, Utilities
import pygame
from pygame.locals import *
import time
import Player
import GUI_Kivy
import TowerAbilities

black = (0,0,0)
white = (255,255,255)
red = (255,0,0)

def makeIcons():
    '''Creates an Icon from the class for each tower'''
    for tower in Towers.baseTowerList:
        Towers.Icon(tower)

def makeUpgradeIcons():
    for ability in TowerAbilities.baseAbilityList:
        TowerAbilities.TowerAbility(ability)

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
        Player.player.newMoveList = True

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
    for enemy in Map.mapvar.enemycontainer.children:
        enemy.distBase = enemy.distToBase()
        if Player.player.newMoveList:
            enemy.movelist = Map.mapvar.pointmovelists[enemy.movelistNum]
        enemy.takeTurn()

    Player.player.newMoveList = False


            #(Player.player.screen, (0,0,0), (enemy.rect_x,enemy.rect_y-2), (enemy.rect_x+enemy.rect_w,enemy.rect_y-2), 3)
        #if enemy.poisontimer:
        #    pygame.draw.line(Player.player.screen, (0,255,0), (enemy.rect_x,enemy.rect_y-2), (enemy.rect_x+(enemy.health*1.0/enemy.starthealth*1.0)*enemy.rect_w,enemy.rect_y-2), 3)
        #else:
        #    pygame.draw.line(Player.player.screen, (255,0,0), (enemy.rect_x,enemy.rect_y-2), (enemy.rect_x+(enemy.health*1.0/enemy.starthealth*1.0)*enemy.rect_w,enemy.rect_y-2), 3)

def updateGUI(wavetime):
    GUI_Kivy.gui.updateTopBar(wavetime)



def towerButtonPressed(selected):
    '''receives a Button object from GUI_Kivy
    Display the tower and a circle for tower range if a button is pressed'''

    mouseat = Map.mapvar.background.touch_pos
    if eval("Towers."+selected.type+"Tower").basecost*(1-Player.player.modDict[selected.type.lower()+"CostMod"])*(1-Player.player.modDict["towerCostMod"]) > Player.player.money:
        addAlert("Not Enough Money", 48, "center", (240, 0, 0))
        Player.player.towerSelected = None
        selected = None
        return selected

    selected.img.pos = mouseat
    Map.mapvar.background.add_widget(selected.img)

def pauseGame(*args):
    id = args[0].id
    print (id)
    if Player.player.state == 'Playing':
        if id == 'pause':
            Player.player.state = 'Paused'
        if id == 'menu':
            Player.player.state = 'Menu'
    elif Player.player.state == 'Paused':
        Player.player.state = 'Playing'


def resetGame():
    '''Resets game variables so player can restart the game quickly.'''
    AllLists = [localdefs.towerlist, localdefs.bulletlist, localdefs.menulist, localdefs.explosions, localdefs.senderlist, localdefs.timerlist, localdefs.shotlist, localdefs.alertQueue]

    i=0
    for list in AllLists:
        while i < len(list):
            list.pop()

    Player.player.wavenum = 0
    Player.player.wavestart = 999
    Player.player.money = Player.playermoney
    Player.player.health = Player.playerhealth
    Player.player.kill_score = 0
    Player.player.bonus_score = 0

    Map.mapvar.towercontainer.clear_widgets()
    Map.mapvar.enemycontainer.clear_widgets()
    Map.mapvar.explosioncontainer.clear_widgets()
    Map.mapvar.roadcontainer.clear_widgets()
    Map.mapvar.towercontainer.clear_widgets()
