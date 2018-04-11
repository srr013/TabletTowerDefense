import os
from kivy.animation import Animation
from kivy.graphics import *

import EventFunctions
import GUI
import Localdefs
import Map
import Pathfinding
import Player
import TowerAbilities
import Towers
import main


def makeIcons():
    '''Creates an Icon from the class for each tower'''
    for tower in Towers.baseTowerList:
        Towers.Icon(tower)

def makeUpgradeIcons():
    for ability in TowerAbilities.baseAbilityList:
        TowerAbilities.TowerAbility(ability)

def tickAndClear(clock, background):
    '''Updates the game time and blits the background
    Clock: pygame.time.Clock instance
    background: the game's background image'''
    clock.tick(30)
    # Player.player.screen.blit(background,(0,0))

def workSenders(*args):
    '''Determines what enemys to create and where to place them.
    Frametime: the amount of time elapsed per frame'''
    for sender in Localdefs.senderlist:
        sender.tick()

def workTowers():
    '''Towers target enemy(s) and create Shot instances
    Frametime: the amount of time elapsed per frame'''
    for tower in Localdefs.towerlist:
        if tower.totalUpgradeTime > 0:
            tower.targetTimer = tower.reload
            tower.upgradeTimeElapsed += Player.player.frametime
            tower.updateUpgradeStatusBar()
        elif tower.type in ['Life', 'Fire']:
            tower.takeTurn()
    for type in Localdefs.towerGroupDict.values():
        if type:
            for group in type:
                if group.needsUpdate:
                    group.updateTowerGroup()
                if group.towerSet == set():
                    group.removeTowerGroup()
                elif group.towerType in ['Wind', 'Ice', 'Gravity']:
                    group.takeTurn()

def buildNodeDicts():
    Map.myGrid.walls = Map.path.border_walls
    Map.flyPath.walls = Map.path.border_walls
    Map.myGrid.genNodeDict()
    Map.flyPath.genNodeDict()

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
    # Map.newPath.walls = Map.path.get_wall_list()
    Map.myGrid.walls = Map.path.get_wall_list()
    if len(Map.mapvar.flymovelists) == 0:
         updateFlyingList()

    Map.mapvar.movelists = []
    x=0
    for startpoint in Map.mapvar.startpoint:
        came_from, cost_so_far = Pathfinding.get_path(Map.myGrid, startpoint, Map.mapvar.basepoint)
        if came_from == 'Path Blocked':
            Map.mapvar.blockedSquare = cost_so_far
            return False
        Map.mapvar.movelists.append(Pathfinding.reconstruct_path(came_from, startpoint, Map.mapvar.basepoint))

    Map.mapvar.genmovelists()
    Map.mapvar.updatePath = False
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
    if not GUI.gui.bgrect:
        with Map.mapvar.backgroundimg.canvas.after:
            if color == 'red':
                x = float(1.0 - (Player.player.health / 20.0))
                Color(1, 0, 0, x)
            else:
                Color(0, 0, 0, .5)
            GUI.gui.bgrect = Rectangle(size=(Map.mapvar.scrwid, Map.mapvar.scrhei), pos=(0, 0))

        Map.mapvar.dispFlashCounter = 0
        Map.mapvar.dispFlashLimit = numframes


def workDisp():
    if GUI.gui.bgrect:
        Map.mapvar.dispFlashCounter += 1
        if Map.mapvar.dispFlashCounter >= Map.mapvar.dispFlashLimit:
            Map.mapvar.backgroundimg.canvas.after.remove(GUI.gui.bgrect)
            GUI.gui.bgrect = None
            Map.mapvar.dispFlashCounter = 0
    dispMessage()
    if GUI.gui.messageCounter > 0:
        GUI.gui.messageCounter += 1
        if GUI.gui.messageCounter >= 20:
            GUI.gui.removeMessage()


def workEnemies():
    '''Move, draw to screen, draw health bars of enemys.
    Frametime: the amount of time elapsed per frame'''
    for enemy in Map.mapvar.enemycontainer.children:
        #enemy.distBase = enemy.distToBase()
        if Player.player.newMoveList:
            if enemy.isair:
                enemy.movelist = Map.mapvar.pointflymovelists[enemy.movelistNum]
            else:
                enemy.movelist = Map.mapvar.pointmovelists[enemy.movelistNum]
        enemy.takeTurn()

    Player.player.newMoveList = False


def updateGUI():
    if Player.player.layout:
        for button in Player.player.layout.children:
                if button.disabled == True and button.group == 'Enableable':
                    if button.instance.cost <= Player.player.money:
                        button.disabled = False


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
        if enemy.anim:
            enemy.anim.cancel_all(enemy)
        if enemy.pushAnimation:
            enemy.pushAnimation.cancel_all(enemy)
    for shot in Map.mapvar.shotcontainer.children:
        shot.anim.cancel(shot)
    for tower in Map.mapvar.towercontainer.children:
        if tower.type == 'Gravity' and tower.animation:
            tower.towerGroup.disable()
        if tower.type == 'Wind':
            tower.turret.source = os.path.join('towerimgs', 'Wind', 'turret.png')
    GUI.gui.waveAnimation.cancel_all(GUI.gui.waveScroller)
    if GUI.gui.catchUpWaveAnimation:
        GUI.gui.catchUpWaveAnimation.cancel_all(GUI.gui.waveScroller)


def startAllAnimation():
    for enemy in Map.mapvar.enemycontainer.children:
        enemy.anim.start(enemy)
    for shot in Map.mapvar.shotcontainer.children:
        shot.anim.start(shot)
    for tower in Map.mapvar.towercontainer.children:
        if tower.type == 'Wind' and tower.towerGroup.active:
            tower.turret.source = os.path.join('towerimgs', 'Wind', 'turret.gif')
    scroll = .25 - GUI.gui.waveScroller.scroll_x
    GUI.gui.catchUpWaveAnimation = Animation(scroll_x=scroll, duration=Player.player.wavetimeInt)
    GUI.gui.catchUpWaveAnimation.bind(on_complete=EventFunctions.updateAnim)
    GUI.gui.catchUpWaveAnimation.start(GUI.gui.waveScroller)


def resetGame():
    '''Resets game variables so player can restart the game quickly.'''
    Map.mapvar.getStartPoints()
    Map.mapvar.flylistgenerated = False
    Map.mapvar.flymovelists = []
    Map.mapvar.pointmovelist = []
    Localdefs.towerGroupDict = {'Life': [], 'Fire': [], 'Ice': [], 'Gravity': [], 'Wind': []}
    AllLists = [Localdefs.towerlist, Localdefs.bulletlist, Localdefs.menulist, Localdefs.explosions,
                Localdefs.senderlist, Localdefs.timerlist, Localdefs.shotlist, Localdefs.alertQueue]
    i = 0
    for list in AllLists:
        while i < len(list):
            list.pop()
    for tower in Map.mapvar.towercontainer.children:
        tower.remove()
    Map.mapvar.towercontainer.clear_widgets()
    for enemy in Map.mapvar.enemycontainer.children:
        enemy.anim.cancel(enemy)
        if enemy.pushAnimation:
            enemy.pushAnimation.cancel(enemy)
    Map.mapvar.enemycontainer.clear_widgets()
    for road in Map.mapvar.roadcontainer.children:
        road.iceNeighbor = False
    Map.mapvar.roadcontainer.clear_widgets()
    Map.mapvar.shotcontainer.clear_widgets()
    Map.mapvar.wallcontainer.clear_widgets()
    Map.mapvar.towerdragimagecontainer.clear_widgets()
    # Map.flyPath = Pathfinding.neighborGridwithWeights(Map.mapvar.squwid, Map.mapvar.squhei - 1, 0, (28, 9))
    # Map.myGrid = Pathfinding.neighborGridwithWeights(Map.mapvar.squwid, Map.mapvar.squhei - 1, 0, (28, 9))
    # buildNodeDicts()
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
    GUI.gui.removeWaveStreamer()
    if GUI.gui.bgrect:
        Map.mapvar.backgroundimg.canvas.after.remove(GUI.gui.bgrect)
        GUI.gui.bgrect = None
    GUI.gui.addAlert("New Game - Play Again", 'repeat')

