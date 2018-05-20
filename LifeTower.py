import os

from Towers import Tower
import Shot
import Map

class LifeTower(Tower):
    type = "Life"
    cost = 15
    initrange = 5
    initdamage = 10
    initreload = 1.0
    initpush = 0
    attacks = "Both"
    imagestr = os.path.join('towerimgs', 'Life', 'icon.png')
    upgradeDict = {'Damage': [1, 1.1, 1.4, 1.7, 2, 10, 12,14,16,18,20,'NA'], 'Range': [1, 1, 1, 1, 1, 1.5, 2.5, 2.8, 3.1, 3.3, 3.5, 'NA'],
     'Reload': [1, 1, 1, 1, 1, 3, 2.9, 2.8, 2.6, 2.4, 2, 'NA'], 'Push':[0,0,0,0,0,1,1.1,1.2,1.3,1.4,1.5, 'NA'],'Cost': [0, 5, 50, 100, 175, (250, 1), 400, 500, 600, 800, 1000, 'NA']}
    upgradeName = 'Sniper'
    upgradeDescription = 'Shoots powerful shots at a single enemy, dealing massive damage. The enemy is knocked backwards due to the velocity of the shot'
    'Effects all enemies, although nearby enemies cannot be targeted. Increases damage and range, but increases reload time.'
    upgradeStats = ['Push: knockback of the enemy when hit by a shot']

    def __init__(self, pos, **kwargs):
        Tower.__init__(self, pos, **kwargs)
        self.pos = pos
        self.cost = LifeTower.cost
        self.initRange = self.range = LifeTower.initrange * Map.mapvar.squsize
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
        self.turretRotates = True
        self.active = True
        self.loadTurret()
        self.reloadFrameList = ["reload_frame1.png","reload_frame2.png", "reload_frame3.png", "turret2.png" ]
        self.upgradeDict = LifeTower.upgradeDict
        self.menu = [('Damage', 1, ' DPH', 'Damage'), ('Range', 0, 'px', 'Range'), ('Reload', 1, 's', 'Reload')]
        self.dmgMenu = [('Damage', 1, ' DPH', 'Damage'), ('Range', 0, 'px', 'Range'), ('Reload', 1, 's', 'Reload'), ('Push', 0, 'px', 'Push')]
        self.leaderMenu = [('Damage', 0, '%', 'Damage'), ('Range', 0, '%', 'Range'), ('Reload', 0, '%', 'Reload')]
        #self.setTowerData()

    def hitEnemy(self, enemy):
        self.targetedEnemy = enemy
        self.moveTurret(enemy)
        self.shotcount += 1
        Shot.Shot(self, self.targetedEnemy)
        self.targetTimer = self.towerGroup.targetTimer = self.reload
        if self.upgradePath == 'LifeDamage':
            self.recharge()

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

    def setupUpgradePath(self):
        if self.leader:
            self.menu = self.leaderMenu
            self.loadTurret()
        else:
            self.menu = self.dmgMenu
            self.recharging = True
            self.turret.source = os.path.join("towerimgs", self.type, "reload_frame1.png")
            self.turret.size = (1.5 * Map.mapvar.squsize, 1.5 * Map.mapvar.squsize)
            self.turret.center = self.center
            self.shotDuration = .1
            self.shotimage = "shot2.png"
            self.initPush = self.push = 5
            self.rangeExclusion = Map.mapvar.squsize*3

    def updateStats(self):
        if not self.leader:
            self.damage = self.stats['Damage'][0]
            self.reload = self.stats['Reload'][0]
            self.range = self.stats['Range'][0]
            if self.upgradePath == 'LifeDamage':
                self.push = self.stats['Push'][0]