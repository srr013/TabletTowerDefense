import os
from kivy.graphics import *
from kivy.uix.image import Image
import Towers
import Shot
import Map

class WindTower(Towers.Tower):
    type = "Wind"
    cost = 15
    initrange = 10
    initdamage = 40
    initreload = 4
    initpush = 25
    attacks = 'Air'
    imagestr = os.path.join('towerimgs', 'Wind', 'icon.png')
    upgradeDict = {'Push': [1, 1.1, 1.2, 1.4, 1.5, 0, 0,0,0,0,0,'NA'], 'Range': [1, 1, 1 , 1.1, 1.2, .25, .3, .35, .4, .45, .5, 'NA'],
                   'Reload': [1, 1, 1, .9, .9, 0, 0, 0, 0, 0, 0, 'NA'], 'Cost': [0, 5, 50, 100, 200, (350, 1), 500, 700, 800, 900, 1000, 'NA'],
                   'Damage': [1, 1, 1, 1, 1, .4, .5, .6, .7, .8, .9, 'NA']}
    upgradeName = "Lightning"
    upgradeDescription = "Targets nearyby enemies with a stream of electricity that deals a constant high damage. Targets up to 5 Airborn units in range."
    "Reduced range, but a large increase to damage per second. Effects only Airborn units."
    upgradeStats = ['']


    def __init__(self, pos, **kwargs):
        Towers.Tower.__init__(self, pos, **kwargs)
        self.pos = pos
        self.cost = WindTower.cost
        self.initRange = self.range = WindTower.initrange * Map.mapvar.squsize
        self.initDamage = self.damage = WindTower.initdamage
        self.initReload = self.reload = WindTower.initreload
        self.initPush = self.push = WindTower.initpush
        self.type = WindTower.type
        self.attackair = True
        self.attackground = False
        self.attacktype = 'single'
        self.shotimage = "shot.png"
        self.hasTurret = True
        self.turretRotates = False
        self.loadTurret()
        if self.towerGroup.active:
            self.turret.source = os.path.join('towerimgs', self.type, "turret.gif")
            self.turret.size = (Map.mapvar.squsize * .65, Map.mapvar.squsize * .65)
            self.turret.center = self.center
        self.active = False
        self.allowedshots = 1

        self.upgradeDict = WindTower.upgradeDict
        self.menu = [('Push', 0, 'px'),('Damage', 1, ' DPH'), ('Range', 0, 'px'), ('Reload', 1, 's')]
        self.dmgMenu = [('Damage', 1, ' DPS'), ('Range', 0, 'px'), ('Reload', 1, 's')]
        self.leaderMenu = [('Push', 0, 'px'),('Damage', 0, '%'), ('Range', 0, '%'), ('Reload', 0, '%')]
        self.setTowerData()

    def hitEnemy(self, enemy):
        self.shotcount += 1
        Shot.Shot(self, enemy)
        self.targetTimer = self.towerGroup.targetTimer = self.reload

    def setupUpgradePath(self):
        if self.leader:
            self.menu = self.leaderMenu
            self.loadTurret()
        else:
            self.allowedshots = 5
            self.menu = self.dmgMenu
            self.turret.source = os.path.join("towerimgs", self.type, "turret2.gif")
            self.turret.size = (Map.mapvar.squsize*.62,Map.mapvar.squsize*.62)
            self.turret.center = self.center

    def loadTurret(self):
        if self.leader:
            if self.hasTurret:
                self.remove_widget(self.turret)
                self.hasTurret = False
            self.leaderturret = Image(source = "towerimgs/leaderturret.png", allow_stretch = True, size = (Map.mapvar.squsize, Map.mapvar.squsize))
            self.leaderturret.center = self.center
            self.add_widget(self.leaderturret)
        else:
            self.turret = Image(source = os.path.join('towerimgs', self.type, 'turret.png'), allow_stretch = True, size = (Map.mapvar.squsize, Map.mapvar.squsize))
            self.turret.center = self.center
            self.add_widget(self.turret)

    def updateStats(self):
        if not self.leader:
            self.damage = self.stats['Damage'][0]
            self.reload = self.stats['Reload'][0]
            self.range = self.stats['Range'][0]
            if self.upgradePath != 'WindDamage':
                self.push = self.stats['Push'][0]

