
import os
import random
from kivy.animation import Animation
from kivy.graphics import *
from kivy.uix.image import Image
from kivy.vector import Vector

import Localdefs
import MainFunctions
import Map
import Player
import SenderClass
import __main__


class Enemy(Image):
    """Enemies attack your base. This is a base class for specific enemy types below."""
    def __init__(self, **kwargs):
        super(Enemy, self).__init__(**kwargs)
        self.nocache = True
        self.specialSend = kwargs['specialSend']
        self.enemyNumber = kwargs['enemyNum']
        if self.type == 'Crowd':
            self.size = (Map.mapvar.squsize/1.8, Map.mapvar.squsize/1.8)
        elif self.type == 'Standard' or self.type == 'Airborn':
            self.size = (Map.mapvar.squsize/1.4, Map.mapvar.squsize/1.4)
        else:
            self.size = (Map.mapvar.squsize - 5, Map.mapvar.squsize - 5)
        self.wavedict = Player.player.waveList[kwargs['wave']]
        if not self.specialSend:
            self.curnode = 0
            self.pos = self.movelist[self.curnode]
            self.pushed = [0, 0]
            self.starthealth = self.health = self.wavedict['enemyhealth']
            self.speed = self.wavedict['enemyspeed']
            self.armor = self.armor_start = self.wavedict['enemyarmor']
            self.reward = self.wavedict['enemyreward']
            self.mods = self.wavedict['enemymods']
            self.isBoss = self.wavedict['isboss']
            #print "health, speed, armor, reward, mods", self.health, self.speed, self.armor, self.reward, self.mods
        else:
            if self.type == 'Crowd':
                self.starthealth = self.health = Crowd.health * 1 + (Player.player.wavenum / 70)
                self.speed = Crowd.speed * 1 + (self.curwave / 70)
                self.armor = self.armor_start = Crowd.armor * 1 + (self.curwave / 70)
                self.reward = Crowd.reward * 1 + (self.curwave / 70)
                self.mods = self.wavedict['enemymods']
                self.isBoss = self.wavedict['isboss']
        self.direction = self.dirlist[self.curnode]
        self.previous_direction = self.direction
        self.allow_stretch = True
        Map.mapvar.enemycontainer.add_widget(self)
        if self.isBoss:
            self.size = (self.size[0] * 1.3, self.size[1] * 1.3)
        self.gemImage = None
        self.slowpercent = 100
        self.slowtime = 0
        self.updateSlow = False
        self.stuntime = 0
        self.stunimage = Image(pos=(self.center_x, self.top + 8),size=(Map.mapvar.squsize/3,Map.mapvar.squsize/3))
        self.burntime = 0
        self.burnDmg = 0
        self.bind(pos=self.bindStunImage)
        self.pushAnimation = None
        self.isair = False
        self.isAlive = True
        self.recovering = False
        self.useOldNode = False
        self.roadPos = 0
        self.pushAnimation = None
        self.backToRoad = None
        self.anim = None
        self.priority = self.getPriority()
        self.percentHealthRemaining = self.health / self.starthealth
        self.percentArmorRemaining = self.armor / self.armor_start
        if not self.specialSend:
            self.move()

    def takeTurn(self):
        '''Moves the enemy and adjusts any slow applied to it'''
        self.priority = self.getPriority()
        if self.slowtime != 0:
            self.workSlowTime()
        if self.stuntime > 0:
            self.workStunTime()
        if self.burntime > 0:
            self.workBurnTimer()
        if self.pushed[0] != 0 or self.pushed[1] != 0:
            self.pushMove()


    def change_move_in_progress(self):
        if self.anim:
            if self.anim.have_properties_to_animate(self):
                self.updateSlow = False
                self.useOldNode = True
                self.anim.cancel(self)
                self.move()

    def workSlowTime(self):
        '''Adjust slow already applied to enemy'''
        if self.updateSlow == True:
            self.change_move_in_progress()

        self.slowtime -= Player.player.frametime
        if self.slowtime < Player.player.frametime:
            self.slowtime = 0
            self.slowpercent = 100
            self.color = [1, 1, 1, 1]
            self.change_move_in_progress()

    def workStunTime(self):
        self.stuntime -= Player.player.frametime
        if self.stuntime <= 0:
            self.stuntime = 0
            self.remove_widget(self.stunimage)
            if not Player.player.state == 'Paused':
                self.anim = self.getNearestRoad()

    def workBurnTimer(self):
        self.burntime -= Player.player.frametime
        self.health -= self.burnDmg * Player.player.frametime
        self.checkHealth()
        if self.burntime <= 0:
            self.burntime = 0
            self.color = [1, 1, 1, 1]

    def bindStunImage(self, *args):
        self.stunimage.center = (self.center_x, self.top + 8)

    def getPriority(self):
        distToBase = Vector(self.center).distance(Map.mapvar.baseimg.center)
        if distToBase < Map.mapvar.squsize*2:
            self.checkHit()
        if distToBase > Map.mapvar.baseimg.x/1.5:
            num = 10
        elif distToBase > Map.mapvar.baseimg.x/2:
            num = 6
        elif distToBase > Map.mapvar.baseimg.x/3:
            num = 2
        else:
            num = 0
        boss = 0 if self.isBoss else 2
        nodes = float(len(self.movelist) - self.curnode)
        isair = 0 if self.isair else 1
        senderNum = self.enemyNumber/10.0
        return float(num + boss + nodes + isair + senderNum)

    def move(self, *args):
        '''Moves the enemy down the generated move list
        Frametime: the amount of time elapsed per frame'''
        if self.stuntime > 0:
            return
        if self.anim:
            if self.anim.have_properties_to_animate(self):
                return
        if self.curnode < len(self.movelist) - 1 and not self.useOldNode:
            self.curnode += 1
        self.direction = self.dirlist[self.curnode-1]
        if self.previous_direction == 'l' and self.direction != 'l':
            self.texture.flip_horizontal()
        if self.direction == 'r':
            self.angle = 0
        elif self.direction == 'u':
            self.angle = 90
        elif self.direction == 'd':
            self.angle = 270
        elif self.direction == 'l':
            #self.source = "enemyimgs/"+ str(self.type)+"_l.png"
            self.texture.flip_vertical()
            self.angle = 180
        self.previous_direction = self.direction
        distToTravel = Vector(self.pos).distance(self.movelist[self.curnode])
        duration = float(distToTravel) / (self.speed * (self.slowpercent/100.0))
        self.anim = Animation(pos=self.movelist[self.curnode], duration=duration, transition="linear")
        if self.curnode < len(self.movelist) - 1 or self.useOldNode == True:
            self.anim.bind(on_complete=self.move)
        self.anim.start(self)
        self.useOldNode = False

    def checkHit(self, *args):
        if Map.mapvar.baseimg.collide_widget(self) and self.isAlive:
            self.die(base=True)
            Player.player.sound.playSound(Player.player.sound.hitBase, start=.5)
            if self.isBoss:
                if self.specialSend:
                    Player.player.health-=2
                else:
                    Player.player.health -=5
            else:
                Player.player.health -= 1
            Player.player.myDispatcher.Health = str(Player.player.health)
            MainFunctions.flashScreen('red', 2)
            if Player.player.health <= 0:
                Player.player.die()
            return

    def pushMove(self):
        if self.recovering == False:
            if self.anim:
                self.anim.cancel_all(self)
            if self.backToRoad:
                self.backToRoad.cancel_all(self)
            self.pushAnimation = Animation(pos=(self.x - self.pushed[0], self.y - self.pushed[1]),
                                           duration=.3, t="out_cubic")
            self.pushAnimation.bind(on_complete = self.pushRecover)
            self.pushAnimation.start(self)
            self.recovering = True
            self.pushed = [0, 0]

    def pushRecover(self, *args):
        self.recovering = False
        self.getNearestRoad()

    def getNearestRoad(self, *args):
        if not self.isair:
            self.useOldNode = True
            if self.curnode == len(self.movelist)-1:
                self.move()
            for road in Map.mapvar.roadcontainer.children:
                if self.collide_widget(road):
                    self.roadPos = road.pos
                    self.getNextNode()
                    return
            distToRoad = 0
            destRoad = None
            for road in Map.mapvar.roadcontainer.children:
                dist = Vector(self.right, self.y).distance(road.pos)
                if dist < distToRoad or distToRoad == 0:
                    distToRoad = Vector(self.pos).distance(road.pos)
                    destRoad = road
                    self.roadPos = road.pos
            duration = float(distToRoad) / (self.speed * (self.slowpercent / 100.0))
            self.backToRoad = Animation(pos = destRoad.pos, duration = duration, transition = 'linear')
            self.backToRoad.bind(on_complete=self.getNextNode)
            self.backToRoad.start(self)
        else:
            self.move()

    def getNextNode(self, *args):
        x = 0
        while x < len(self.movelist)-1:
            priorpos = self.movelist[x]
            nextpos = self.movelist[x+1]
            if self.roadPos:
                if Vector.in_bbox((self.roadPos),priorpos,nextpos):
                    self.roadPos = 0
                    self.curnode = x+1
                    break
            else:
                if Vector.in_bbox((self.pos),priorpos,nextpos):
                    self.curnode = x+1
                    break
            x += 1
        self.useOldNode = True
        self.move()

    def getFuturePos(self,time):
        '''time is in seconds'''
        distToNode_x = self.movelist[self.curnode][0] - self.x
        distToNode_y = self.movelist[self.curnode][1] - self.y
        timeToNode = abs(distToNode_x + distToNode_y)/(self.speed * (self.slowpercent/100.0))
        if time <= timeToNode:
            change = (self.speed * (self.slowpercent/100)) * time
            if distToNode_x != 0:
                if distToNode_x > 0:
                    return (self.x + change, self.y)
                else:
                    return (self.x - change, self.y)
            else:
                if distToNode_y > 0:
                    return (self.x, self.y + change)
                else:
                    return (self.x, self.y - change)

        else:
            if self.curnode >= len(self.movelist) - 1:
                return self.movelist[self.curnode]
            else:
                time = time-timeToNode
                distToNode_x = self.movelist[self.curnode+1][0] - self.movelist[self.curnode][0]
                distToNode_y = self.movelist[self.curnode+1][1] - self.movelist[self.curnode][1]
                change = (self.speed * (self.slowpercent / 100)) * time
                if distToNode_x != 0:
                    if distToNode_x > 0:
                        return (self.movelist[self.curnode][0] + change, self.movelist[self.curnode][1])
                    else:
                        return (self.movelist[self.curnode][0] - change, self.movelist[self.curnode][1])
                else:
                    if distToNode_y > 0:
                        return (self.movelist[self.curnode][0], self.movelist[self.curnode][1] + change)
                    else:
                        return (self.movelist[self.curnode][0], self.movelist[self.curnode][1] - change)

    def checkHealth(self):
        '''Checks enemy health and kills the enemy if health <=0'''
        self.percentHealthRemaining = self.health / self.starthealth
        self.percentArmorRemaining = self.armor / self.armor_start
        if self.percentArmorRemaining < .02:
            self.percentArmorRemaining = 0
        if self.health <= 0:
            self.die()

    def die(self, base = False):
        '''If enemy runs out of health add them to explosions list, remove from enemy list, and add money to player's account'''
        if self.isAlive:
            if self.isair == True:
                Localdefs.flyinglist.remove(self)
            if self.anim:
                self.anim.cancel_all(self)
            if self.pushAnimation:
                self.pushAnimation.cancel_all(self)
            if self.backToRoad:
                self.backToRoad.cancel_all(self)
            self.clear_widgets()
            Map.mapvar.enemycontainer.remove_widget(self)
            if not base:
                if self.type == 'Splinter' and self.isAlive:
                    self.splinter()
                if self.isBoss:
                    x = random.randint(0, 100)
                    if x < 3:
                        self.gemImage = True
                self.startDeathAnim()
                Player.player.money += int(self.reward)
                Player.player.analytics.moneyEarned += self.reward
                Player.player.score += self.points
                Player.player.myDispatcher.Money = str(Player.player.money)
                Player.player.myDispatcher.Score = str(Player.player.score)
                MainFunctions.updateGUI()
            self.isAlive = False

    def startDeathAnim(self):
        if self.gemImage:
            self.gemImage = Image(source=(os.path.join("iconimgs", "gem.png")), size = (40,40), center = (self.x - .45*Map.mapvar.background.width, self.y - .45*Map.mapvar.background.height))
            Map.mapvar.background.add_widget(self.gemImage)
            self.gemanim = Animation(pos=(__main__.ids.gemimage.x - .55*Map.mapvar.background.width,
                                          __main__.ids.gemimage.y - .6*Map.mapvar.background.height),
                                     size=(20, 24), duration=4) + \
                           Animation(size=(0, 0), duration=.1)
            Player.player.gems += 1
            Player.player.myDispatcher.Gems = str(Player.player.gems)
            self.gemanim.bind(on_complete=self.endDeathAnim)
            self.gemanim.start(self.gemImage)
        if not Player.player.coinAnimating:
            Player.player.coinanim.start(__main__.ids.coinimage)

    def endDeathAnim(self, *args):
        if self.isBoss:
            if self.gemImage:
                Map.mapvar.background.remove_widget(self.gemImage)


class Standard(Enemy):
    defaultNum = 8
    deploySpeed = 1
    health = 80
    speed = 45
    armor = 20
    reward = 1
    points = 1
    imagesrc = os.path.join("enemyimgs", "Standard.png")

    def __init__(self, **kwargs):
        self.type = 'Standard'
        self.defaultNum = Standard.defaultNum
        self.deploySpeed = Standard.deploySpeed
        self.points = Standard.points  # points granted per kill
        self.imagesrc = Standard.imagesrc
        self.source = self.imagesrc
        self.movelistNum = random.randint(0, Map.mapvar.numpaths - 1)
        self.movelist = Map.mapvar.enemymovelists[self.movelistNum]  # 0 for ground, 1 for air
        self.dirlist = Map.mapvar.dirmovelists[self.movelistNum]
        self.percentHealthRemaining = 100
        self.percentArmorRemaining = 100
        super(Standard, self).__init__(**kwargs)


class Airborn(Enemy):
    defaultNum = 8
    deploySpeed = 1
    health = 80
    speed = 50
    armor = 20
    reward = 1
    points = 1
    imagesrc = os.path.join("enemyimgs", "Airborn.png")

    def __init__(self, **kwargs):
        self.type = 'Airborn'
        self.defaultNum = Airborn.defaultNum  # 10 enemies per wave
        self.deploySpeed = Airborn.deploySpeed
        self.points = Airborn.points  # points granted per kill
        self.imagesrc = Airborn.imagesrc
        self.source = self.imagesrc
        self.movelistNum = random.randint(0, Map.mapvar.numpaths - 1)
        self.movelist = Map.mapvar.enemyflymovelists[self.movelistNum]  # 0 for ground, 1 for air
        self.dirlist = Map.mapvar.dirflymovelists[self.movelistNum]
        self.percentHealthRemaining = 100
        self.percentArmorRemaining = 100
        super(Airborn, self).__init__(**kwargs)
        self.isair = True
        Localdefs.flyinglist.append(self)


class Splinter(Enemy):
    defaultNum = 5
    deploySpeed = 3
    health = 150
    speed = 30
    armor = 100
    reward = 2
    points = 2
    imagesrc = os.path.join("enemyimgs", "Splinter.png")

    def __init__(self, **kwargs):
        self.type = 'Splinter'
        self.defaultNum = Splinter.defaultNum  # 10 enemies per wave
        self.deploySpeed = Splinter.deploySpeed
        self.points = Splinter.points  # points granted per kill
        self.imagesrc = Splinter.imagesrc
        self.source = self.imagesrc
        self.movelistNum = random.randint(0, Map.mapvar.numpaths - 1)
        self.movelist = Map.mapvar.enemymovelists[self.movelistNum]  # 0 for ground, 1 for air
        self.curwave = kwargs['wave']
        self.dirlist = Map.mapvar.dirmovelists[self.movelistNum]
        self.percentHealthRemaining = 100
        self.percentArmorRemaining = 100
        super(Splinter, self).__init__(**kwargs)

    # break the Splinter apart when it dies. 8 Crowd are released.
    def splinter(self):
        SenderClass.Sender(specialSend=True, enemytype='Crowd', pos=self.pos, number=8,
                           deploySpeed=0, curwave=self.curwave)


class Strong(Enemy):
    defaultNum = 5
    deploySpeed = 3
    health = 200
    speed = 25
    armor = 200
    reward = 2
    points = 2
    imagesrc = os.path.join("enemyimgs", "Strong.png")

    def __init__(self, **kwargs):
        self.type = 'Strong'
        self.defaultNum = Strong.defaultNum
        self.deploySpeed = Strong.deploySpeed
        self.points = Strong.points  # points granted per kill
        self.imagesrc = Strong.imagesrc
        self.source = self.imagesrc
        self.movelistNum = random.randint(0, Map.mapvar.numpaths - 1)
        self.movelist = Map.mapvar.enemymovelists[self.movelistNum]  # 0 for ground, 1 for air
        self.dirlist = Map.mapvar.dirmovelists[self.movelistNum]
        self.percentHealthRemaining = 100
        self.percentArmorRemaining = 100
        super(Strong, self).__init__(**kwargs)


class Crowd(Enemy):
    defaultNum = 15
    deploySpeed = .8
    health = 40
    speed = 60
    armor = 10
    reward = 1
    points = 1
    imagesrc = os.path.join("enemyimgs", "Crowd.png")

    def __init__(self, **kwargs):
        self.type = 'Crowd'
        self.defaultNum = Crowd.deploySpeed
        self.points = Crowd.points  # points granted per kill
        self.imagesrc = Crowd.imagesrc
        self.source = self.imagesrc
        self.movelistNum = random.randint(0, Map.mapvar.numpaths - 1)
        self.movelist = Map.mapvar.enemymovelists[self.movelistNum]  # 0 for ground, 1 for air
        self.dirlist = Map.mapvar.dirmovelists[self.movelistNum]
        self.percentHealthRemaining = 100
        self.percentArmorRemaining = 100

        if kwargs['specialSend']:
            self.size = (Map.mapvar.squsize * .5, Map.mapvar.squsize * .5)
            self.pos = kwargs['pos']
            self.curwave = kwargs['wave']
            pushx = random.randint(-Map.mapvar.squsize*3, Map.mapvar.squsize*3)
            pushy = random.randint(-Map.mapvar.squsize*3, Map.mapvar.squsize*3)
            self.pushed = [pushx, pushy]
            self.curnode = 0

        super(Crowd, self).__init__(**kwargs)
