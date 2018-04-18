import math
import os
import random
from kivy.animation import Animation
from kivy.graphics import *
from kivy.uix.widget import Widget

import GUI
import Localdefs
import MainFunctions
import Map
import Player
import SenderClass
import Utilities


class Enemy(Widget):
    """Enemies attack your base. This is a base class for specific enemy types below."""
    def __init__(self, **kwargs):
        super(Enemy, self).__init__()
        self.specialSend = kwargs['specialSend']
        if self.type == 'Crowd':
            self.size = (Map.mapvar.squsize/1.8, Map.mapvar.squsize/1.8)
        elif self.type == 'Standard' or self.type == 'Airborn':
            self.size = (Map.mapvar.squsize/1.4, Map.mapvar.squsize/1.4)
        else:
            self.size = (Map.mapvar.squsize - 5, Map.mapvar.squsize - 5)
        self.wavedict = Player.player.waveList[kwargs['wave']]
        if not self.specialSend:
            self.curnode = self.weightedcurnode = 0
            self.weightedcurnode = len(Map.mapvar.enemymovelists[0])- len(self.movelist)
            self.direction = self.dirlist[self.curnode]
            self.rect = Utilities.createRect(self.movelist[self.curnode], self.size, instance=self)
            self.pos = self.movelist[self.curnode]
            self.pushed = [0, 0]
            self.starthealth = self.health = self.wavedict['enemyhealth']
            self.speed = self.wavedict['enemyspeed']
            self.armor = self.wavedict['enemyarmor']
            self.reward = self.wavedict['enemyreward']
            self.mods = self.wavedict['enemymods']
            self.isBoss = self.wavedict['isboss']
            #print "health, speed, armor, reward, mods", self.health, self.speed, self.armor, self.reward, self.mods
        else:
            if self.type == 'Crowd':
                self.starthealth = self.health = Crowd.health * 1 + (Player.player.wavenum / 70)
                self.speed = Crowd.speed * 1 + (self.curwave / 70)
                self.armor = Crowd.armor * 1 + (self.curwave / 70)
                self.reward = Crowd.reward * 1 + (self.curwave / 70)
                self.mods = self.wavedict['enemymods']
                self.isBoss = self.wavedict['isboss']
        self.image.size = self.size
        self.image.allow_stretch = True
        self.add_widget(self.image)
        Map.mapvar.enemycontainer.add_widget(self)
        if self.isBoss:
            self.size = (self.size[0] * 1.3, self.size[1] * 1.3)
        self.gemImage = None

        self.slowtimers = list()
        self.slowpercent = 1
        self.slowtime = 0
        self.stuntimers = list()
        self.stuntime = 0
        self.pushAnimation = None
        # self.poisontimer = None

        #self.distBase = self.distToBase()
        self.explosionlength = 1
        self.isair = False
        self.isAlive = True
        self.hit = False
        self.recovering = False
        self.pushtimer = .5
        self.anim = self.move()
        self.image.pos = self.pos
        self.bind(pos=self.binding)
        self.drawHealthBar()
        Player.player.analytics.totalHP += self.health

    def takeTurn(self):
        '''Moves the enemy and adjusts any slow applied to it
        Frametime: the amount of time elapsed per frame'''
        self.workSlowTimers()
        self.workStunTimers()
        if self.pushed[0] != 0 or self.pushed[1] != 0:
            self.pushMove()
            self.updateHealthBar()
        else:
            self.updateHealthBar()

    def workSlowTimers(self):
        '''Adjust slow already applied to enemy
        Frametime: the amount of time elapsed per frame'''
        for st in self.slowtimers:
            st.slowtime -= Player.player.frametime
            if st.slowtime <= 0:
                self.slowpercent = 1
                self.slowtimers.remove(st)
                self.image.color = [1, 1, 1, 1]

    def workStunTimers(self):
        for st in self.stuntimers:
            st.stuntime -= Player.player.frametime
            if st.stuntime <= 0:
                self.stuntimers.remove(st)
                self.remove_widget(self.stunimage)
                self.anim = self.getNearestNode()

    def addStunImage(self):
        self.stunimage = Utilities.imgLoad(os.path.join('enemyimgs', "stunned.png"),
                                           pos=(self.x + (self.width / 2), self.top + 8))
        self.stunimage.size = (10, 10)
        self.add_widget(self.stunimage)
        self.bind(pos=self.bindStunImage)

    def bindStunImage(self, *args):
        self.stunimage.pos = (self.x + (self.width / 2), self.top + 8)

    # def distToBase(self):
    #     '''Determine distance to the end point using hypotenuse of xs and ys. Returns the distance.'''
    #     return math.sqrt(math.pow(Map.mapvar.basepoint[0] * Map.mapvar.squsize - self.rect_centerx, 2) + math.pow(
    #         Map.mapvar.basepoint[1] * Map.mapvar.squsize - self.rect_centery, 2))

    def move(self, *args):
        '''Moves the enemy down the generated move list
        Frametime: the amount of time elapsed per frame'''
        if self.stuntime > 0:
            return
        if self.curnode < len(self.movelist) - 1:
            self.direction = self.dirlist[self.curnode]
            self.curnode += 1
            self.weightedcurnode +=1
        distToTravel = int(
            abs(self.pos[0] - self.movelist[self.curnode][0] + self.pos[1] - self.movelist[self.curnode][1]))
        duration = float(distToTravel) / (self.speed * self.slowpercent)
        self.anim = Animation(pos=self.movelist[self.curnode], duration=duration, transition="linear")

        self.image.source = os.path.join("enemyimgs", self.type+ "_"+self.direction+".png")

        if self.curnode >= len(self.movelist) - 1:
            self.anim.bind(on_complete=self.checkHit)
        else:
            self.anim.bind(on_complete=self.move)
        self.anim.start(self)

        return self.anim

    def checkHit(self, *args):
        if Map.mapvar.baseimg.collide_widget(self.image):
            Player.player.sound.playSound(Player.player.sound.hitBase, start=.5)
            if self.isBoss:
                Player.player.health -=5
            else:
                Player.player.health -= 1
            GUI.gui.myDispatcher.Health = str(Player.player.health)
            Map.mapvar.enemycontainer.remove_widget(self)
            MainFunctions.flashScreen('red', 3)
            if Player.player.health <= 0:
                Player.player.die()
            return

    def pushMove(self):
        if self.recovering == False:
            if self.anim:
                self.anim.cancel_all(self)
            self.pushAnimation = Animation(pos=(self.x - self.pushed[0], self.y - self.pushed[1]),
                                           duration=self.pushtimer, t="out_cubic")
            self.pushAnimation.start(self)
            self.pushAnimation.bind(on_complete=self.getNearestNode)
            self.recovering = True
        self.pushtimer -= Player.player.frametime
        if self.pushtimer <= 0:
            self.recovering = False
            self.pushtimer = .5
            self.pushed = [0, 0]
            self.hit = False

    def binding(self, *args):
        self.image.pos = self.pos
        self.image.size = self.size
        self.rect_centerx, self.rect_centery = self.center

    def getNearestNode(self, *args):
        curnodedist = math.sqrt((self.center[0] - self.movelist[self.curnode][0]) ** 2 + (
                    self.center[1] - self.movelist[self.curnode][1]) ** 2)
        x = self.curnode
        for square in self.movelist[self.curnode:]:
            dist = math.sqrt((self.center[0] - square[0]) ** 2 + (
                    self.center[1] - square[1]) ** 2)
            if dist < curnodedist:
                self.curnode = x
                curnodedist = dist
            x += 1
        self.curnode -= 1
        self.move()

    def checkHealth(self):
        '''Checks enemy health and kills the enemy if health <=0'''
        if self.health <= 0:
            self.die()

    def die(self):
        '''If enemy runs out of health add them to explosions list, remove from enemy list, and add money to player's account'''
        if self.isAlive:
            self.isAlive = False
            if self.type == 'Splinter':
                self.splinter()
            if self.isair == True:
                Localdefs.flyinglist.remove(self)
            if self.anim:
                self.anim.cancel_all(self)
            if self.pushAnimation:
                self.pushAnimation.cancel_all(self)
            if self.isBoss:
                x = random.randint(0, 100)
                if x < 10:
                    self.gemImage = True
                    Player.player.gems += 1
                    GUI.gui.myDispatcher.Gems = str(Player.player.gems)
            self.startDeathAnim()
            self.remove_widget(self.image)
            Map.mapvar.enemycontainer.remove_widget(self)
            Player.player.money += int(self.reward)
            Player.player.analytics.moneyEarned += self.reward
            Player.player.score += self.points
            GUI.gui.myDispatcher.Money = str(Player.player.money)
            GUI.gui.myDispatcher.Score = str(Player.player.score)
            MainFunctions.updateGUI()

    def startDeathAnim(self):
        if self.gemImage:
            self.gemImage = Utilities.imgLoad(source=(os.path.join("iconimgs", "reddiamond.png")))
            self.gemImage.size = (40, 40)
            self.gemImage.center = self.center
            Map.mapvar.backgroundimg.add_widget(self.gemImage)
            self.gemanim = Animation(pos=(Map.mapvar.squsize*20, Map.mapvar.scrhei - Map.mapvar.squsize), size=(20, 24), duration=6) + \
                           Animation(size=(0, 0), duration=.1)
            self.gemanim.bind(on_complete=self.endDeathAnim)
            self.gemanim.start(self.gemImage)
        self.coinimage = Utilities.imgLoad(source=(os.path.join("iconimgs", "coin20x24.png")))
        self.coinimage.size = (5, 7)
        self.coinimage.center = self.center
        Map.mapvar.backgroundimg.add_widget(self.coinimage)
        self.deathanim = Animation(pos=(Map.mapvar.squsize*18, Map.mapvar.scrhei - Map.mapvar.squsize), size=(10, 12), duration=.3) + \
                         Animation(size=(0, 0), duration=.1)
        self.deathanim.bind(on_complete=self.endDeathAnim)
        self.deathanim.start(self.coinimage)

    def endDeathAnim(self, *args):
        Map.mapvar.backgroundimg.remove_widget(self.coinimage)
        if self.isBoss:
            if self.gemImage:
                Map.mapvar.backgroundimg.remove_widget(self.gemImage)

    def drawHealthBar(self):
        healthbarpoints = [self.x, self.y + self.height + 2, self.x + self.width, self.y + self.height + 2]
        if self.direction == 'd':
            healthbarpoints = [self.right + 2, self.y + self.height, self.right + 2, self.y]
        elif self.direction == 'u':
            healthbarpoints = [self.x - 2, self.y, self.x - 2, self.y + self.height]

        with self.canvas:  # draw health bars
            Color(0, 0, 0, .6)
            self.healthbar = Line(
                points=healthbarpoints, width=2, cap=None)
            Color(1, 1, 1, 1)
            self.remaininghealth = Line(
                points=healthbarpoints, width=1.4, cap=None)

    def updateHealthBar(self):
        healthbarpoints = [self.x, self.y + self.height + 2, self.x + self.width, self.y + self.height + 2]
        if self.direction == 'd':
            healthbarpoints = [self.right + 2, self.y + self.height, self.right + 2, self.y]
        elif self.direction == 'u':
            healthbarpoints = [self.x - 2, self.y, self.x - 2, self.y + self.height]


        self.percentHealthRemaining = self.health / self.starthealth
        remaininghealth = [self.x, self.y + self.height + 2, self.x + self.width * self.percentHealthRemaining, self.y + self.height + 2]
        if self.direction == 'd':
            remaininghealth = [self.right + 2, self.y + self.height, self.right + 2, self.y + self.height * (1 - self.percentHealthRemaining)]
        elif self.direction == 'u':
            remaininghealth = [self.x - 2, self.y, self.x - 2, self.y + self.height * self.percentHealthRemaining]

        self.healthbar.points = healthbarpoints
        self.remaininghealth.points = remaininghealth


class Standard(Enemy):
    defaultNum = 8
    deploySpeed = 1
    health = 80
    speed = 45
    armor = 0
    reward = 1
    points = 1
    imagesrc = os.path.join("enemyimgs", "Standard_r.png")

    def __init__(self, **kwargs):
        self.type = 'Standard'
        self.defaultNum = Standard.defaultNum
        self.deploySpeed = Standard.deploySpeed
        self.points = Standard.points  # points granted per kill
        self.imagesrc = Standard.imagesrc
        self.image = Utilities.imgLoad(self.imagesrc)
        self.movelistNum = random.randint(0, Map.mapvar.numpaths - 1)
        self.movelist = Map.mapvar.enemymovelists[self.movelistNum]  # 0 for ground, 1 for air
        self.dirlist = Map.mapvar.dirmovelists[self.movelistNum]
        super(Standard, self).__init__(**kwargs)


class Airborn(Enemy):
    defaultNum = 8
    deploySpeed = 1
    health = 80
    speed = 50
    armor = 0
    reward = 1
    points = 1
    imagesrc = os.path.join("enemyimgs", "Airborn_r.png")

    def __init__(self, **kwargs):
        self.type = 'Airborn'
        self.defaultNum = Airborn.defaultNum  # 10 enemies per wave
        self.deploySpeed = Airborn.deploySpeed
        self.points = Airborn.points  # points granted per kill
        self.imagesrc = Airborn.imagesrc
        self.image = Utilities.imgLoad(self.imagesrc)
        self.movelistNum = random.randint(0, Map.mapvar.numpaths - 1)
        self.movelist = Map.mapvar.enemyflymovelists[self.movelistNum]  # 0 for ground, 1 for air
        self.dirlist = Map.mapvar.dirflymovelists[self.movelistNum]
        super(Airborn, self).__init__(**kwargs)
        self.isair = True
        Localdefs.flyinglist.append(self)


class Splinter(Enemy):
    defaultNum = 5
    deploySpeed = 3
    health = 150
    speed = 30
    armor = 5
    reward = 2
    points = 2
    imagesrc = os.path.join("enemyimgs", "Splinter_r.png")

    def __init__(self, **kwargs):
        self.type = 'Splinter'
        self.defaultNum = Splinter.defaultNum  # 10 enemies per wave
        self.deploySpeed = Splinter.deploySpeed
        self.points = Splinter.points  # points granted per kill
        self.imagesrc = Splinter.imagesrc
        self.image = Utilities.imgLoad(self.imagesrc)
        self.movelistNum = random.randint(0, Map.mapvar.numpaths - 1)
        self.movelist = Map.mapvar.enemymovelists[self.movelistNum]  # 0 for ground, 1 for air
        self.curwave = Player.player.wavenum
        self.dirlist = Map.mapvar.dirmovelists[self.movelistNum]
        super(Splinter, self).__init__(**kwargs)

    # break the Splinter apart when it dies. 15 Crowd are released.
    def splinter(self):
        SenderClass.Sender(specialSend=True, enemytype='Crowd', pos=self.pos, curnode=self.curnode, number=8,
                           deploySpeed=0, curwave=self.curwave)


class Strong(Enemy):
    defaultNum = 5
    deploySpeed = 3
    health = 200
    speed = 25
    armor = 10
    reward = 2
    points = 2
    imagesrc = os.path.join("enemyimgs", "Strong_r.png")

    def __init__(self, **kwargs):
        self.type = 'Strong'
        self.defaultNum = Strong.defaultNum
        self.deploySpeed = Strong.deploySpeed
        self.points = Strong.points  # points granted per kill
        self.imagesrc = Strong.imagesrc
        self.image = Utilities.imgLoad(self.imagesrc)
        self.movelistNum = random.randint(0, Map.mapvar.numpaths - 1)
        self.movelist = Map.mapvar.enemymovelists[self.movelistNum]  # 0 for ground, 1 for air
        self.dirlist = Map.mapvar.dirmovelists[self.movelistNum]
        super(Strong, self).__init__(**kwargs)


class Crowd(Enemy):
    defaultNum = 15
    deploySpeed = .8
    health = 40
    speed = 60
    armor = 0
    reward = 1
    points = 1
    imagesrc = os.path.join("enemyimgs", "Crowd_r.png")

    def __init__(self, **kwargs):
        self.type = 'Crowd'
        self.defaultNum = Crowd.deploySpeed
        self.points = Crowd.points  # points granted per kill
        self.imagesrc = Crowd.imagesrc
        self.image = Utilities.imgLoad(self.imagesrc)
        self.movelistNum = random.randint(0, Map.mapvar.numpaths - 1)
        self.movelist = Map.mapvar.enemymovelists[self.movelistNum]  # 0 for ground, 1 for air
        self.dirlist = Map.mapvar.dirmovelists[self.movelistNum]

        if kwargs['specialSend']:
            self.size = (Map.mapvar.squsize * .5, Map.mapvar.squsize * .5)
            self.pos = kwargs['pos']
            self.curwave = kwargs['wave']
            pushx = random.randint(-75, 75)
            pushy = random.randint(-75, 75)
            self.pushed = [pushx, pushy]
            self.curnode = self.weightedcurnode = kwargs['curnode']
            print self.curnode, self.movelist
            self.rect = Utilities.createRect(self.pos, self.size, instance=self)

        super(Crowd, self).__init__(**kwargs)
