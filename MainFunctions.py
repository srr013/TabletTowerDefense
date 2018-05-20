import os
import operator
from kivy.animation import Animation
from kivy.graphics import *

import EventFunctions
import Localdefs
import Map
import Pathfinding
import Player
import TowerAbilities
import TowerIcon
import Analytics
import __main__
import Messenger


def makeIcons():
    '''Creates an Icon from the class for each tower'''
    for tower in TowerIcon.baseTowerList:
        TowerIcon.Icon(tower)


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
            tower.updateUpgradeStatus()
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
        group.getAdjacentRoads()

def workShots():
    '''Update the shot location and hit the enemy'''
    for shot in Localdefs.shotlist:
        shot.takeTurn()

def dispMessage(*args):
    '''Display any alerts in the queue, then remove them'''
    if Messenger.messenger.alertQueue and not Messenger.messenger.alertAnimation.have_properties_to_animate(Messenger.messenger.alertScroller):
        Messenger.messenger.alertLabel.text = Messenger.messenger.alertQueue[0][0]
        Messenger.messenger.alertAnimation.start(Messenger.messenger.alertScroller)

def flashScreen(color, numframes):
    if not Messenger.messenger.bgrect:
        with Map.mapvar.background.canvas.after:
            if color == 'red':
                x = float(1.0 - (Player.player.health / 20.0))
                Color(1, 0, 0, x)
            else:
                Color(0, 0, 0, .5)
            Messenger.messenger.bgrect = Rectangle(size=(__main__.app.root.scrwid, __main__.app.root.scrhei), pos=(0, 0))
        Map.mapvar.dispFlashCounter = 0
        Map.mapvar.dispFlashLimit = numframes


def workDisp():
    if Messenger.messenger.bgrect:
        Map.mapvar.dispFlashCounter += 1
        if Map.mapvar.dispFlashCounter >= Map.mapvar.dispFlashLimit:
            Map.mapvar.background.canvas.after.remove(Messenger.messenger.bgrect)
            Messenger.messenger.bgrect = None
            Map.mapvar.dispFlashCounter = 0
    dispMessage()
    if Messenger.messenger.messageCounter > 0:
        Messenger.messenger.messageCounter += 1
        if Messenger.messenger.messageCounter >= 20:
            Messenger.messenger.removeMessage()


def workEnemies():
    '''Move, draw to screen, draw health bars of enemys.
    Frametime: the amount of time elapsed per frame'''
    for enemy in Map.mapvar.enemycontainer.children:
        if Player.player.newMoveList:
            if enemy.isair:
                enemy.movelist = Map.mapvar.enemyflymovelists[enemy.movelistNum]
            else:
                enemy.movelist = Map.mapvar.enemymovelists[enemy.movelistNum]
        for road in Localdefs.burnroadlist:
            if not enemy.isair and enemy.collide_widget(road):
                road.burnEnemy(enemy)
                if enemy.slowtime > 0:
                    enemy.slowtime = 0
                    enemy.workSlowTime()
        enemy.takeTurn()
    Player.player.sortedlist = sorted(Map.mapvar.enemycontainer.children, key=operator.attrgetter("priority"))
    Player.player.newMoveList = False


def updateGUI():
    if Player.player.tbbox:
        for button in Player.player.tbbox.enableList:
            if Player.player.towerSelected:
                if Player.player.towerSelected.totalUpgradeTime != 0:
                    return
            if isinstance(button.instance.cost,tuple):
                if button.instance.cost[0] <= Player.player.money and button.instance.cost[1] <= Player.player.gems:
                    button.disabled = False
                else:
                    button.disabled = True
            elif button.instance.cost <= Player.player.money:
                button.disabled = False
            else:
                button.disabled = True

def stopAllAnimation():
    for enemy in Map.mapvar.enemycontainer.children:
        if enemy.anim:
            enemy.anim.cancel_all(enemy)
        if enemy.pushAnimation:
            enemy.pushAnimation.cancel_all(enemy)
        if enemy.backToRoad:
            enemy.backToRoad.cancel_all(enemy)
    for shot in Map.mapvar.shotcontainer.children:
        if shot.anim:
            shot.anim.cancel(shot)
    for tower in Map.mapvar.towercontainer.children:
        if tower.type == 'Gravity' and tower.animation:
            tower.towerGroup.disable()
    __main__.ids.wavestreamer.waveAnimation.cancel_all(__main__.ids.wavescroller)


def startAllAnimation():
    for enemy in Map.mapvar.enemycontainer.children:
        enemy.getNearestRoad()
    for shot in Map.mapvar.shotcontainer.children:
        if shot.anim:
            shot.anim.start(shot)
    if Player.player.wavenum > 0:
        __main__.ids.wavestreamer.waveAnimation = Animation(scroll_x=.3, duration=Player.player.wavetimeInt)
        __main__.ids.wavestreamer.waveAnimation.bind(on_complete=EventFunctions.updateAnim)
        __main__.ids.wavestreamer.waveAnimation.start(__main__.ids.wavescroller)


def resetGame():
    '''Resets game variables so player can restart the game quickly.'''
    Player.player.state = 'Restart'
    stopAllAnimation()
    Player.player.gameover = False
    Map.mapvar.getStartPoints()
    Map.mapvar.flylistgenerated = False
    Map.mapvar.flymovelists = []
    Map.mapvar.pointmovelists = []
    Localdefs.towerGroupDict = {'Life': [], 'Fire': [], 'Ice': [], 'Gravity': [], 'Wind': []}
    AllLists = [Localdefs.towerlist, Localdefs.bulletlist, Localdefs.menulist, Localdefs.explosions,
                Localdefs.senderlist, Localdefs.timerlist, Localdefs.shotlist, Localdefs.alertQueue]
    i = 0
    for list in AllLists:
        while i < len(list):
            list.pop()
    for tower in Map.mapvar.towercontainer.children:
        if tower.type != 'Base':
            tower.remove()
    Map.mapvar.baseimg = None
    Map.mapvar.towercontainer.clear_widgets()
    Map.mapvar.enemycontainer.clear_widgets()
    for road in Map.mapvar.roadcontainer.children:
        road.iceNeighbor = False
    Map.mapvar.roadcontainer.clear_widgets()
    Map.mapvar.shotcontainer.clear_widgets()
    Map.mapvar.wallcontainer.clear_widgets()
    Map.mapvar.towerdragimagecontainer.clear_widgets()
    Player.player.wavenum = 0
    Player.player.wavetime = int(Map.mapvar.waveseconds)
    Player.player.myDispatcher.Timer = str(Player.player.wavetime)
    Player.player.health = Player.playerhealth
    Player.player.myDispatcher.Health = str(Player.player.health)
    Player.player.score = 0
    Player.player.myDispatcher.Score = str(Player.player.score)
    Player.player.analytics = Analytics.Analytics()
    __main__.ids.wavestreamer.removeWaveStreamer()
    __main__.ids.wavescroller.scroll_x = 0
    __main__.ids.play.text = 'Start'
    if Messenger.messenger.bgrect:
        Map.mapvar.background.canvas.after.remove(Messenger.messenger.bgrect)
        Messenger.messenger.bgrect = None

