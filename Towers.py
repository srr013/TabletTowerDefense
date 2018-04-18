import operator
import os
import random
from kivy.animation import Animation
from kivy.graphics import *
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.widget import Widget

from kivy.properties import NumericProperty

import GUI
import Localdefs
import Map
import Player
import Shot
import TowerGroup
import Utilities
import TowerNeighbors


class Tower(Widget):
    """Towers attack enemies and define the enemy path. Specific tower types below Super this class."""
    level = NumericProperty(1)

    def on_level(self, instance, value):
        self.levelLabel.text = str(int(value))

    def __init__(self, pos, **kwargs):
        Player.player.analytics.towersBought += 1
        super(Tower, self).__init__(**kwargs)
        self.pos = pos
        self.targetTimer = 0
        Player.player.money -= self.cost
        GUI.gui.myDispatcher.Money = str(Player.player.money)
        Localdefs.towerlist.append(self)
        self.size = (Map.mapvar.squsize * 2 - 1, Map.mapvar.squsize * 2 - 1)
        self.rect = Utilities.createRect(self.pos, self.size, instance=self)
        self.squareheight = 2
        self.squarewidth = 2
        self.towerwalls = Utilities.genWalls(self.pos, self.squarewidth, self.squareheight)
        self.imageNum = 0
        self.imagestr = os.path.join('towerimgs', self.type, str(self.imageNum) + '.png')
        self.image = Utilities.imgLoad(self.imagestr)
        self.image.pos = self.pos
        self.image.size = self.size
        self.image.allow_stretch = True
        self.currentRotation = 0
        self.add_widget(self.image)
        self.currentPointerAngle = 0
        self.turretpointpos = [self.center[0] + 12, self.center[1]]
        self.lastNeighborCount = 0
        self.neighborFlag = 'update'
        self.neighborList = []
        self.neighbors = TowerNeighbors.getNeighbors(self)  # neighbors is a directional dict 'left':towerobj
        self.towerGroup = None
        TowerNeighbors.getGroup(self)
        self.adjacentRoadPos = Utilities.adjacentRoadPos(self.pos)
        self.adjacentRoads = list()
        self.adjacentRoadFlag = False
        self.totalspent = self.cost
        self.refund = self.totalspent
        self.abilities = list()
        self.buttonlist = list()
        self.upgrades = list()
        self.attackair = True
        self.attackground = True
        self.attacktype = 'single'
        self.hasTurret = False
        self.shotcount = 0
        self.allowedshots = 1
        self.totalUpgradeTime = 0
        self.upgradeTimeElapsed = 0
        self.percentComplete = 0
        self.upgradePath = None

        self.levelLabel = Label(text=str(self.level), size_hint=(None, None), size=(7, 7),
                                pos=(self.image.pos[0] + 6, self.image.pos[1] + 6),
                                color=[1, .72, .07, 1], font_size=(18), bold=True)
        self.add_widget(self.levelLabel)
        self.image.bind(size=self.bindings)

        self.towerGroup.needsUpdate = True

    def bindings(self):
        self.size = (Map.mapvar.squsize * 2 - 1, Map.mapvar.squsize * 2 - 1)
        self.image.size = self.size
        if self.turret:
            self.turret.size = (Map.mapvar.squsize, Map.mapvar.squsize)
        self.range = Map.mapvar.squsize * self.rangecalc

    def remove(self, sell=False):
        for wall in self.towerwalls:
            Map.mapvar.wallcontainer.remove_widget(wall)
        Map.myGrid.walls = Map.path.get_wall_list()
        for wall in self.towerwalls:
            Map.myGrid.updateWalls(wall.squpos)
        if self in Localdefs.towerlist:
            Localdefs.towerlist.remove(self)
        if self.type == 'Gravity':
            if self.animation:
                self.animation.cancel_all(self.turret)
            if self.closeanimation:
                self.closeanimation.cancel_all(self.turret)
        Map.mapvar.towercontainer.remove_widget(self)
        if self.upgradePath == 'LeaderPath' and self.towerGroup.hasLeader:
            self.towerGroup.hasLeader = False
        if self in self.towerGroup.towerSet:
            self.towerGroup.towerSet.remove(self)
        if sell and self.neighborList:
            TowerNeighbors.updateNeighbors(self)

    def updateModifiers(self):
        self.damage = self.damage * self.towerGroup.dmgModifier
        if self.type != 'Gravity' and self.type != 'Ice':
            self.reload = self.reload * self.towerGroup.reloadModifier
            self.range = self.rangecalc * Map.mapvar.squsize * self.towerGroup.rangeModifier
        if self.type == 'Wind':
            self.push = self.push * self.towerGroup.pushModifier
        if self.type == 'Ice':
            self.slowtime = self.slowtime * self.towerGroup.slowTimeModifier
            self.slowpercent = self.slowpercent * self.towerGroup.slowPercentModifier
        if self.type == 'Gravity':
            self.stuntime = self.stuntime * self.towerGroup.stunTimeModifier
        self.setUpgradeData()

    def upgrade(self):
        if self.type == 'Gravity':
            if self.animating:
                self.animation.cancel_all(self.turret)
                self.closeanimation.start(self.turret)
        if self.hasTurret:
            self.remove_widget(self.turret)
        with self.canvas:  # draw upgrade bars
            Color(1, 1, 1, 1)
            self.statusbar = Line(points=[self.x + .5*Map.mapvar.squsize, self.y + Map.mapvar.squsize/3, self.x + self.width - .5*Map.mapvar.squsize, self.y + Map.mapvar.squsize/3], width=4,
                                  cap='none')
            Color(0, 0, 0, 1)
            self.remainingtime = Line(points=[self.x + .5*Map.mapvar.squsize, self.y + Map.mapvar.squsize/3, self.x + .5*Map.mapvar.squsize, self.y + Map.mapvar.squsize/3], width=4, cap='none')
        self.upgradeTimeElapsed = 0
        self.totalUpgradeTime = self.level * 5
        if self.level == Player.player.upgPathSelectLvl:
            self.setupUpgradePath()

    def updateUpgradeStatusBar(self):
        self.percentComplete = self.upgradeTimeElapsed / self.totalUpgradeTime
        if self.percentComplete >= 1:
            self.upgradeTowerStats()
            self.level += 1
            if Player.player.analytics.maxTowerLevel < self.level:
                Player.player.analytics.maxTowerLevel = self.level
            self.canvas.remove(self.remainingtime)
            self.canvas.remove(self.statusbar)
            self.totalUpgradeTime = self.upgradeTimeElapsed = self.percentComplete = 0
            if self.hasTurret:
                self.add_widget(self.turret)

            return
        self.remainingtime.points = [self.x + .5*Map.mapvar.squsize, self.y + Map.mapvar.squsize/3, self.x + .5*Map.mapvar.squsize + ((self.width - Map.mapvar.squsize) * self.percentComplete),
                                     self.y + Map.mapvar.squsize/3]
    def setupUpgradePath(self):
        #called at upgrade start so self.level+!
        if self.upgradePath == 'LeaderPath':
            if self.hasTurret:
                self.hasTurret = False
                self.remove_widget(self.turret)
            self.damageBonus = (self.level + 1 - Player.player.upgPathSelectLvl) * 20
            self.reloadBonus = (self.level + 1 - Player.player.upgPathSelectLvl) * 20
            self.rangeBonus = (self.level + 1 - Player.player.upgPathSelectLvl) * 20
            self.pushBonus = (self.level + 1 - Player.player.upgPathSelectLvl) * 20
            self.slowpercentBonus = (self.level + 1 - Player.player.upgPathSelectLvl) * 20
            self.slowtimeBonus = (self.level + 1 - Player.player.upgPathSelectLvl) * 20
            self.stuntimeBonus = (self.level + 1 - Player.player.upgPathSelectLvl) * 20
        else:
            if self.type == 'Fire':
                self.turret.source = os.path.join("towerimgs", self.type, "turret2.gif")

    def upgradeTowerStats(self):
        self.refund = self.totalspent * .8
        self.range = self.range + self.range * self.upgradeDict['Range'][self.level - 1]
        #self.nextRange = round(self.upgradeDict['Range'][self.level] * self.range + self.range, 1)
        if self.type == 'Ice':
            self.slowpercent = self.slowpercent + self.slowpercent * self.upgradeDict['Slow%'][self.level - 1]
            #self.nextSlowPercent = round(self.upgradeDict['Slow%'][self.level] * self.slowpercent + self.slowpercent, 2)
            self.slowtime = self.slowtime + self.slowtime * self.upgradeDict['SlowTime'][self.level - 1]
            #self.nextSlowTime = round(self.upgradeDict['SlowTime'][self.level] * self.slowtime + self.slowtime, 1)
        elif self.type == 'Wind':
            self.push = self.push + self.push * self.upgradeDict['Push'][self.level - 1]
            #self.nextPush = round(self.upgradeDict['Push'][self.level] * self.push + self.push, 1)
            self.reload = self.reload + self.reload * self.upgradeDict['Reload'][self.level - 1]
            #self.nextReload = round(self.upgradeDict['Reload'][self.level] * self.reload + self.reload, 1)
        else:
            self.damage = self.damage + self.damage * self.upgradeDict['Damage'][self.level - 1]
            #self.nextDamage = round(self.upgradeDict['Damage'][self.level] * self.damage + self.damage, 1)
            self.reload = self.reload + self.reload * self.upgradeDict['Reload'][self.level - 1]
            #self.nextReload = round(self.upgradeDict['Reload'][self.level] * self.reload + self.reload, 1)

        self.setUpgradeData()

    def setUpgradeData(self):
        if self.upgradePath != 'LeaderPath':
            dict = self.upgradeDict
        else:
            dict = self.upgradeLeaderDict
        self.nextDamage = round(dict['Damage'][self.level - 1] * self.damage + self.damage, 1)
        self.groupDamage = str(int((self.towerGroup.dmgModifier-1.0)*100))+'%'
        self.nextReload = round(dict['Reload'][self.level - 1] * self.reload + self.reload, 1)
        self.groupReload = '0%' if self.towerGroup.reloadModifier == 1 else str(int(self.towerGroup.reloadModifier-1.0)*100)+'%'
        if self.towerGroup.leader:
            self.groupReload = self.towerGroup.leader.reloadBonus
        self.nextRange = int(dict['Range'][self.level - 1] * self.range + self.range)
        self.groupRange = str(int((self.towerGroup.rangeModifier-1.0)*100))+'%'
        if self.upgradePath != 'LeaderPath':
            self.upgradeData = ['Dmg', round(self.damage,1), self.groupDamage, self.nextDamage,
                                'Rld', round(self.reload,1), self.groupReload, self.nextReload,
                                'Rng', int(self.range), self.groupRange, self.nextRange]
        else:
            self.upgradeData = ['GrpDmg', str(int(self.damageBonus))+"%", self.groupDamage, self.nextDamage,
                                'GrpRld', str(int(self.reloadBonus))+"%", self.groupReload, self.nextReload,
                                'GrpRng', str(int(self.rangeBonus))+"%", self.groupRange, self.nextRange]

    def takeTurn(self):
        '''Maintain reload wait period and call target() once period is over
        Frametime: the amount of time elapsed per frame'''
        if self.totalUpgradeTime == 0:
            self.targetTimer -= Player.player.frametime
            ##if the rest period is up then shoot again
            if self.targetTimer <= 0:
                self.target()


    def target(self):
        '''Create a sorted list of enemies based on distance from the tower. If enemy is within tower range then hit enemy'''
        if self.attacktype == 'single':
            sortedlist = reversed(sorted(Map.mapvar.enemycontainer.children, key=operator.attrgetter("weightedcurnode")))
            for enemy in sortedlist:
                if Utilities.in_range(self, enemy):
                    if enemy.isair and self.attackair:
                        if not self.type == 'Wind':
                            self.moveTurret(enemy)
                        self.shotcount += 1
                        Shot.Shot(self, enemy)
                    if not enemy.isair and self.attackground:
                        self.moveTurret(enemy)
                        self.shotcount += 1
                        Shot.Shot(self, enemy)
                    if self.shotcount > 0:
                        self.targetTimer = self.towerGroup.targetTimer = self.reload
                if self.shotcount >= self.allowedshots:
                    return
        else:
            sortedlist = Utilities.get_all_in_range(self,Map.mapvar.enemycontainer.children)
            for enemy in sortedlist:
                if enemy.isair and self.attackair:
                    self.hitEnemy(enemy)
                    self.shotcount += 1
                if not enemy.isair and self.attackground:
                    self.hitEnemy(enemy)
                    self.shotcount += 1
            if self.shotcount > 0:
                self.towerGroup.targetTimer = self.reload
                if self.towerGroup.towersNeedingAnim:
                    self.towerGroup.disable()
                    self.towerGroup.towersNeedingAnim = []


    def hitEnemy(self, enemy = None):
        '''Reduces enemy health by damage - armor'''
        Player.player.analytics.gameDamage += self.damage
        if self.type == "Ice" and enemy.slowtime <= self.slowtime - 1:
            enemy.slowtimers.append(enemy)
            if enemy.image.color != [0, 0, 1, 1]:
                enemy.image.color = [0, 0, 1, 1]
            enemy.slowtime = self.slowtime
            enemy.slowpercent = 1 - self.slowpercent
            enemy.health -= max(self.damage - enemy.armor, 0)
            enemy.checkHealth()
        elif self.type == 'Gravity':
            rand = True if random.randint(0, 100) > 90 else False
            if rand == True:
                enemy.stuntimers.append(enemy)
                enemy.stuntime = self.stuntime
                if enemy.anim:
                    enemy.anim.cancel_all(enemy)
                enemy.addStunImage()
            dir = (enemy.pos[0] - self.pos[0], enemy.pos[1] - self.pos[1])
            pushx = pushy = 0
            if dir[0] <= 0:
                pushx = self.push
            elif dir[0] > 0:
                pushx = -self.push
            if dir[1] <= 0:
                pushy = self.push
            elif dir[1] > 0:
                pushy = -self.push
            enemy.pushed = [pushx, pushy]
            enemy.health -= max(self.damage - enemy.armor, 0)
            enemy.checkHealth()

    def moveTurret(self, enemy):
        angle = 180 + Utilities.get_rotation(self, enemy)
        # print ("angle:", angle)
        self.turret.anim = Animation(angle=angle, d=.1)
        self.turret.anim.start(self.turret_rot)

    def loadTurret(self):
        if self.type == 'Gravity':
            with self.canvas:
                self.color = Color(0, 0, 0, 1)
                self.turret = Image(source=os.path.join('towerimgs', 'Gravity', "attack.png"),
                                         size=(Map.mapvar.squsize * 1.5, Map.mapvar.squsize * 1.5),
                                         pos=(self.center[0] - Map.mapvar.squsize * .74,
                                              self.center[1] - Map.mapvar.squsize * .74))
            self.animation = None
            self.closeanimation = Animation(size=(Map.mapvar.squsize * 1.5, Map.mapvar.squsize * 1.5),
                                            pos=(self.center[0] - Map.mapvar.squsize * .74,
                                                 self.center[1] - Map.mapvar.squsize * .74),
                                            duration=.3)
            self.closeanimation.bind(on_complete = self.closeAnimation)
        else:
            self.turretstr = os.path.join('towerimgs', self.type, 'turret.png')
            self.turret = Utilities.imgLoad(self.turretstr)
            self.turret.allow_stretch = True
            self.turret.size = (Map.mapvar.squsize, Map.mapvar.squsize)
            self.turret.center = self.center
            self.add_widget(self.turret)
            with self.turret.canvas.before:
                PushMatrix()
                self.turret_rot = Rotate()
                self.turret_rot.origin = self.turret.center
                self.turret_rot.axis = (0, 0, 1)
                self.turret_rot.angle = 0
            with self.turret.canvas.after:
                PopMatrix()

    def closeAnimation(self, *args):
        self.animating = False


class FireTower(Tower):
    type = "Fire"
    cost = 15
    initdamage = 10
    initrange = 100
    initreload = .4
    attacks = "Ground"
    imagestr = os.path.join('towerimgs', 'Fire', 'icon.png')

    def __init__(self, pos, **kwargs):
        self.rangecalc = 3.3
        Tower.__init__(self, pos, **kwargs)
        self.pos = pos
        self.cost = FireTower.cost
        self.initrange = self.range = FireTower.initrange
        self.initdamage = self.damage = FireTower.initdamage
        self.initreload = self.reload = FireTower.initreload
        self.type = FireTower.type
        self.attacktype = 'single'
        self.attackair = False
        self.active = True
        self.shotimage = "flame.png"
        self.hasTurret = True
        self.loadTurret()
        self.upgradeDict = {'Damage': [.1, .1, .1, .1, .1, 0], 'Range': [0, 0, 0, 0, .5, 0],
                            'Reload': [0, 0, 0, 0, -.2, 0], 'Cost': [5, (50,1), 150, 250, (500,1), 'NA']}
        self.upgradeLeaderDict = {'Damage': [.1, .1, .1, .1, .1, 0], 'Range': [0, 0, 0, 0, .5, 0],
                            'Reload': [0, 0, 0, 0, -.2, 0], 'Cost': [5, 50, 150, 250, (500,1), 'NA']}
        self.setUpgradeData()


class LifeTower(Tower):
    type = "Life"
    cost = 15
    initrange = 150
    initdamage = 10
    initreload = 1.0
    attacks = "Both"
    imagestr = os.path.join('towerimgs', 'Life', 'icon.png')

    def __init__(self, pos, **kwargs):
        self.rangecalc = 5
        Tower.__init__(self, pos, **kwargs)
        self.pos = pos
        self.cost = LifeTower.cost
        self.initrange = self.range = LifeTower.initrange
        self.initdamage = self.damage = LifeTower.initdamage
        self.initreload = self.reload = LifeTower.initreload
        self.type = LifeTower.type
        self.attacktype = 'single'
        self.attackair = True
        self.shotimage = "cannonball.png"
        self.hasTurret = True
        self.active = True
        self.loadTurret()
        self.upgradeDict = {'Damage': [.1, .1, .1, .1, .1, 0], 'Range': [0, 0, 0, 0, .5, 0],
                            'Reload': [0, 0, 0, 0, -.2, 0], 'Cost': [5, 50, 150, 250, (500,1), 'NA']}
        self.upgradeLeaderDict = {'Damage': [.1, .1, .1, .1, .1, 0], 'Range': [0, 0, 0, 0, .5, 0],
                            'Reload': [0, 0, 0, 0, -.2, 0], 'Cost': [5, 50, 150, 250, (500, 1), 'NA']}
        self.setUpgradeData()


class GravityTower(Tower):
    type = "Gravity"
    cost = 15
    initrange = 60
    initdamage = 30
    initreload = 2.5
    initstuntime = 3
    initpush = -10
    attacks = "Ground"
    imagestr = os.path.join('towerimgs', 'Gravity', 'icon.png')

    def __init__(self, pos, **kwargs):
        self.rangecalc = 2
        Tower.__init__(self, pos, **kwargs)
        self.pos = pos
        self.cost = GravityTower.cost
        self.initrange = self.range = GravityTower.initrange
        self.initdamage = self.damage = GravityTower.initdamage
        self.initreload = self.reload = GravityTower.initreload
        self.initstuntime = self.stuntime = GravityTower.initstuntime
        self.initpush = self.push = GravityTower.initpush
        self.type = GravityTower.type
        self.attackair = False
        self.attacktype = "multi"
        self.active = False
        self.allowedshots = 999
        self.hasTurret = True
        self.animating = False
        self.loadTurret()
        self.upgradeDict = {'Damage': [.2, .2, .3, .3, .6, 0], 'Range': [0, 0, 0, 0, 0, 0],
                            'Reload': [0, 0, 0, 0, 0, 0], 'Cost': [5, 50, 150, 250, (500,1), 'NA']}
        self.upgradeLeaderDict = {'Damage': [.2, .2, .3, .3, .6, 0], 'Range': [0, 0, 0, 0, 0, 0],
                            'Reload': [0, 0, 0, 0, 0, 0], 'Cost': [5, 50, 150, 250, (500, 1), 'NA']}
        self.setUpgradeData()

    def setUpgradeData(self):
        if self.upgradePath != 'LeaderPath':
            dict = self.upgradeDict
        else:
            dict = self.upgradeLeaderDict
        self.nextDamage = round(dict['Damage'][self.level - 1] * self.damage + self.damage, 1)
        self.groupDamage = str(int((self.towerGroup.dmgModifier - 1.0) * 100)) + '%'
        self.nextReload = round(dict['Reload'][self.level - 1] * self.reload + self.reload, 1)
        self.nextRange = int(dict['Range'][self.level - 1] * self.range + self.range)
        self.upgradeData = ['Dmg', round(self.damage, 1), self.groupDamage, self.nextDamage,
                            'Rld', round(self.reload, 1), '0%', self.nextReload,
                            'Rng', int(self.range), '0%', self.nextRange]


class IceTower(Tower):
    type = "Ice"
    cost = 15
    initrange = 60
    initdamage = 1
    initreload = 2
    initslowtime = 3
    initslowpercent = .2
    attacks = "Both"
    imagestr = os.path.join('towerimgs', 'Ice', 'icon.png')

    def __init__(self, pos, **kwargs):
        self.rangecalc = 2
        Tower.__init__(self, pos, **kwargs)
        self.pos = pos
        self.cost = IceTower.cost
        self.initrange = self.range = IceTower.initrange
        self.initdamage = self.damage = IceTower.initdamage
        self.initreload = self.reload = IceTower.initreload
        self.initslowtime = self.slowtime = IceTower.initslowtime
        self.initslowpercent = self.slowpercent = IceTower.initslowpercent
        self.type = IceTower.type
        self.attackair = True
        self.attacktype = 'multi'
        self.active = False
        self.allowedshots = 999
        self.hasTurret = False
        self.upgradeDict = {'Slow%': [.05, .05, .05, .05, .15, 0], 'Range': [0, 0, 0, 0, 0, 0],
                            'SlowTime': [.1, .1, .1, .1, .5, 0], 'Cost': [5, 50, 150, 250, (500,1), 'NA']}
        self.upgradeLeaderDict = {'Slow%': [.05, .05, .05, .05, .15, 0], 'Range': [0, 0, 0, 0, 0, 0],
                            'SlowTime': [.1, .1, .1, .1, .5, 0], 'Cost': [5, 50, 150, 250, (500, 1), 'NA']}
        self.setUpgradeData()

    def setUpgradeData(self):
        if self.upgradePath != 'LeaderPath':
            dict = self.upgradeDict
        else:
            dict = self.upgradeLeaderDict
        self.nextSlowPercent = round(dict['Slow%'][self.level - 1] * self.slowpercent + self.slowpercent, 2)
        self.groupSlowPercent = str(int((self.towerGroup.slowPercentModifier-1.0)*100))+'%'
        self.nextSlowTime = round(dict['SlowTime'][self.level - 1] * self.slowtime + self.slowtime, 1)
        self.groupSlowTime = str(int((self.towerGroup.slowTimeModifier-1.0)*100))+'%'
        self.nextRange = round(dict['Range'][self.level - 1] * self.range + self.range, 1)
        self.upgradeData = ['Slow', str(int(self.slowpercent*100))+'%', self.groupSlowPercent, str(int((self.nextSlowPercent)*100))+'%',
                            'SlowTm', str(round(self.slowtime,1))+'s', self.groupSlowTime, str(round(self.nextSlowTime,1))+'s',
                            'Rng', round(self.range,1), '0%', round(self.nextRange,1)]


class WindTower(Tower):
    type = "Wind"
    cost = 15
    initrange = 300
    initdamage = 40
    initreload = 4
    initpush = 25
    attacks = 'Air'
    imagestr = os.path.join('towerimgs', 'Wind', 'icon.png')

    def __init__(self, pos, **kwargs):
        self.rangecalc = 10
        Tower.__init__(self, pos, **kwargs)
        self.pos = pos
        self.cost = WindTower.cost
        self.initrange = self.range = WindTower.initrange
        self.initdamage = self.damage = WindTower.initdamage
        self.initreload = self.reload = WindTower.initreload
        self.initpush = self.push = WindTower.initpush
        self.type = WindTower.type
        self.attackair = True
        self.attackground = False
        self.attacktype = 'single'
        self.shotimage = "gust.png"
        self.hasTurret = True
        self.loadTurret()
        if self.towerGroup.active:
            self.turret.source = os.path.join('towerimgs', self.type, "turret.gif")
        self.active = False
        self.allowedshots = 1

        self.upgradeDict = {'Push': [.1, .1, .1, .1, .1, 0], 'Range': [0, 0, .1, 0, .5, 0],
                            'Reload': [0, 0, -.1, 0, -.2, 0], 'Cost': [5, 50, 150, 250, (500,1), 'NA']}
        self.upgradeLeaderDict = {'Push': [.1, .1, .1, .1, .1, 0], 'Range': [0, 0, .1, 0, .5, 0],
                            'Reload': [0, 0, -.1, 0, -.2, 0], 'Cost': [5, 50, 150, 250, (500, 1), 'NA']}

        self.setUpgradeData()

    def setUpgradeData(self):
        if self.upgradePath != 'LeaderPath':
            dict = self.upgradeDict
        else:
            dict = self.upgradeLeaderDict
        self.nextPush = round(dict['Push'][self.level - 1] * self.push + self.push, 1)
        self.groupPush = str(int((self.towerGroup.pushModifier-1.0)*100))+'%'
        self.nextReload = round(dict['Reload'][self.level - 1] * self.reload + self.reload, 1)
        self.groupReload = str(int((self.towerGroup.reloadModifier-1.0)*100))+'%'
        self.nextRange = round(dict['Range'][self.level - 1] * self.range + self.range, 1)
        self.upgradeData = ['Push', round(self.push,1), self.groupPush, round(self.nextPush,1),
                            'Rld', round(self.reload,1), self.groupReload, round(self.nextReload,1),
                            'Rng', int(self.range), '0%', int(self.nextRange)]


available_tower_list = [FireTower, IceTower, GravityTower, WindTower, LifeTower]
baseTowerList = [(tower.type, tower.cost, tower.initdamage, tower.initrange, tower.initreload, tower.imagestr, tower.attacks) for tower
                 in available_tower_list]


class Icon():
    def __init__(self, tower):
        '''Instantiate an Icon with the tower information it represents'''
        self.type = tower[0]
        self.base = "Tower"
        self.cost = tower[1]
        self.damage = tower[2]
        self.range = tower[3]
        self.reload = tower[4]
        self.attacks = tower[6]
        Localdefs.iconlist.append(self)
        try:
            self.imgstr = tower[5]
            self.img = Utilities.imgLoad(self.imgstr)

        except:
            self.imgstr = str(os.path.join('towerimgs', '0.png'))
            self.img = Utilities.imgLoad(self.imgstr)
        self.rect = Utilities.createRect(self.img.pos, self.img.size, self)
