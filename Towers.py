import operator
import os
import random
from kivy.animation import Animation
from kivy.graphics import *
from kivy.uix.image import Image
from kivy.uix.label import Label

from kivy.properties import NumericProperty

import GUI
import Localdefs
import Map
import Player
import Shot
import TowerGroup
import Utilities
import TowerNeighbors
import __main__



class Tower(Image):
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
        self.source = self.imagestr
        self.allow_stretch = True
        self.currentRotation = 0
        self.levelLabel = Label(text=str(self.level), size_hint=(None, None), size=(7, 7),
                                pos=(self.pos[0] + 6, self.pos[1] + 6),
                                color=[1, .72, .07, 1], font_size=__main__.Window.width*.018, bold=True)
        self.add_widget(self.levelLabel)
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
        self.animating = False
        self.rangeExclusion = 0
        self.blackhole_in_progress = False
        self.hasTurret = False
        self.targetedEnemy = None
        self.shotcount = 0
        self.allowedshots = 1
        self.totalUpgradeTime = 0
        self.upgradeTimeElapsed = 0
        self.percentComplete = 0
        self.upgradePath = None
        self.leader = False
        self.recharging = False
        self.bind(size=self.bindings)
        self.towerGroup.needsUpdate = True

    def bindings(self):
        self.size = (Map.mapvar.squsize * 2 - 1, Map.mapvar.squsize * 2 - 1)
        if self.turret:
            self.turret.size = (Map.mapvar.squsize, Map.mapvar.squsize)
        self.range = self.range / 30 * Map.mapvar.squsize

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
        if self.leader and self.towerGroup.leader:
            self.towerGroup.hasLeader = False
        if self in self.towerGroup.towerSet:
            self.towerGroup.towerSet.remove(self)
        if sell and self.neighborList:
            TowerNeighbors.updateNeighbors(self)

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
        self.refund = self.totalspent * .8
        self.upgradeTimeElapsed = 0
        self.totalUpgradeTime = self.level #############UPDATE############

    def updateUpgradeStatus(self):
        self.percentComplete = self.upgradeTimeElapsed / self.totalUpgradeTime
        if self.percentComplete >= 1:
            self.level += 1
            if Player.player.analytics.maxTowerLevel < self.level:
                Player.player.analytics.maxTowerLevel = self.level
            self.canvas.remove(self.remainingtime)
            self.canvas.remove(self.statusbar)
            self.totalUpgradeTime = self.upgradeTimeElapsed = self.percentComplete = 0
            if self.hasTurret:
                self.add_widget(self.turret)
            if self.level == Player.player.upgPathSelectLvl + 1:
                if self.upgradePath == 'LeaderPath':
                    self.leader = True
                self.setupUpgradePath()
                self.setTowerData()
            if self.leader:
                self.towerGroup.updateModifiers()
            self.setTowerData()
            if Map.mapvar.background.popUpOpen and GUI.gui.tbbox == 'Tower':
                Map.mapvar.background.removeAll()
                GUI.gui.towerMenu(Player.player.towerSelected.pos)
            return
        else:
            self.remainingtime.points = [self.x + .5*Map.mapvar.squsize, self.y + Map.mapvar.squsize/3, self.x + .5*Map.mapvar.squsize + ((self.width - Map.mapvar.squsize) * self.percentComplete),
                                     self.y + Map.mapvar.squsize/3]

    def setTowerData(self):
        self.stats = {}
        self.menuStats = {}
        list = self.menu
        if not self.leader:
            for x in list:
                tgmod = eval("self.towerGroup." + x[0] + "Modifier") - 1
                val = eval("self.init" + x[0]) * self.upgradeDict[x[0]][self.level - 1]
                val = val + val * tgmod
                val = round(val, x[1]) if x[1] > 0 else int(val)
                if self.upgradeDict[x[0]][self.level] == 'NA':
                    nextval = 'NA'
                else:
                    nextval = eval("self.init" + x[0]) * self.upgradeDict[x[0]][self.level]
                    nextval = nextval + nextval * tgmod
                    nextval = round(nextval, x[1]) if x[1] > 0 else int(nextval)
                self.stats[x[0]] = [val, tgmod, nextval]
                val = str(val) + x[2]
                nextval = str(nextval) + x[2]
                tgmod = str(int(tgmod*100)) + '%'
                self.menuStats[x[0]] = [val, tgmod, nextval]
        else:
            for x in list:
                bonus = int(eval("self.towerGroup."+x[0]+"Bonus") * 100) #units are always percent except slow/stuntime??
                bonus = str(bonus) + '%'
                mod = int(round((eval("self.towerGroup."+x[0]+"Modifier") - 1) * 100))
                mod = str(mod)+ '%'
                nextbonus = int(eval("self.towerGroup.next"+x[0]+"Bonus") * 100)
                nextbonus = str(nextbonus) + '%'
                self.menuStats[x[0]] = [bonus, mod, nextbonus]
        self.updateStats()

    def takeTurn(self):
        '''Maintain reload wait period and call target() once period is over
        Frametime: the amount of time elapsed per frame'''
        if self.totalUpgradeTime == 0:
            if self.targetedEnemy:
                if self.turretRotates:
                    if not self.turret.anim.have_properties_to_animate(self.turret_rot):
                        self.moveTurret(self.targetedEnemy)
            if self.recharging:
                self.recharge()
            self.targetTimer -= Player.player.frametime
            ##if the rest period is up then shoot again
            if self.targetTimer <= 0:
                self.target()

    def target(self):
        if self.targetedEnemy:
            if self.targetedEnemy.isAlive and Utilities.in_range(self, self.targetedEnemy):
                self.hitEnemy(self.targetedEnemy)
            else:
                self.targetedEnemy = None
        if not self.targetedEnemy and self.attacktype == 'single' and not self.leader:
            for enemy in Player.player.sortedlist:
                if Utilities.in_range(self, enemy):
                    if Utilities.can_attack(self, enemy):
                        self.hitEnemy(enemy)
                    if self.shotcount >= self.allowedshots:
                        return
        elif self.attacktype == 'multi' and not self.leader:
            sortedlist = Utilities.get_all_in_range(self,Map.mapvar.enemycontainer.children)
            for enemy in sortedlist:
                if Utilities.can_attack(self, enemy):
                    self.hitEnemy(enemy)
            if self.shotcount > 0:
                self.targetTimer = self.towerGroup.targetTimer = self.reload

    def moveTurret(self, enemy):
        if self.hasTurret and self.turretRotates:
            angle = 180 + Utilities.get_rotation(self, enemy)
            # print ("angle:", angle)
            self.turret.anim = Animation(angle=angle, d=.1)
            self.turret.anim.start(self.turret_rot)

    def loadTurret(self):
        if self.leader:
            if self.hasTurret:
                self.remove_widget(self.turret)
                self.hasTurret = False
            self.leaderturret = Image(source = "towerimgs/leaderturret.png", allow_stretch = True, size = (Map.mapvar.squsize, Map.mapvar.squsize))
            self.leaderturret.center = self.center
            self.add_widget(self.leaderturret)
        else:
            self.turretstr = os.path.join('towerimgs', self.type, 'turret.png')
            self.turret = Image(source = self.turretstr, allow_stretch = True, size = (Map.mapvar.squsize, Map.mapvar.squsize))
            self.turret.center = self.center
            self.turret.anim = None
            self.add_widget(self.turret)
            with self.turret.canvas.before:
                PushMatrix()
                self.turret_rot = Rotate()
                self.turret_rot.origin = self.turret.center
                self.turret_rot.axis = (0, 0, 1)
                self.turret_rot.angle = 180
            with self.turret.canvas.after:
                PopMatrix()


