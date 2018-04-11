import MainFunctions
from kivy.uix.widget import Widget

import GUI
import MainFunctions
import Map
import Player
import SenderClass
import Towers


def placeTowerFromList(*args):
    list = Map.mapvar.background.dragger.towerposlist
    instance = args[0]
    createdTowers = []
    for tower in list:
        createdTowers.append(placeTower(instance, tower))
    x = 0
    while MainFunctions.updatePath() == False:
        if x == 0:
            checkBlockedPath(createdTowers)
            x += 1
        else:
            for tower in createdTowers:
                tower.remove()
                GUI.gui.createMessage("Path Blocked")
                Player.player.money += tower.cost
                GUI.gui.myDispatcher.Money = str(Player.player.money)
    if createdTowers:
        resetEnemyPaths()


def resetEnemyPaths():
    for enemy in Map.mapvar.enemycontainer.children:
        if not enemy.isair:
            if enemy.anim:
                enemy.anim.cancel_all(enemy)
            try:
                enemy.movelist = Map.mapvar.pointmovelists[enemy.movelistNum]
                enemy.dirlist = Map.mapvar.dirmovelists[enemy.movelistNum]
                enemy.getNearestNode()
            except IndexError:
                print "Indexerror", enemy.movelist, enemy.movelistNum, enemy.curnode


def checkBlockedPath(createdTowers):
    right = (Map.mapvar.blockedSquare[0] + 1, Map.mapvar.blockedSquare[1])
    left = (Map.mapvar.blockedSquare[0] - 1, Map.mapvar.blockedSquare[1])
    up = (Map.mapvar.blockedSquare[0], Map.mapvar.blockedSquare[1] + 1)
    down = (Map.mapvar.blockedSquare[0], Map.mapvar.blockedSquare[1] - 1)
    dirlist = [right, up, down, left]

    for tower in createdTowers:
        for wall in tower.towerwalls:
            for dir in dirlist:
                if dir == wall.squpos:
                    GUI.gui.createMessage("Path Blocked")
                    tower.remove()
                    Player.player.money += tower.cost
                    GUI.gui.myDispatcher.Money = str(Player.player.money)
                    return


def placeTower(*args):
    '''Places a tower at location of the touch'''
    pos = args[1]
    towerselected = args[0].instance
    sufficient_funds = True if towerselected.cost <= Player.player.money else False
    if sufficient_funds == False:
        GUI.gui.createMessage("Not Enough Money")
    collide = None
    towerWidget = Widget(pos=pos, size=(Map.mapvar.squsize * 2 - 1, Map.mapvar.squsize * 2 - 1))
    for wall in Map.mapvar.wallcontainer.children:
        if towerWidget.collide_widget(wall):
            collide = wall
            GUI.gui.createMessage("Can't Overlap")

    if sufficient_funds and not collide:
        newTower = eval("Towers." + towerselected.type + towerselected.base)(pos)
        Map.mapvar.towercontainer.add_widget(newTower)
        Player.player.towerSelected = None
        return newTower

def updateAnim(*args):
    for child in GUI.gui.waveStreamerEnemyLayout.children:
        if child.id == 'wave' + str(Player.player.wavenum - 1):
            GUI.gui.waveStreamerEnemyLayout.remove_widget(child)
            break
    GUI.gui.waveScroller.scroll_x = 0
    GUI.gui.waveAnimation.start(GUI.gui.waveScroller)


def nextWave(*args):
    '''Send the next enemy wave'''
    Player.player.score += int(Player.player.wavetimeInt * Player.player.wavenum * .25)
    GUI.gui.myDispatcher.Score = str(Player.player.score)
    Player.player.wavenum += 1
    GUI.gui.myDispatcher.WaveNum = str(Player.player.wavenum)
    Map.mapvar.enemypanel.CurrentWave = str(Player.player.wavenum)
    # GUI.gui.myDispatcher.Wave = str(Player.player.wavenum)
    Player.player.wavetime = Map.mapvar.waveseconds
    Player.player.wavetimeInt = int(Map.mapvar.waveseconds)
    GUI.gui.myDispatcher.Timer = str(Player.player.wavetimeInt)
    Player.player.next_wave = False
    SenderClass.Sender(specialSend=False)
    GUI.gui.waveAnimation.start(GUI.gui.waveScroller)
    if Player.player.waveList[Player.player.wavenum]['isboss']:
        GUI.gui.addAlert('Boss Round. Wave ' + str(Player.player.wavenum) + ' starting', 'warning')
    else:
        GUI.gui.addAlert('Wave ' + str(Player.player.wavenum) + ' starting', 'warning')
