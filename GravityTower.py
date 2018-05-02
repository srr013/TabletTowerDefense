import os
import random
from kivy.animation import Animation
from kivy.uix.image import Image
from kivy.graphics import *

import Towers
import Map
import Player

class GravityTower(Towers.Tower):
    type = "Gravity"
    cost = 15
    initrange = 2
    initdamage = 30
    initreload = 2.8
    initstuntime = 2
    initstunchance = 6
    initpush = -10
    initblackholechance = 3
    attacks = "Ground"
    imagestr = os.path.join('towerimgs', 'Gravity', 'icon.png')
    upgradeDict = {'Damage': [1, 1.2, 1.4, 1.5, 1.7, 3.0, 3.4,3.8,4.2,4.6,5, 'NA'], 'StunChance': [1, 1.1, 1.2, 1.4, 1.6, 2, 2.3, 2.6, 2.9, 3.2, 3.5, 'NA'],
     'Reload': [1, 1, 1, 1, 1, 1, 1,1,1,1,1,'NA'], 'StunTime': [1, 1, 1.2, 1.3, 1.4, 1.8, 2, 2.2, 2.4, 2.6, 2.8, 'NA'], "BlackHoleChance": [0,0,0,0,0,1,1.5,2,2.5,3,4, 'NA'],
     'Cost': [0, 5, 50, 100, 200, (350, 1), 500, 700, 800, 900, 1000, 'NA']}
    upgradeName = "Black Hole"
    upgradeDescription = " At times the tower may form a black hole, dealing 5x damage and teleporting an enemy to the start of its path."
    "Does not attack Airborn enemies. Increases damage. All Gravity attacks ignore the effects of armor, and so are especially effective against Strong and Splinter enemies. "
    upgradeStats = ['Black Hole %: The percent chance that a Black Hole will occur during a shot.']

    def __init__(self, pos, **kwargs):
        Towers.Tower.__init__(self, pos, **kwargs)
        self.pos = pos
        self.cost = GravityTower.cost
        self.initRange = self.range = GravityTower.initrange * Map.mapvar.squsize
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
        self.turretRotations = False
        self.loadTurret()
        self.upgradeDict = GravityTower.upgradeDict
        self.menu = [('Damage', 1, ' DPH'), ('StunChance', 0, '%'), ('StunTime', 1, 's')]
        self.dmgMenu = [('Damage', 1, ' DPH'), ('StunChance', 0, '%'), ('StunTime', 1, 's'), ('BlackHoleChance', 0, '%')]
        self.leaderMenu = [('Damage', 0, '%'), ('StunChance', 0, '%'), ('StunTime', 0, '%$')]
        self.setTowerData()
        self.blackhole = Image(source='towerimgs/Gravity/blackhole.png',
                               size=(5,5), center=self.center)
        self.blackholeTwo = Image(source='towerimgs/Gravity/blackhole.png',
                               size=(Map.mapvar.squsize * 1.5, Map.mapvar.squsize * 1.5))
        self.teleAnimation = Animation(size=(Map.mapvar.squsize * 1.5, Map.mapvar.squsize * 1.5), center=self.center,
                                       duration=.2)
        self.teleAnimation.bind(on_complete=self.moveEnemy)

    def teleport(self, *args):
        self.add_widget(self.blackhole)
        self.teleAnimation.start(self.blackhole)
        self.appearAnimation = Animation(size=(0, 0),
                                         center=self.teleEnemy.center, duration=.2)
        self.appearAnimation.bind(on_complete=self.removeBlackHole)

    def moveEnemy(self, *args):
        self.blackhole.size = (0,0)
        self.blackhole.center = self.center
        self.remove_widget(self.blackhole)
        self.teleEnemy.curnode = 0
        telePos = self.teleEnemy.movelist[self.teleEnemy.curnode]
        self.teleEnemy.pos = telePos
        print "teleported", self.teleEnemy.pos
        self.blackholeTwo.pos = telePos
        Map.mapvar.backgroundimg.add_widget(self.blackholeTwo)
        self.appearAnimation.start(self.blackholeTwo)
        self.teleEnemy.move()

    def removeBlackHole(self,*args):
        self.teleEnemy.teleporting = None
        Map.mapvar.backgroundimg.remove_widget(self.blackholeTwo)
        self.blackholeTwo.size = (Map.mapvar.squsize * 1.5, Map.mapvar.squsize * 1.5)
        self.blackholeTwo.center = self.center
        self.blackhole_in_progress = False

    def hitEnemy(self, enemy = None):
        Player.player.analytics.gameDamage += self.damage
        enemy.health -= self.damage
        enemy.checkHealth()
        self.shotcount += 1
        if self.upgradePath == 'GravityDamage' and not self.blackhole_in_progress:
            blackhole = random.randint(0,100)
            if blackhole <= self.blackHoleChance:
                self.blackhole_in_progress = True
                self.teleEnemy = enemy
                enemy.teleporting = self
                enemy.pushed = [enemy.center_x - self.center_x, enemy.center_y - self.center_y]
                enemy.health -= self.damage * 5
                enemy.checkHealth()
                if not enemy.isAlive:
                    self.blackhole_in_progress = False
                return
        stun = random.randint(0, 100)
        if stun <= self.stunChance:
            enemy.stuntime = self.stunTime
            if enemy.anim:
                enemy.anim.cancel_all(enemy)
            enemy.stunimage.source = "enemyimgs/stunned.png"
            if not enemy.stunimage.parent:
                enemy.add_widget(enemy.stunimage)
        dir = (enemy.center[0] - self.center[0], enemy.center[1] - self.center[1])
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


    def setupUpgradePath(self):
        print "leader?", self.leader
        if self.leader:
            self.menu = self.leaderMenu
            self.loadTurret()
        else:
            self.menu = self.dmgMenu

    def closeAnimation(self, *args):
        self.animating = False

    def loadTurret(self):
        if self.leader:
            self.turret.size = (0,0)
            self.leaderturret = Image(source="towerimgs/leaderturret.png",
                                      size=(Map.mapvar.squsize, Map.mapvar.squsize), center=self.center)
            self.add_widget(self.leaderturret)
            self.leaderturret.center = self.center
        else:
            self.turret = Image(source=os.path.join('towerimgs', 'Gravity', "attack.png"),
                                    size=(Map.mapvar.squsize * 1.5, Map.mapvar.squsize * 1.5),
                                    pos=(self.center[0] - Map.mapvar.squsize * .74,
                                         self.center[1] - Map.mapvar.squsize * .74))
            self.add_widget(self.turret)
            self.animation = None
            self.closeanimation = Animation(size=(Map.mapvar.squsize * 1.5, Map.mapvar.squsize * 1.5),
                                            pos=(self.center[0] - Map.mapvar.squsize * .74,
                                                 self.center[1] - Map.mapvar.squsize * .74),
                                            duration=.3)
            self.closeanimation.bind(on_complete=self.closeAnimation)

    def updateStats(self):
        if not self.leader:
            self.damage = self.stats['Damage'][0]
            self.stunChance = self.stats['StunChance'][0]
            self.stunTime = self.stats['StunTime'][0]
            if self.upgradePath == 'GravityDamage':
                self.blackHoleChance = self.stats['BlackHoleChance'][0]
