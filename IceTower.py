import os
import random
from kivy.uix.image import Image
import Towers
import Player
import Map


class IceTower(Towers.Tower):
    type = "Ice"
    cost = 15
    initrange = 2
    initdamage = .5
    initreload = .25
    initslowtime = 3
    initslowpercent = 35
    initstunchance = 7
    initstuntime = 3
    attacks = "Both"
    imagestr = os.path.join('towerimgs', 'Ice', 'icon.png')
    upgradeDict = {'SlowPercent': [1, 1.1, 1.2, 1.3, 1.4, 1.6, 1.8, 2, 2.1, 2.3, 2.5, 'NA'], 'Damage': [1, 1.5, 2, 2.5, 3, 3.5, 10, 15, 20, 25, 30, 'NA'],
     'SlowTime': [1, 1.1, 1.2, 1.3, 1.4, 2, 2.2, 2.4, 2.6, 2.8, 3, 'NA'], 'StunChance':[0,0,0,0,0,1,1.5,2,2.5,3,3.5, 'NA'], 'StunTime':[0,0,0,0,0,1,1.2,1.4,1.6,1.8,2, 'NA'],
                'Cost': [0, 5, 50, 100, 175, (250, 1), 400, 500, 600, 800, 1000, 'NA'], }
    upgradeName = "Blizzard"
    upgradeDescription = "Randomly freezes units in place for a period of time. The Blizzard effect cancels the Volcano effect on enemies and vice-versa."
    "Works on all enemies."
    upgradeStats = ['Stun Chance: The percent chance an enemy will be frozen in place when hit.', 'Stun Time: The amount of time in seconds an enemy remains frozen.']

    def __init__(self, pos, **kwargs):
        Towers.Tower.__init__(self, pos, **kwargs)
        self.pos = pos
        self.cost = IceTower.cost
        self.initRange = self.range = IceTower.initrange * Map.mapvar.squsize
        self.initDamage = self.damage = IceTower.initdamage
        self.initReload = self.reload = IceTower.initreload
        self.initSlowTime = self.slowTime = IceTower.initslowtime
        self.initSlowPercent = self.slowPercent = IceTower.initslowpercent
        self.initStunChance = self.stunChance = IceTower.initstunchance
        self.initStunTime = self.stunTime = IceTower.initstuntime
        self.push = 0
        self.type = IceTower.type
        self.attackair = True
        self.attacktype = 'multi'
        self.active = False
        self.allowedshots = 999
        self.hasTurret = False
        self.turretRotates = False
        self.upgradeDict = IceTower.upgradeDict
        self.menu = [('Damage', 1, ' DPH', 'Damage'), ('SlowPercent', 0, '%', 'Slow Percent'), ('SlowTime', 1, 's', 'Slow Time')]
        self.dmgMenu = [('Damage', 1, ' DPH', 'Damage'), ('SlowPercent', 0, '%', 'Slow Percent'), ('SlowTime', 1, 's', 'Slow Time'), ('StunChance', 0, '%', 'Stun Chance')]
        self.leaderMenu = [('Damage', 0, '%', 'Damage'), ('SlowPercent', 0, '%', 'Slow Percent'), ('SlowTime', 0, '%', 'Slow Time')]
        #self.setTowerData()

    def hitEnemy(self, enemy = None):
        '''Reduces enemy health by damage - armor'''
        if enemy.burntime > 0:
            enemy.burtime = 0
            enemy.workBurnTimer()
        enemy.color = [0, 0, 1, 1]
        if enemy.slowtime == 0:
            enemy.updateSlow = True
        enemy.slowtime = self.slowTime
        enemy.slowpercent = 100 - self.slowPercent
        if self.upgradePath == 'IceDamage':
            stun = random.randint(0,(100/self.reload))
            if stun <= self.stunChance:
                enemy.stuntime = self.stunTime
                enemy.stunimage.source = "towerimgs/Ice/icon.png"
                if not enemy.stunimage.parent:
                    enemy.add_widget(enemy.stunimage)
                if enemy.anim:
                    enemy.anim.cancel_all(enemy)
        Player.player.analytics.gameDamage += self.damage

        enemy.armor -= self.damage if enemy.armor > 0 else 0
        enemy.health -= max(self.damage - enemy.armor, 0)
        enemy.checkHealth()
        self.shotcount += 1

    def setupUpgradePath(self):
        if self.leader:
            self.menu = self.leaderMenu
            self.loadTurret()
        else:
            self.menu = self.dmgMenu
            self.loadTurret()

    def loadTurret(self):
        if self.upgradePath == 'IceDamage':
            self.turret = Image(source = 'towerimgs/Ice/turret2.gif', size = (Map.mapvar.squsize * .65,Map.mapvar.squsize * .65))
            self.turret.center = (self.center[0]-1, self.center[1]+1)
        else:
            self.turret = Image(source = 'towerimgs/leaderturret.png', size = (Map.mapvar.squsize, Map.mapvar.squsize))
            self.turret.center = self.center
        self.add_widget(self.turret)

    def updateStats(self):
        if not self.leader:
            self.damage = self.stats['Damage'][0]
            self.slowPercent = self.stats['SlowPercent'][0]
            self.slowTime = self.stats['SlowTime'][0]
            if self.upgradePath == 'IceDamage':
                self.stunChance = self.stats['StunChance'][0]