from localdefs import *
from localclasses import *
import pygame
from pygame.locals import *
import EventFunctions
import sys
import time
from GUI import *

black = (0,0,0)
white = (255,255,255)
red = (255,0,0)

def makeIcons():
    for tower in localclasses.baseTowerList:
        localclasses.Icon(tower)

def tickAndClear(clock,background):
    clock.tick(30)
    player.screen.blit(background,(0,0))

def workSenders(frametime):
    for sender in senderlist:
        sender.tick(frametime)

def workTowers(frametime):
    for tower in towerlist:
        tower.takeTurn(frametime,player.screen)

def updateFlyingList():
    # only border walls for flying list. Flying list to be index 1.
    newPath.walls = path.border_walls
    newPath.weights = {}
    came_from, cost_so_far = pathfinding.get_path(newPath, mapvar.startpoint, mapvar.basepoint)
    mapvar.movelists.append(pathfinding.reconstruct_path(came_from, mapvar.startpoint, mapvar.basepoint))
    mapvar.genmovelists()

##mywork
def updatePath(openPath):
    if openPath == True:
        newPath.walls = path.get_wall_list()
        came_from, cost_so_far = pathfinding.get_path(newPath, mapvar.startpoint, mapvar.basepoint)
        if len(mapvar.movelists) == 0:
            mapvar.movelists.append(pathfinding.reconstruct_path(came_from, mapvar.startpoint, mapvar.basepoint))
        else:
            mapvar.movelists[0] = (pathfinding.reconstruct_path(came_from, mapvar.startpoint, mapvar.basepoint))
        if mapvar.movelists[0] == "Path Blocked":
            i = 0
            while i < len(towerlist[-1].towerwalls):
                path.wall_list.pop(-1)
                i +=1

            tower = towerlist.pop(-1)
            player.money += tower.cost
            addAlert("Path Blocked", 48, "center", (240, 0, 0))
            newPath.walls = path.get_wall_list()
            came_from, cost_so_far = pathfinding.get_path(newPath, mapvar.startpoint, mapvar.basepoint)
            mapvar.movelists[0] = (pathfinding.reconstruct_path(came_from, mapvar.startpoint, mapvar.basepoint))
            mapvar.genmovelists()
            return mapvar.backgroundGen()

        if len(mapvar.movelists) < 2:
            updateFlyingList()
        mapvar.genmovelists()
        mapvar.updatePath = False

        return mapvar.backgroundGen()


##my work
def workShots():
    for shot in shotlist:
        shot.takeTurn(player.screen)
        player.screen.blit(shot.image, shot.rect)

def dispExplosions():
    #Display any explosions in the queue, then remove them.
    for rect in explosions:
        player.screen.blit(imgLoad('explosion.png'),rect)
        explosions.remove(rect)

def dispText():
    for alert in alertQueue:
        if alert[2] <= time.time():
            alertQueue.pop(0)
        else:
            player.screen.blit(alert[0], alert[1])

def addAlert(message, fontsize, location, color, length = 2):
    if location == "center":
        location = (winwid/2, winhei/2)

    font = pygame.font.Font(None, fontsize)
    text = font.render(message, 1, color)
    textpos = text.get_rect(center=location)
    endtime = time.time() + length
    alertQueue.append([text,textpos, endtime])


def workEnemies(frametime):
    #Let the enemies do their thing. Move, draw to screen, draw health bars.
    for enemy in enemylist:
        enemy.distBase = enemy.distToBase()
        enemy.takeTurn(frametime)
        player.screen.blit(enemy.image,enemy.rect)
        pygame.draw.line(player.screen, (0,0,0), (enemy.rect.left,enemy.rect.top-2), (enemy.rect.right,enemy.rect.top-2), 3)
        if enemy.poisontimer:
            pygame.draw.line(player.screen, (0,255,0), (enemy.rect.left,enemy.rect.top-2), (enemy.rect.left+(enemy.health*1.0/enemy.starthealth*1.0)*enemy.rect.width,enemy.rect.top-2), 3)
        else:
            pygame.draw.line(player.screen, (255,0,0), (enemy.rect.left,enemy.rect.top-2), (enemy.rect.left+(enemy.health*1.0/enemy.starthealth*1.0)*enemy.rect.width,enemy.rect.top-2), 3)

def dispStructures():
    for struct in (towerlist):
        player.screen.blit(struct.image,struct.rect)

def selectedIcon(selected):
    mouseat = roundRect(selected.img.get_rect(center=pygame.mouse.get_pos()))
    if eval("localclasses."+selected.type+"Tower").basecost*(1-localdefs.player.modDict[selected.type.lower()+"CostMod"])*(1-localdefs.player.modDict["towerCostMod"]) > player.money:
        addAlert("Not Enough Money", 48, "center", (240, 0, 0))
        player.towerSelected = None
        selected = None
        return selected
    player.screen.blit(selected.img,mouseat)
    if selected.base == "Tower":
        rn = int(eval("localclasses."+selected.type+"Tower").baserange*(1+player.modDict['towerRangeMod'])*(1+player.modDict[selected.type.lower()+'RangeMod']))
        area = pygame.Surface((2*rn,2*rn),SRCALPHA)
        pygame.draw.circle(area, (255, 255, 255, 75), (rn, rn), rn, 0)
        player.screen.blit(area,mouseat.move((-1*rn,-1*rn)).center)
        return selected

def selectedTower(selected):
    player.towerSelected = selected
    gui.showTowerButtons(selected)

    #selected.genButtons(screen)
    """for img,rect,info,infopos,cb in selected.buttonlist:
        screen.blit(img,rect)
        if rect.collidepoint(mousepos):
            screen.blit(info,infopos)
    def r():
        rn = int(selected.range)
        area = pygame.Surface((2*rn,2*rn),SRCALPHA)
        pygame.draw.circle(area,(255,255,255,85),(rn,rn),rn,0)
        screen.blit(area,selected.rect.move((-1*rn,-1*rn)).center)
    def s():
        st = 65
        area = pygame.Surface((2*st,2*st),SRCALPHA)
        pygame.draw.circle(area,(0,0,0,85),(st,st),st,0)
        screen.blit(area,selected.rect.move((-1*st,-1*st)).center)
    if selected.range<65:
        s()
        r()
    else:
        r()
        s()"""


#def dispIcons(screen,mousepos,font):
#    for icon in iconlist:
#        screen.blit(icon.img,icon.rect)
#        if icon.rect.collidepoint(mousepos):
#            text = font.render("%s Tower (%d)" % (icon.type,eval(icon.type+"Tower").basecost*(1-player.modDict[icon.type.lower()+"CostMod"])*(1-player.modDict["towerCostMod"])),1,(0,0,0))
#            textpos = text.get_rect(left=icon.rect.left,bottom=icon.rect.top-2)
#            screen.blit(text,textpos)

def roundPoint(point):
    x = squsize*(point[0]/squsize)
    y = squsize*(point[1]/squsize)
    return (x,y)

def roundRect(rect):
    new = rect.copy()
    new.topleft = roundPoint((rect.centerx,rect.centery))
    return new

##Called from towerdefense.py. Handles user input.
def workEvents(selected, wavestart, menu):
    for event in pygame.event.get():
        # Thorpy integration
        menu.react(event)

        #keyboard integration
        if event.type == QUIT:
            sys.exit()
        elif event.type == MOUSEBUTTONUP:
            selected,mBUb = EventFunctions.mouseButtonUp(event, selected)
            if selected == None and gui.popUp_displayed!=selected:
                GUI.hidePopUp(gui, selected)
        else:
            keyinput = pygame.key.get_pressed()
            if keyinput[K_ESCAPE]:
                sys.exit()
            elif event.type==KEYDOWN and event.dict['key']==K_n:
                player.next_wave = True
            elif keyinput[K_f]:
                player.screen = pygame.display.set_mode((scrwid,scrhei),FULLSCREEN)
            elif keyinput[K_w]:
                player.screen = pygame.display.set_mode((scrwid,scrhei))
            elif keyinput[K_s]:
                player.save()
            elif keyinput[K_UP]:
                if player.game_speed<10:
                    game_speed_update(1,True)
            elif keyinput[K_DOWN]:
                if player.game_speed>1:
                    game_speed_update(-1,True)

            #CAUTION - above "keyinput" is True if the input was hit no matter the event processed. This means it renders
            #true multiple times per frame. Use the below instead.
            elif event.type==KEYDOWN and event.dict['key']==K_SPACE:
                player.paused = True

    return selected,wavestart

def resetGame():
    AllLists = [localdefs.towerlist,localdefs.enemylist, localdefs.bulletlist,localdefs.iconlist,localdefs.menulist, localdefs.explosions, localdefs.senderlist, localdefs.timerlist, localdefs.shotlist, localdefs.alertQueue]

    i=0
    for list in AllLists:
        while i < len(list):
            list.pop()

    player.wavenum = 0

gui = GUI(player)

def getGUI(timer):
    gui.createTopBar(timer)
    gui.createBottomBar()
    gui.createRightPanel()

    for box in gui.boxes:
        box.blit()
        box.update()

    game_speed_reaction = thorpy.Reaction(reacts_to=thorpy.constants.THORPY_EVENT,
                                          reac_func=game_speed_update,
                                          event_args={"id": thorpy.constants.EVENT_SLIDE},
                                          params={},
                                          reac_name="updating game speed")
    gui.game_speed.add_reaction(game_speed_reaction)


    return gui.boxes

def updateMenu():
    return gui.boxes

def updateGUI(timer):
    gui.updateGui(timer)
    gui.updatePanel()

    for box in gui.boxes:
        box.blit()
        box.update()


def game_speed_update(change=0, keydown = False):
    if keydown == True:
        gui.game_speed.unblit_and_reblit_func(gui.game_speed.set_value, value=player.game_speed+change)
    localdefs.player.game_speed = gui.game_speed.get_value()
    print localdefs.player.game_speed

