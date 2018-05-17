import os
import random
from kivy.animation import Animation
from kivy.uix.image import Image
from kivy.graphics import *

import Towers
import Map
import Player
import __main__

class GravityTower(Towers.Tower):
    type = "Gravity"
    cost = 15
    initrange = 2
    initdamage = 30
    initreload = 2.8
    initstuntime = 2
    initstunchance = 6
    initpush = -10
    initblackholechance = 10
    attacks = "Ground"
    imagestr = os.path.join('towerimgs', 'Gravity', 'icon.png')
    upgradeDict = {'Damage': [1, 1.2, 1.4, 1.5, 1.7, 3.0, 3.4,3.8,4.2,4.6,5, 'NA'], 'StunChance': [1, 1.1, 1.2, 1.4, 1.6, 2, 2.3, 2.6, 2.9, 3.2, 3.5, 'NA'],
     'Reload': [1, 1, 1, 1, 1, 1, 1,1,1,1,1,'NA'], 'StunTime': [1, 1, 1.2, 1.3, 1.4, 1.8, 2, 2.2, 2.4, 2.6, 2.8, 'NA'], "BlackHoleChance": [0,0,0,0,0,1,1.5,2,2.5,3,4, 'NA'],
     'Cost': [0, 5, 50, 100, 175, (250, 1), 400, 500, 600, 800, 1000, 'NA']}
    upgradeName = "Black Hole"
    upgradeDescription = " At times the tower may form a black hole, dealing 5x damage and stunning all enemies in range."
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
        self.menu = [('Damage', 1, ' DPH', 'Damage'), ('StunChance', 0, '%', 'Stun Chance'), ('StunTime', 1, 's', 'Stun Time')]
        self.dmgMenu = [('Damage', 1, ' DPH', 'Damage'), ('StunChance', 0, '%', 'Stun Chance'), ('StunTime', 1, 's', 'Stun Time'), ('BlackHoleChance', 0, '%', 'Black Hole Chance')]
        self.leaderMenu = [('Damage', 0, '%', 'Damage'), ('StunChance', 0, '%', 'Stun Chance'), ('StunTime', 0, '%', 'Stun Time')]
        #self.setTowerData()
        self.black_hole_list = []
        self.blackhole = Image(source='towerimgs/Gravity/blackhole.png',
                               size=(5,5), center=self.center, allow_stretch = True)
        self.black_hole_Animation = Animation(size=(__main__.app.root.squsize * 6, __main__.app.root.squsize * 6), center=self.center,
                                       duration=.4)
        self.black_hole_Animation.bind(on_complete=self.removeBlackHole)

    def removeBlackHole(self,*args):
        self.blackhole.size = (5, 5)
        self.blackhole.center = self.center
        self.remove_widget(self.blackhole)

    def black_hole(self):
        if not self.blackhole.parent:
            self.add_widget(self.blackhole)
            self.blackhole.center = self.center
            self.black_hole_Animation.start(self.blackhole)
            for enemy in self.black_hole_list:
                self.hitEnemy(enemy, dmg_modifier = 1, stun = True)


    def hitEnemy(self, enemy = None, dmg_modifier = 1, stun = False):
        Player.player.analytics.gameDamage += self.damage
        enemy.health -= self.damage * dmg_modifier
        enemy.checkHealth()
        self.shotcount += 1
        if not stun:
            s = random.randint(0, 100)
        else:
            s = 1
        if s <= self.stunChance:
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
        if self.leader:
            self.menu = self.leaderMenu
            self.loadTurret()
        else:
            self.menu = self.dmgMenu

    def closeAnimation(self, *args):
        self.animating = False

    def loadTurret(self):
        if self.leader:
            self.remove_widget(self.turret)
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

