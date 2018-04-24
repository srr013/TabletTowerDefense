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
        self.currentPointerAngle = 0
        self.turretpointpos = [self.center[0] + 12, self.center[1]]
        self.levelLabel = Label(text=str(self.level), size_hint=(None, None), size=(7, 7),
                                pos=(self.pos[0] + 6, self.pos[1] + 6),
                                color=[1, .72, .07, 1], font_size=(18), bold=True)
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
        self.rangeExclusion = 0
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
            if self.upgradePath == 'LeaderPath':
                self.leader = True
                self.upgradePath = ' '
                self.towerGroup.updateModifiers()
            else:
                self.setTowerData()
            if Map.mapvar.background.popUpOpen and GUI.gui.tbbox == 'Tower':
                Map.mapvar.background.removeAll()
                GUI.gui.towerMenu(Player.player.towerSelected.pos)
            return
        self.remainingtime.points = [self.x + .5*Map.mapvar.squsize, self.y + Map.mapvar.squsize/3, self.x + .5*Map.mapvar.squsize + ((self.width - Map.mapvar.squsize) * self.percentComplete),
                                     self.y + Map.mapvar.squsize/3]
    def setupUpgradePath(self):
        if self.leader:
            self.menu = self.leaderMenu
            self.loadTurret()
        else:
            self.menu = self.dmgMenu
            if self.type == 'Fire':
                self.turret.source = os.path.join("towerimgs", self.type, "turret2.gif")
                with self.turret.canvas.before:
                    PushMatrix()
                    self.turret_rot = Rotate()
                    self.turret_rot.origin = self.turret.center
                    self.turret_rot.axis = (0, 0, 1)
                    self.turret_rot.angle = 0
                with self.turret.canvas.after:
                    PopMatrix()
                self.shotimage = "shot2.png"
                self.shotDuration = 1
            elif self.type == 'Life':
                self.recharging = True
                self.turret.source = os.path.join("towerimgs", self.type, "reload_frame1.png")
                self.turret.size = (1.5 * Map.mapvar.squsize, 1.5 * Map.mapvar.squsize)
                self.turret.center = self.center
                self.shotDuration = .1
                self.shotimage = "shot2.png"
                self.rangeExclusion = Map.mapvar.squsize*4
            elif self.type == 'Wind':
                self.turret.source = os.path.join("towerimgs", self.type, "turret2.png")

    def setTowerData(self):
        self.refund = self.totalspent * .8
        if self.level == Player.player.upgPathSelectLvl+1:
            self.setupUpgradePath()
        x = self.initDamage * self.upgradeDict['Damage'][self.level-1]
        y = self.initDamage * self.upgradeDict['Damage'][self.level]
        self.damage = x * self.towerGroup.damageModifier
        self.nextDamage = y * self.towerGroup.damageModifier
        if self.type == 'Fire':
            x = self.initBurn * self.upgradeDict['Burn'][self.level - 1]
            y = self.initBurn * self.upgradeDict['Burn'][self.level]
            self.burn = x * self.towerGroup.burnModifier
            self.nextBurn = y * self.towerGroup.burnModifier
        elif self.type == 'Wind' or self.type == 'Life':
            x = self.initPush * self.upgradeDict['Push'][self.level - 1]
            y = self.initPush * self.upgradeDict['Push'][self.level]
            self.push = x * self.towerGroup.pushModifier
            self.nextPush = y * self.towerGroup.pushModifier
        if self.type != 'Ice' and self.type != 'Gravity':
            x = self.initReload * self.upgradeDict['Reload'][self.level - 1]
            y = self.initReload * self.upgradeDict['Reload'][self.level]
            self.reload = x * self.towerGroup.reloadModifier
            self.targetTimer = self.reload
            self.nextReload = y * self.towerGroup.reloadModifier
            x = self.initRange * self.upgradeDict['Range'][self.level - 1]
            y = self.initRange * self.upgradeDict['Range'][self.level]
            self.range = x * self.towerGroup.rangeModifier
            self.nextRange = y * self.towerGroup.rangeModifier
        elif self.type == 'Ice':
            x = self.initSlowPercent * self.upgradeDict['SlowPercent'][self.level - 1]
            y = self.initSlowPercent * self.upgradeDict['SlowPercent'][self.level]
            self.slowPercent = x * self.towerGroup.slowPercentModifier
            self.nextSlowPercent = y * self.towerGroup.slowPercentModifier
            x = self.initSlowTime * self.upgradeDict['SlowTime'][self.level - 1]
            y = self.initSlowTime * self.upgradeDict['SlowTime'][self.level]
            self.slowTime = x * self.towerGroup.slowTimeModifier
            self.nextSlowTime = y * self.towerGroup.slowTimeModifier
        elif self.type == 'Gravity':
            x = self.initStunTime * self.upgradeDict['StunTime'][self.level - 1]
            y = self.initStunTime * self.upgradeDict['StunTime'][self.level]
            self.stunTime = x * self.towerGroup.stunTimeModifier
            self.nextStunTime = y * self.towerGroup.stunTimeModifier
            x = self.initStunChance * self.upgradeDict['StunChance'][self.level - 1]
            y = self.initStunChance * self.upgradeDict['StunChance'][self.level]
            self.stunChance = x * self.towerGroup.stunChanceModifier
            self.nextStunChance = y * self.towerGroup.stunChanceModifier
            x = self.initBlackHoleChance * self.upgradeDict['BlackHoleChance'][self.level - 1]
            y = self.initBlackHoleChance * self.upgradeDict['BlackHoleChance'][self.level]
            self.blackHoleChance = x * self.towerGroup.blackHoleChanceModifier
            self.nextBlackHoleChance = y * self.towerGroup.blackHoleChanceModifier

    def setMenuData(self):
        self.menuData = {}
        for item in self.menu:
            if item == 'Dmg':
                self.menuData['Dmg'] = [round(self.damage,1), str(int(round((self.towerGroup.damageModifier - 1) * 100))) + '%', str(round(self.nextDamage,1))]
            elif item == 'Rng':
                self.menuData['Rng'] = [int(self.range), str(int(round((self.towerGroup.rangeModifier - 1) * 100))) + '%', str(int(self.nextRange))]
            elif item == 'Rld':
                self.menuData['Rld'] = [round(self.reload,1), str(int(round((self.towerGroup.reloadModifier - 1) * -100))) + '%', str(round(self.nextReload,1))]
            elif item == 'Push':
                self.menuData['Push'] = [round(self.push, 1), str(int(round((self.towerGroup.pushModifier - 1) * 100))) + '%', str(round(self.nextPush, 1))]
            elif item == 'Slow%':
                self.menuData['Slow%'] = [str(int(self.slowpercent))+'%', str(int(round((self.towerGroup.slowPercentModifier-1) * 100))) + '%', str(round(self.nextSlowPercent,1))+'%']
            elif item == 'SlowTm':
                self.menuData['SlowTm'] = [str(round(self.slowTime,1))+'s', str(int(round((self.towerGroup.slowTimeModifier-1) * 100))) + '%', str(round(self.nextSlowTime,1))+'s']
            elif item == 'StunChance':
                self.menuData['StunChance'] = [str(round(self.stunChance, 1))+'%', str(int(round((self.towerGroup.stunChanceModifier-1) * 100))) + '%', str(round(self.nextStunChance,1))+'%']
            elif item == 'StunTm':
                self.menuData['StunTm'] = [str(int(self.stunTime)) + 's', str(int(round((self.towerGroup.stunTimeModifier-1) * 100))) + '%', str(round(self.nextStunTime,1))+'s']
            elif item == 'BurnDmg':
                self.menuData['BurnDmg'] = [round(self.burn,1), str(int(round((self.towerGroup.burnModifier - 1) * 100))) + '%', str(round(self.nextBurn,1))]
            elif item == 'BalckHoleChance':
                self.menuData['BlackHoleChance'] = [str(round(self.blackHoleChance, 1))+'%', str(int((self.towerGroup.blackHoleChanceModifier-1) * 100)) + '%', str(round(self.nextblackHoleChance,1))+'%']
            elif item == 'GrpDmg':
                self.menuData['GrpDmg'] = [str(int(self.towerGroup.damageBonus*100))+"%", str(int(round((self.towerGroup.damageModifier-1) * 100))) + '%', str(int(self.towerGroup.nextDamageBonus*100))+"%"]
            elif item == 'GrpRld':
                self.menuData['GrpRld'] = [str(int(self.towerGroup.reloadBonus*-100))+"%", str(int(round((self.towerGroup.reloadModifier - 1.0) * -100))) + '%', str(int(self.towerGroup.nextReloadBonus*-100))+"%"]
            elif item == 'GrpRng':
                self.menuData['GrpRng'] = [str(int(self.towerGroup.rangeBonus*100))+"%", str(int(round((self.towerGroup.rangeModifier - 1.0) * 100))) + '%', str(int(self.towerGroup.nextRangeBonus*100))+"%"]
            elif item == 'GrpPush':
                self.menuData['GrpPush'] = [str(int(self.towerGroup.pushBonus*100))+"%", str(int(round((self.towerGroup.pushModifier - 1.0) * 100))) + '%', str(int(self.towerGroup.nextPushBonus*100))+"%"]
            elif item == 'GrpSlowTm':
                self.menuData['GrpSlowTm'] = [str(int(self.towerGroup.slowtimeBonus*100))+"s", str(int(round((self.towerGroup.slowTimeModifier - 1.0) * 100))) + '%', str(int(self.towerGroup.nextSlowtimeBonus*100))+"s"]
            elif item == 'GrpSlow%':
                self.menuData['GrpSlow%'] = [str(int(self.towerGroup.slowpercentBonus*100))+"%", str(int(round((self.towerGroup.slowPercentModifier - 1.0) * 100))) + '%', str(int(self.towerGroup.nextSlowpercentBonus*100))+"%"]
            elif item == 'GrpStunChance':
                sele.menuData['GrpStunChance'] = [str(int(self.towerGroup.stunchanceBonus*100))+"%", str(int(round((self.towerGroup.stunChanceModifier - 1.0) * 100))) + '%', str(int(self.towerGroup.nextStunchanceBonus*100))+"%"]
            elif item == 'GrpStunTm':
                self.menuData['GrpStunTm'] = [str(int(self.towerGroup.stuntimeBonus)) + 's', str(int((self.towerGroup.stunTimeModifier-1) * 100)) + '%', str(round(self.towerGroup.nextStuntimeBonus,1))+'s']
            elif item == 'GrpBurn':
                self.menuData['GrpBurn'] = [str(int(self.towerGroup.burnBonus*100))+"%", str(int(round((self.towerGroup.burnModifier - 1.0) * 100))) + '%', str(int(self.towerGroup.nextBurnBonus*100))+"%"]
        return self.menuData

    def takeTurn(self):
        '''Maintain reload wait period and call target() once period is over
        Frametime: the amount of time elapsed per frame'''
        if self.totalUpgradeTime == 0:
            if self.targetedEnemy:
                if self.upgradePath != 'FireDamage':
                    if not self.turret.anim.have_properties_to_animate(self.turret_rot):
                        self.moveTurret(self.targetedEnemy)
            if self.recharging:
                self.recharge()
            self.targetTimer -= Player.player.frametime
            ##if the rest period is up then shoot again
            if self.targetTimer <= 0:
                self.target()


    def target(self):
        '''Create a sorted list of enemies based on distance from the tower. If enemy is within tower range then hit enemy'''
        if self.targetedEnemy and self.targetedEnemy.isAlive:
            if Utilities.in_range(self, self.targetedEnemy):
                Shot.Shot(self, self.targetedEnemy)
                self.targetTimer = self.towerGroup.targetTimer = self.reload
                if self.upgradePath == 'LifeDamage':
                    self.recharge()
            else:
                self.targetedEnemy = None
        elif self.attacktype == 'single' and not self.leader:
            sortedlist = reversed(sorted(Map.mapvar.enemycontainer.children, key=operator.attrgetter("weightedcurnode")))
            for enemy in sortedlist:
                if Utilities.in_range(self, enemy):
                    if enemy.isair and self.attackair:
                        if self.type == 'Life' or self.upgradePath == 'WindDamage':
                            self.targetedEnemy = enemy
                            self.moveTurret(enemy)
                        self.shotcount += 1
                        Shot.Shot(self, enemy)
                    if not enemy.isair and self.attackground:
                        self.targetedEnemy = enemy
                        self.moveTurret(enemy)
                        self.shotcount += 1
                        Shot.Shot(self, enemy)
                    if self.shotcount > 0:
                        self.targetTimer = self.towerGroup.targetTimer = self.reload
                        if self.upgradePath == 'LifeDamage':
                            self.recharge()
                if self.shotcount >= self.allowedshots:
                    return
        elif self.attacktype == 'multi' and not self.leader:
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
        if self.type == "Ice":
            if enemy.burntime > 0:
                enemy.burtime = 0
                enemy.workBurnTimer()
            enemy.color = [0, 0, 1, 1]
            enemy.slowtime = self.slowTime
            enemy.slowpercent = 100 - self.slowPercent
            if self.upgradePath == 'IceDamage':
                #random = random.randint(0,100)
                stun = 1
                if stun < self.stunChance:
                    enemy.stuntime = self.stunTime
                    enemy.stunimage.source = "towerimgs/Ice/icon.png"
                    if not enemy.stunimage.parent:
                        enemy.add_widget(enemy.stunimage)
                    if enemy.anim:
                        enemy.anim.cancel_all(enemy)

            enemy.health -= max(self.damage - enemy.armor, 0)
            enemy.checkHealth()

        elif self.type == 'Gravity':
            stun = True if random.randint(0, 100) > 100 - self.stunChance else False
            if stun == True:
                enemy.stuntime = self.stunTime
                if enemy.anim:
                    enemy.anim.cancel_all(enemy)
                enemy.stunimage.source = "enemyimgs/stunned.png"
                if not enemy.stunimage.parent:
                    enemy.add_widget(enemy.stunimage)
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

    def recharge(self):
        if self.targetTimer == self.reload:
            self.recharging = True
            self.turret.source = os.path.join("towerimgs", self.type, self.reloadFrameList[0])
        elif self.targetTimer <  self.reload and self.targetTimer > self.reload * .6:
            self.turret.source = os.path.join("towerimgs", self.type, self.reloadFrameList[1])
        elif self.targetTimer <  self.reload and self.targetTimer > self.reload * .3:
            self.turret.source = os.path.join("towerimgs", self.type, self.reloadFrameList[2])
        elif self.targetTimer <  self.reload and self.targetTimer > self.reload * .05:
            self.turret.source = os.path.join("towerimgs", self.type, self.reloadFrameList[3])
            self.recharging = False


    def moveTurret(self, enemy):
        if not self.leader and self.upgradePath != 'FireDamage':
            if self.type == 'Wind' and self.upgradePath == None:
                return
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
        elif self.type == 'Gravity':
            with self.canvas:
                Color(0, 0, 0, 1)
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
            self.turret.anim = None
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
    initburn = 10
    initrange = 100
    initreload = .4
    attacks = "Ground"
    imagestr = os.path.join('towerimgs', 'Fire', 'icon.png')
    upgradeDict = {'Damage': [1, 1.2, 1.3, 1.4, 1.5, 1.6, 2], 'Range': [1, 1, 3, 1, 1, 1.5, 1.5],
     'Reload': [1, 1, 8, 1, 1, .8, .8], 'Burn':[0,0,1,0,0,1,1.2,1.4,1.6,1.8,2],'Cost': [0, 5, (50, 1), 150, 250, (500, 1), 'NA']}
    upgradeName = 'Volcano'
    upgradeDescription = 'Shoots fireballs at the enemy dealing high damage to the target and low damage to surrounding enemies.'
    'Volcano effects cancel out the Ice and Blizzard effects on enemies and vice-versa. Does not attack Airborn enemies. Increases range and damage, and increases reload time.'
    upgradeStats = ['Burn: damage dealt to surrounding enemies each second for 5 seconds after impact. Does not impact Airborn enemies.']

    def __init__(self, pos, **kwargs):
        self.rangecalc = 3.3
        Tower.__init__(self, pos, **kwargs)
        self.pos = pos
        self.cost = FireTower.cost
        self.initRange = self.range = FireTower.initrange
        self.initDamage = self.damage = FireTower.initdamage
        self.initReload = self.reload = FireTower.initreload
        self.initBurn = self.burn = FireTower.initburn
        self.push = 0
        self.type = FireTower.type
        self.attacktype = 'single'
        self.attackair = False
        self.active = True
        self.shotimage = "flame.png"
        self.shotDuration = .25
        self.hasTurret = True
        self.loadTurret()
        self.upgradeDict = FireTower.upgradeDict
        self.menu = ['Dmg', 'Rng', 'Rld']
        self.dmgMenu = ['Dmg', 'Rng', 'Rld', 'BurnDmg']
        self.leaderMenu = ['GrpDmg', 'GrpRng', 'GrpRld','GrpBurn']
        self.setTowerData()




class LifeTower(Tower):
    type = "Life"
    cost = 15
    initrange = 150
    initdamage = 10
    initreload = 1.0
    initpush = 5
    attacks = "Both"
    imagestr = os.path.join('towerimgs', 'Life', 'icon.png')
    upgradeDict = {'Damage': [1, 1.1, 8, 1.3, 1.4, 1.5, 2], 'Range': [1, 1, 3, 1, 1, 1.5, 1],
     'Reload': [1, 1, 3, 1, 1, .4, .4], 'Push':[0,0,1,0,0,1, 1.1,1.2,1.3,1.4,1.5],'Cost': [0, 5, (50, 1), 150, 250, (500, 1), 'NA']}
    upgradeName = 'Sniper'
    upgradeDescription = 'Shoots powerful shots at a single enemy, dealing massive damage. The enemy is knocked backwards due to the velocity of the shot'
    'Effects all enemies, although nearby enemies cannot be targeted. Increases damage and range, and increases reload time.'
    upgradeStats = ['Push: knockback of the enemy when hit by a shot']

    def __init__(self, pos, **kwargs):
        Tower.__init__(self, pos, **kwargs)
        self.pos = pos
        self.cost = LifeTower.cost
        self.initRange = self.range = LifeTower.initrange
        self.initDamage = self.damage = LifeTower.initdamage
        self.initReload = self.reload = LifeTower.initreload
        self.initPush = self.push = LifeTower.initpush
        self.rangeExclusion = 0
        self.type = LifeTower.type
        self.attacktype = 'single'
        self.attackair = True
        self.shotimage = "shot.png"
        self.shotDuration = .2
        self.hasTurret = True
        self.active = True
        self.loadTurret()
        self.reloadFrameList = ["reload_frame1.png","reload_frame2.png", "reload_frame3.png", "turret2.png" ]
        self.upgradeDict = LifeTower.upgradeDict
        self.menu = ['Dmg', 'Rng', 'Rld']
        self.dmgMenu = ['Dmg', 'Rng', 'Rld', 'Push']
        self.leaderMenu = ['GrpDmg', 'GrpRng', 'GrpRld']
        self.setTowerData()


class GravityTower(Tower):
    type = "Gravity"
    cost = 15
    initrange = 60
    initdamage = 30
    initreload = 2.5
    initstuntime = 2
    initstunchance = 10
    initpush = -10
    initblackholechance = 10
    attacks = "Ground"
    imagestr = os.path.join('towerimgs', 'Gravity', 'icon.png')
    upgradeDict = {'Damage': [1, 1.2, 1.4, 1.6, 1.8, 2.0, 0], 'StunChance': [1, 1.1, 1.5, 2.0, 2.5, 3, 4],
     'Reload': [1, 1, 1, 1, 1, 1, 1], 'StunTime': [1, 1, 1.2, 1.3, 1.4, 1.5, 2], "BlackHoleChance": [0,0,0,0,0,1,1.1,1.2,1.3,1.4,1.5],
     'Cost': [0, 5, (50,1), 150, 250, (500, 1), 'NA']}
    upgradeName = "Black Hole"
    upgradeDescription = "Deals increased damage to enemies. At times the tower may form a black hole, dealing massive damage and teleporting enemies to a random square on the map."
    "Does not attack Airborn enemies. Ignores the effects of armor, and so it is especially effective against Strong and Splinter. Increases damage."
    upgradeStats = ['Black Hole Chance: The percent chance that a Black Hole will occur during a shot.']

    def __init__(self, pos, **kwargs):
        Tower.__init__(self, pos, **kwargs)
        self.pos = pos
        self.cost = GravityTower.cost
        self.initRange = self.range = GravityTower.initrange
        self.initDamage = self.damage = GravityTower.initdamage
        self.initReload = self.reload = GravityTower.initreload
        self.initStunTime = self.stunTime = GravityTower.initstuntime
        self.initStunChance = self.stunChance = GravityTower.initstunchance
        self.initPush = self.push = GravityTower.initpush
        self.initBlackHoleChance = self.blackHoleChance = GravityTower.initblackholechance
        self.type = GravityTower.type
        self.attackair = False
        self.attacktype = "multi"
        self.active = False
        self.allowedshots = 999
        self.hasTurret = True
        self.animating = False
        self.loadTurret()
        self.upgradeDict = GravityTower.upgradeDict
        self.menu = ['Dmg', 'StunChance', 'StunTm']
        self.dmgMenu = ['Dmg', 'StunChance', 'StunTm','BlackHoleChance']
        self.leaderMenu = ['GrpDmg', 'GrpStunChance', 'GrpStunTm']
        self.setTowerData()

class IceTower(Tower):
    type = "Ice"
    cost = 15
    initrange = 60
    initdamage = 1
    initreload = 2
    initslowtime = 3
    initslowpercent = 15
    initstunpercent = 10
    initstuntime = 3
    attacks = "Both"
    imagestr = os.path.join('towerimgs', 'Ice', 'icon.png')
    upgradeDict = {'SlowPercent': [1, 1.1, 1.2, 1.3, 1.4, 1.5, 1.5], 'Damage': [1, 1, 1, 1, 1, 1, 1],
     'SlowTime': [1, 1.1, 1.2, 1.3, 1.4, 1.5, 1.5], 'StunChance':[0,0,0,0,0,1,1.2,1.4,1.6,1.8,2], 'StunTime':[0,0,0,0,0,1,1.1,1.2,1.3,1.4,1.5],'Cost': [0, 5, (50,1), 150, 250, (500, 1), 'NA'], }
    upgradeName = "Blizzard"
    upgradeDescription = "Randomly freezes units in place for a period of time. The Blizzard effect cancels the Volcano effect on enemies and vice-versa."
    "Works on all enemies."
    upgradeStats = ['Stun Chance: The percent chance an enemy will be frozen in place when hit.', 'Stun Time: The amount of time in seconds an enemy remains frozen.']

    def __init__(self, pos, **kwargs):
        Tower.__init__(self, pos, **kwargs)
        self.pos = pos
        self.cost = IceTower.cost
        self.initRange = self.range = IceTower.initrange
        self.initDamage = self.damage = IceTower.initdamage
        self.initReload = self.reload = IceTower.initreload
        self.initSlowTime = self.slowTime = IceTower.initslowtime
        self.initSlowPercent = self.slowpercent = IceTower.initslowpercent
        self.initStunPercent = self.stunChance = IceTower.initstunpercent
        self.initStunTime = self.stunTime = IceTower.initstuntime
        self.push = 0
        self.type = IceTower.type
        self.attackair = True
        self.attacktype = 'multi'
        self.active = False
        self.allowedshots = 999
        self.hasTurret = False
        self.upgradeDict = IceTower.upgradeDict
        self.menu = ['Dmg', 'Slow%', 'SlowTm']
        self.dmgMenu = ['Dmg', 'Slow%', 'StunTm', 'StunChance']
        self.leaderMenu = ['GrpDmg', 'GrpSlow%', 'GrpSlowTm']
        self.setTowerData()


class WindTower(Tower):
    type = "Wind"
    cost = 15
    initrange = 300
    initdamage = 40
    initreload = 4
    initpush = 25
    attacks = 'Air'
    imagestr = os.path.join('towerimgs', 'Wind', 'icon.png')
    upgradeDict = {'Push': [1, 1.1, 1.2, 1.4, 1.5, 2, 2], 'Range': [1, 1, 1, 1.1, 1.1, 1.5, 1.5],
                   'Reload': [1, 1, 1, .9, .9, .7, .7], 'Cost': [0, 5, (50,1), 150, 250, (500, 1), 'NA'],
                   'Damage': [1, 1, 1, 1, 1, 1, 1]}
    upgradeName = "Tornado"
    upgradeDescription = "Targets the enemies closest to the Base with a wider and more powerful gust of wind."
    "Increased damage. Effects only Airborn units."
    upgradeStats = ['']


    def __init__(self, pos, **kwargs):
        Tower.__init__(self, pos, **kwargs)
        self.pos = pos
        self.cost = WindTower.cost
        self.initRange = self.range = WindTower.initrange
        self.initDamage = self.damage = WindTower.initdamage
        self.initReload = self.reload = WindTower.initreload
        self.initPush = self.push = WindTower.initpush
        self.type = WindTower.type
        self.attackair = True
        self.attackground = False
        self.attacktype = 'single'
        self.shotimage = "shot.png"
        self.hasTurret = True
        self.loadTurret()
        if self.towerGroup.active:
            self.turret.source = os.path.join('towerimgs', self.type, "turret.gif")
        self.active = False
        self.allowedshots = 1

        self.upgradeDict = WindTower.upgradeDict
        self.menu = ['Push', 'Dmg','Rng', 'Rld']
        self.dmgMenu = ['Push', 'Dmg','Rng', 'Rld']
        self.leaderMenu = ['GrpPush','GrpDmg', 'GrpRng','GrpRld']
        self.setTowerData()

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
