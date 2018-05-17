import os
from kivy.graphics import *
from kivy.uix.image import Image
import Towers
import Shot
import Map
import Player
import __main__

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
                   'Reload': [1, 1, 1, .9, .9, 0, 0, 0, 0, 0, 0, 'NA'], 'Cost': [0, 5, 50, 100, 175, (250, 1), 400, 500, 600, 800, 1000, 'NA'],
                   'Damage': [1, 1, 1, 1, 1, .4, .5, .6, .7, .8, .9, 'NA']}
    upgradeName = "Lightning"
    upgradeDescription = "Targets nearyby enemies with a stream of electricity that deals a constant high damage. Targets up to 5 Airborn units in range."
    "Reduced range, but a large increase to damage per second. Effects only Airborn units."
    upgradeStats = ['']


    def __init__(self, pos, **kwargs):
        Towers.Tower.__init__(self, pos, **kwargs)
        self.pos = pos
        self.cost = WindTower.cost
        self.squsize = __main__.app.root.squsize
        self.initRange = self.range = WindTower.initrange * self.squsize
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
        # if self.towerGroup.active:
        #     self.turret.source = os.path.join('towerimgs', self.type, "turret.gif")
        #     self.turret.size = (self.squsize * .65, self.squsize * .65)
        #     self.turret.center = self.center
        self.active = False
        self.allowedshots = 1

        self.upgradeDict = WindTower.upgradeDict
        self.menu = [('Push', 0, 'px', 'Push'),('Damage', 1, ' DPH', 'Damage'), ('Range', 0, 'px', 'Range'), ('Reload', 1, 's', 'Reload')]
        self.dmgMenu = [('Damage', 1, ' DPS', 'Damage'), ('Range', 0, 'px', 'Range'), ('Reload', 1, 's', 'Reload')]
        self.leaderMenu = [('Push', 0, 'px', 'Push'),('Damage', 0, '%', 'Damage'), ('Range', 0, '%', 'Range'), ('Reload', 0, '%', 'Reload')]
        #self.setTowerData()

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
            self.turret.size = (self.squsize*.62,self.squsize*.62)
            self.turret.center = self.center

    def loadTurret(self):
        if self.leader:
            if self.hasTurret:
                self.remove_widget(self.turret)
                self.hasTurret = False
            self.leaderturret = Image(source = "towerimgs/leaderturret.png", allow_stretch = True, size = (self.squsize, self.squsize))
            self.leaderturret.center = self.center
            self.add_widget(self.leaderturret)
        else:
            self.turret = Image(source = os.path.join('towerimgs', self.type, 'turret.png'), allow_stretch = True, size = (self.squsize, self.squsize))
            self.turret.center = self.center
            self.add_widget(self.turret)

    def updateStats(self):
        if not self.leader:
            self.damage = self.stats['Damage'][0]
            self.reload = self.stats['Reload'][0]
            self.range = self.stats['Range'][0]
            if self.upgradePath != 'WindDamage':
                self.push = self.stats['Push'][0]

    def updateTriangle(self):
        self.removeTriangle()
        self.drawTriangle()

    def drawTriangle(self):
        with Map.mapvar.background.canvas.after:
            Color(1, 1, 0, 1)
            if Player.player.towerSelected.towerGroup.facing == 'l':
                Map.mapvar.triangle = self.getTriangle('l')
                if Player.player.tbbox.x < Player.player.towerSelected.x and \
                        Player.player.tbbox.right > Player.player.towerSelected.x - self.squsize:
                    Player.player.tbbox.pos = (Player.player.tbbox.x - self.squsize, Player.player.tbbox.pos[1])
            elif Player.player.towerSelected.towerGroup.facing == 'r':
                Map.mapvar.triangle = self.getTriangle('r')
                if Player.player.tbbox.x > Player.player.towerSelected.x and \
                        Player.player.tbbox.x < Player.player.towerSelected.right + self.squsize:
                    Player.player.tbbox.pos = (Player.player.tbbox.x + self.squsize, Player.player.tbbox.pos[1])
            elif Player.player.towerSelected.towerGroup.facing == 'u':
                Map.mapvar.triangle = self.getTriangle('u')
            else:
                Map.mapvar.triangle = self.getTriangle('d')

    def removeTriangle(self):
        if Map.mapvar.triangle:
            Map.mapvar.background.canvas.after.remove(Map.mapvar.triangle)
            Map.mapvar.triangle = None

    def getTriangle(self, dir):
        # triangles for display around a tower indicating its direction
        x, y, top, right = self.x + __main__.app.root.border, self.y + __main__.app.root.border, \
                           self.top + __main__.app.root.border, self.right + __main__.app.root.border
        if dir == 'l':
            return Triangle(points=(x - self.squsize / 6,
                                    y + self.squsize / 6,
                                    x - self.squsize,
                                    y + self.squsize,
                                    x - self.squsize / 6,
                                    top - self.squsize / 6))
        if dir == 'r':
            return Triangle(points=(right + self.squsize / 6,
                                    y + self.squsize / 6,
                                    right + self.squsize,
                                    y + self.squsize,
                                    right + self.squsize / 6,
                                    top - self.squsize / 6))
        if dir == 'u':
            return Triangle(points=(x + self.squsize / 6,
                                    top + self.squsize / 6,
                                    x + self.squsize,
                                    top + self.squsize,
                                    right - self.squsize / 6,
                                    top + self.squsize / 6))
        if dir == 'd':
            return Triangle(points=(x + self.squsize / 6,
                                    y - self.squsize / 6,
                                    x + self.squsize,
                                    y - self.squsize,
                                    right - self.squsize / 6,
                                    y - self.squsize / 6))