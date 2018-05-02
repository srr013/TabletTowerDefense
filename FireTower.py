import os
from kivy.graphics import *

from Towers import Tower
import Shot
import Map

class FireTower(Tower):
    type = "Fire"
    cost = 15
    initdamage = 10
    initburn = 10
    initrange = 3.3
    initreload = .4
    attacks = "Ground"
    imagestr = os.path.join('towerimgs', 'Fire', 'icon.png')
    upgradeDict = {'Damage': [1, 1.2, 1.4, 1.6, 1.8, 7, 9, 11, 13, 15, 17, 'NA'], 'Range': [1, 1, 1, 1, 1, 2, 2.2, 2.4, 2.6, 2.8, 3, 'NA'],
     'Reload': [1, 1, 1, 1, 1, 8, 7.6, 7.2, 6.8, 6.4, 6, 'NA'], 'BurnDamage':[0,0,0,0,0,1,1.2,1.4,1.6,1.8,2, 'NA'],'Cost': [0, 5, 50, 100, 200, (350, 1), 500, 700, 800, 900, 1000, 'NA']}
    upgradeName = 'Volcano'
    upgradeDescription = "Shoots fireballs at the enemy dealing high damage to the target and low damage to surrounding enemies." \
                         "The volcano tower must guess where it's enemy will be, and has a tendency to miss."
    'Volcano effects cancel out the Ice and Blizzard effects on enemies and vice-versa. Does not attack Airborn enemies. Increases range and damage, and increases reload time.'
    upgradeStats = ['Burn: damage dealt to surrounding enemies each second for 5 seconds after impact. Does not impact Airborn enemies.']

    def __init__(self, pos, **kwargs):
        self.rangecalc = 3.3
        Tower.__init__(self, pos, **kwargs)
        self.pos = pos
        self.cost = FireTower.cost
        self.initRange = self.range = FireTower.initrange * Map.mapvar.squsize
        self.initDamage = self.damage = FireTower.initdamage
        self.initReload = self.reload = FireTower.initreload
        self.initBurnDamage = self.burn = FireTower.initburn
        self.push = 0
        self.type = FireTower.type
        self.attacktype = 'single'
        self.attackair = False
        self.active = True
        self.shotimage = "flame.png"
        self.shotDuration = .25
        self.hasTurret = True
        self.turretRotates = True
        self.loadTurret()
        self.upgradeDict = FireTower.upgradeDict
        self.menu = [('Damage', 1, ' DPH'), ('Range', 0, 'px'), ('Reload', 1,'s')]
        self.dmgMenu = [('Damage', 1, ' DPH'), ('Range', 0, 'px'), ('Reload', 1, 's'), ('BurnDamage', 1, ' DPS')]
        self.leaderMenu = [('Damage', 0, '%'),('Range', 0, '%'),('Reload', 0, '%'),('BurnDamage', 0, '%')]
        self.setTowerData()

    def hitEnemy(self, enemy):
        self.targetedEnemy = enemy
        self.shotcount += 1
        if self.turretRotates:
            self.moveTurret(enemy)
        Shot.Shot(self, enemy)
        self.targetTimer = self.towerGroup.targetTimer = self.reload

    def setupUpgradePath(self):
        if self.leader:
            self.turretRotates = False
            self.menu = self.leaderMenu
            self.loadTurret()
        else:
            self.menu = self.dmgMenu
            self.turretRotates = False
            self.turret.source = os.path.join("towerimgs", self.type, "turret2.gif")
            self.turret_rot.angle = 0
            self.shotimage = "shot2.png"
            self.shotDuration = 1

    def updateStats(self):
        if not self.leader:
            self.damage = self.stats['Damage'][0]
            self.reload = self.stats['Reload'][0]
            self.range = self.stats['Range'][0]
            if self.upgradePath == 'FireDamage':
                self.burn = self.stats['BurnDamage'][0]
