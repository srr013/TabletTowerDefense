import Localdefs, Map, Towers, Pathfinding
import time
import Player
import GUI
import TowerAbilities
import EventFunctions
import os

from kivy.uix.label import Label
from kivy.graphics import *
from kivy.animation import Animation

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
    for sender in Localdefs.senderlist:
        sender.tick()

def workTowers():
    '''Towers target enemy(s) and create Shot instances
    Frametime: the amount of time elapsed per frame'''
    for tower in Localdefs.towerlist:
        tower.takeTurn()
    for type in Localdefs.towerGroupDict.values():
        if type:
            for group in type:
                if group.towerSet == set():
                    group.removeTowerGroup()
                else:
                    group.takeTurn()

def updateFlyingList():
    '''Update movelist for flying enemies'''
    # only border walls for flying list. Flying list to be index 1.
    Map.flyPath.walls = Map.path.border_walls
    Map.flyPath.weights = {}
    for startpoint in Map.mapvar.startpoint:
        came_from, cost_so_far = Pathfinding.get_path(Map.flyPath, startpoint, Map.mapvar.basepoint)
        Map.mapvar.flymovelists.append(Pathfinding.reconstruct_path(came_from, startpoint, Map.mapvar.basepoint))

def updatePath():
    '''Update the path using A* algorithm'''
    Map.newPath.walls = Map.path.get_wall_list()
    #print "walls", Map.newPath.walls
    if len(Map.mapvar.flymovelists) == 0:
        updateFlyingList()

    Map.mapvar.movelists = list()
    x=0
    for startpoint in Map.mapvar.startpoint:
        came_from, cost_so_far = Pathfinding.get_path(Map.newPath, startpoint, Map.mapvar.basepoint)
        if came_from == 'Path Blocked':
            Map.mapvar.blockedSquare = cost_so_far
            return False
        Map.mapvar.movelists.append(Pathfinding.reconstruct_path(came_from, startpoint, Map.mapvar.basepoint))
        # if Map.mapvar.movelists[x][0] == "Path Blocked":
        #     Map.mapvar.blockedSquare = Map.mapvar.movelists[x][1]
        #     return False
        # x+=1

    Map.mapvar.genmovelists()
    Map.mapvar.updatePath = False
    Player.player.newMoveList = True
    Map.mapvar.roadGen()
    updateIce()

def updateIce():
    for group in Localdefs.towerGroupDict['Ice']:
        group.getAdjacentRoads()


def workShots():
    '''Update the shot location and hit the enemy'''
    for shot in Localdefs.shotlist:
        shot.takeTurn()

def dispMessage(*args):
    '''Display any alerts in the queue, then remove them'''
    if GUI.gui.alertQueue and not GUI.gui.alertAnimation.have_properties_to_animate(GUI.gui.alertScroller):
        GUI.gui.alertLabel.text = GUI.gui.alertQueue[0][0]
        GUI.gui.alertAnimation.start(GUI.gui.alertScroller)

def flashScreen(color, numframes):
    with Map.mapvar.backgroundimg.canvas.after:
        if color == 'red':
            Color(1,0,0,.5)
        else:
            Color(0,0,0,.5)
        GUI.gui.bgrect = Rectangle(size=(Map.mapvar.scrwid, Map.mapvar.scrhei), pos=(0, 0))

    Map.mapvar.dispFlashCounter = 0
    Map.mapvar.dispFlashLimit = numframes

def workDisp():
    if GUI.gui.bgrect:
        Map.mapvar.dispFlashCounter +=1
        if Map.mapvar.dispFlashCounter >= Map.mapvar.dispFlashLimit:
            print "removing bgrect from flash"
            Map.mapvar.backgroundimg.canvas.after.remove(GUI.gui.bgrect)
            GUI.gui.bgrect = None
            Map.mapvar.dispFlashCounter = 0
    dispMessage()

#
# def dispExplosions():
#     for explosion in Localdefs.explosions:
#         print explosion
#         explosion[2].dispExplosions(explosion)


def workEnemies():
    '''Move, draw to screen, draw health bars of enemys.
    Frametime: the amount of time elapsed per frame'''
    for enemy in Map.mapvar.enemycontainer.children:
        enemy.distBase = enemy.distToBase()
        if Player.player.newMoveList:
            if enemy.isair:
                enemy.movelist = Map.mapvar.pointflymovelists[enemy.movelistNum]
            else:
                enemy.movelist = Map.mapvar.pointmovelists[enemy.movelistNum]
        enemy.takeTurn()

    Player.player.newMoveList = False

def updateGUI(wavetime):
    GUI.gui.updateTopBar(wavetime)



# def towerButtonPressed(selected):
#     '''receives a Button object from GUI_Kivy
#     Display the tower and a circle for tower range if a button is pressed'''
#
#     mouseat = Map.mapvar.background.touch_pos
#     if eval("Towers."+selected.type+"Tower").basecost*(1-Player.player.modDict[selected.type.lower()+"CostMod"])*(1-Player.player.modDict["towerCostMod"]) > Player.player.money:
#         addAlert("Not Enough Money", 48, "center", (240, 0, 0))
#         Player.player.towerSelected = None
#         selected = None
#         return selected
#
#     selected.img.pos = mouseat
#     Map.mapvar.background.add_widget(selected.img)

def pauseGame(*args):
    id = args[0].id
    if Player.player.state == 'Playing':
        if id == 'pause':
            Player.player.state = 'Paused'
        if id == 'menu':
            Player.player.state = 'Menu'
    elif Player.player.state == 'Paused':
        Player.player.state = 'Playing'

def stopAllAnimation():
    for enemy in Map.mapvar.enemycontainer.children:
        enemy.anim.cancel(enemy)
        if enemy.pushAnimation:
            enemy.pushAnimation.cancel(enemy)
    for shot in Map.mapvar.shotcontainer.children:
        shot.anim.cancel(shot)
    for tower in Map.mapvar.towercontainer.children:
        if tower.type == 'Gravity' and tower.animation:
                tower.towerGroup.disable()
        if tower.type == 'Wind':
            tower.turret.source = os.path.join('towerimgs','Wind','turret.png')
    GUI.gui.waveAnimation.cancel(GUI.gui.waveScroller)
    if GUI.gui.catchUpWaveAnimation:
        GUI.gui.catchUpWaveAnimation.cancel(GUI.gui.waveScroller)

def startAllAnimation():
    for enemy in Map.mapvar.enemycontainer.children:
        enemy.anim.start(enemy)
    for shot in Map.mapvar.shotcontainer.children:
        shot.anim.start(shot)
    for tower in Map.mapvar.towercontainer.children:
        if tower.type == 'Wind' and tower.towerGroup.active:
            tower.turret.source = os.path.join('towerimgs','Wind','turret.gif')
    scroll = .25 - GUI.gui.waveScroller.scroll_x
    GUI.gui.catchUpWaveAnimation = Animation(scroll_x=scroll, duration=Player.player.wavetimeInt)
    GUI.gui.catchUpWaveAnimation.bind(on_complete=EventFunctions.updateAnim)
    GUI.gui.catchUpWaveAnimation.start(GUI.gui.waveScroller)

def resetGame():
    '''Resets game variables so player can restart the game quickly.'''
    Map.mapvar.getStartPoints()
    Map.mapvar.flylistgenerated = False
    Map.mapvar.flymovelists = []
    AllLists = [Localdefs.towerlist, Localdefs.bulletlist, Localdefs.menulist, Localdefs.explosions, Localdefs.senderlist, Localdefs.timerlist, Localdefs.shotlist, Localdefs.alertQueue]

    i=0
    for list in AllLists:
        while i < len(list):
            list.pop()

    for tower in Map.mapvar.towercontainer.children:
        tower = 0
    Map.mapvar.towercontainer.clear_widgets()

    for enemy in Map.mapvar.enemycontainer.children:
        enemy.anim.cancel(enemy)
        if enemy.pushAnimation:
            enemy.pushAnimation.cancel(enemy)
        enemy = 0
    Map.mapvar.enemycontainer.clear_widgets()

    for road in Map.mapvar.roadcontainer.children:
        road.iceNeighbor = False
        road = 0
    Map.mapvar.roadcontainer.clear_widgets()

    Map.mapvar.shotcontainer.clear_widgets()
    Map.mapvar.wallcontainer.clear_widgets()
    Map.mapvar.towerdragimagecontainer.clear_widgets()

    Player.player.wavenum = 0
    GUI.gui.myDispatcher.WaveNum = GUI.gui.myDispatcher.Wave = str(Player.player.wavenum)
    Player.player.wavetime = int(Map.mapvar.waveseconds)
    GUI.gui.myDispatcher.Timer = str(Player.player.wavetime)
    Player.player.money = Player.playermoney
    GUI.gui.myDispatcher.Money = str(Player.player.money)
    Player.player.health = Player.playerhealth
    GUI.gui.myDispatcher.Health = str(Player.player.health)
    Player.player.score = 0
    GUI.gui.myDispatcher.Score = str(Player.player.score)
    GUI.gui.resetWaveStreamer()

    GUI.gui.menuButton.disabled = False
    GUI.gui.pauseButton.disabled = False
    GUI.gui.nextwaveButton.disabled = False
    GUI.gui.enemyInfoButton.disabled = False

    updatePath()
    GUI.gui.addAlert("New Game", 'repeat')