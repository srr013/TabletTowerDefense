
from kivy.uix.widget import Widget

import MainFunctions
import Map
import Player
import SenderClass
import __main__
import Towers
import FireTower
import LifeTower
import IceTower
import GravityTower
import WindTower
import Messenger
import TowerNeighbors
import TowerGroup


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
                Messenger.messenger.createMessage("Path Blocked")
                Player.player.money += tower.cost
                Player.player.analytics.moneySpent -= tower.cost
                Player.player.myDispatcher.Money = str(Player.player.money)
    if createdTowers:
        resetEnemyPaths()
        towerset = set()
        towergroupset = set()
        towerset.add(createdTowers[0])
        TowerNeighbors.initNeighbors(createdTowers[0],towerset,towergroupset)
        tower = next(iter(towerset))
        if len(towergroupset) == 0:
            tower.towerGroup = TowerGroup.TowerGroup(tower)
            tg = tower.towerGroup
        else:
            tg = next(iter(towergroupset))
            tower.towerGroup = tg
        tg.needsUpdate = True
        for tower in towerset:
            TowerNeighbors.getImage(tower)
            tower.towerGroup = tg
            if tower.leader:
                tg.leader = tower
        for menu in towerset:
            menu.setTowerData()

def resetEnemyPaths():
    for enemy in Map.mapvar.enemycontainer.children:
        if not enemy.isair:
            if enemy.anim:
                enemy.anim.cancel_all(enemy)
            if enemy.backToRoad:
                enemy.backToRoad.cancel_all(enemy)
            try:
                enemy.movelist = Map.mapvar.enemymovelists[enemy.movelistNum]
                enemy.dirlist = Map.mapvar.dirmovelists[enemy.movelistNum]
                enemy.getNearestRoad()
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
                    Messenger.messenger.createMessage("Path Blocked")
                    tower.remove()
                    Player.player.money += tower.cost
                    Player.player.myDispatcher.Money = str(Player.player.money)
                    return


def placeTower(*args):
    '''Places a tower at location of the touch'''
    parentPos = Map.mapvar.background.to_parent(*args[1])
    pos = args[1]
    towerselected = args[0].instance
    sufficient_funds = True if towerselected.cost <= Player.player.money else False
    if sufficient_funds == False:
        Messenger.messenger.createMessage("Not Enough Money")
    collide = None
    towerWidget = Widget(pos=parentPos, size=(Map.mapvar.squsize * 2 - 1, Map.mapvar.squsize * 2 - 1))
    for wall in Map.mapvar.wallcontainer.children:
        if towerWidget.collide_widget(wall):
            print towerWidget.pos, wall.pos, wall.size
            collide = wall
            Messenger.messenger.createMessage("Can't Overlap")

    if sufficient_funds and not collide:
        newTower = eval(towerselected.type+"Tower." + towerselected.type + towerselected.base)(pos)
        Player.player.analytics.moneySpent += newTower.cost
        Map.mapvar.towercontainer.add_widget(newTower)
        Player.player.towerSelected = None
        return newTower

def updateAnim(*args):
    for child in __main__.ids.wavelist.children:
        i = int(child.id[4:])
        if i <= Player.player.wavenum:
            __main__.ids.wavelist.remove_widget(child)
            break
    __main__.ids.wavescroller.scroll_x = 0
    __main__.ids.wavestreamer.waveAnimation.start(__main__.ids.wavescroller)


def nextWave(*args):
    '''Send the next enemy wave'''
    Player.player.score += int(Player.player.wavetimeInt * Player.player.wavenum * .25)
    Player.player.myDispatcher.Score = str(Player.player.score)
    Player.player.wavenum += 1
    #Map.mapvar.enemypanel.CurrentWave = str(Player.player.wavenum)
    Player.player.wavetime = Map.mapvar.waveseconds
    Player.player.wavetimeInt = int(Map.mapvar.waveseconds)
    Player.player.myDispatcher.Timer = str(Player.player.wavetimeInt)
    Player.player.next_wave = False
    Player.player.sound.playSound(Player.player.sound.waveBeep)
    SenderClass.Sender(specialSend=False)
    __main__.ids.wavestreamer.waveAnimation.start(__main__.ids.wavescroller)
    if Player.player.waveList[Player.player.wavenum]['isboss']:
        Messenger.messenger.addAlert('Bosses are worth 5 health. Wave '+ str(Player.player.wavenum)+': '+Player.player.waveList[Player.player.wavenum]['enemytype'] , 'warning')
    else:
        Messenger.messenger.addAlert('Wave ' + str(Player.player.wavenum)+": "+Player.player.waveList[Player.player.wavenum]['enemytype'], 'normal')
