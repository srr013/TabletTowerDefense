import os
import math
import random
from kivy.animation import Animation
from kivy.graphics import *
from kivy.uix.image import Image
from kivy.vector import Vector

import Localdefs
import Map
import Utilities
import Player

##manages each shot from each tower so we can show the shot in flight.
class Shot(Image):
    def __init__(self, tower, enemy, **kwargs):
        super(Shot, self).__init__(**kwargs)
        self.enemy = enemy
        self.tower = tower
        self.size = (10,10)
        self.center = tower.center
        self.source = os.path.join('towerimgs',tower.type,tower.shotimage)
        self.allow_stretch = True
        self.damage = tower.damage
        self.burnDmg = 0
        self.road = []
        self.attacktype = tower.attacktype
        self.speed = 100
        self.complete = False
        Map.mapvar.shotcontainer.add_widget(self)
        Localdefs.shotlist.append(self)
        # if tower.type != 'Wind':
        #     with self.image.canvas.before:
        #         PushMatrix()
        #         self.rot = Rotate()
        #         self.rot.axis = (0, 0, 1)
        #         self.rot.origin=self.image.center
        #         self.rot.angle=180
        #     with self.image.canvas.after:
        #         PopMatrix()
        self.pushx = 0
        self.pushy = 0
        if tower.type == 'Wind':
            self.hitlist = []
            self.speed = 250
            self.facing = self.tower.towerGroup.facing
            with self.canvas.before:
                PushMatrix()
                self.rot = Rotate()
                self.rot.axis = (0, 0, 1)
                self.rot.origin=self.center
                self.rot.angle = 0
            with self.canvas.after:
                PopMatrix()
        self.anim = None
        self.shotAnimate()


    def takeTurn(self):
        #if self.tower.type != 'Wind':
        self.rotate()
        if self.tower.upgradePath == 'WindDamage':
            if Utilities.in_range(self.tower,self.enemy):
                self.updateLine()
                Player.player.analytics.gameDamage += self.damage
                self.enemy.health -= max(self.damage - (self.enemy.armor * Player.player.frametime), 0)
                self.enemy.checkHealth()
                if not self.enemy.isAlive:
                    self.canvas.remove(self.electricLine)
                    self.removeShot()
            else:
                self.canvas.remove(self.electricLine)
                self.removeShot()

    def hitEnemy(self, enemy):
        '''Reduces enemy health by damage - armor'''
        Player.player.analytics.gameDamage += self.damage
        enemy.health -= max(self.damage - (self.damage*(self.enemy.armor/100)), 0)
        enemy.checkHealth()
        if self.tower.type == 'Life' and self.tower.push > 0:
            enemy.pushed = [self.pushx, self.pushy]
            self.removeShot()
            return
        elif self.tower.type == "Wind":
            if not self.tower.upgradePath:
                enemy.pushed = [self.pushx, self.pushy]
        elif self.tower.upgradePath == 'FireDamage':
            enemy.slowtime = 0
            enemy.workSlowTime()
        else:
            self.removeShot()

    def shotAnimate(self):
        if self.tower.type == 'Wind':
            if self.tower.upgradePath != 'WindDamage':
                dest = [0, 0]
                self.angle = 0
                if self.facing == 'l':
                    dest[1] = self.tower.pos[1]
                    self.angle = 180
                elif self.facing == 'r':
                    dest[0] = Map.mapvar.scrwid
                    dest[1] = self.tower.pos[1]
                elif self.facing == 'u':
                    dest[0] = self.tower.pos[0]
                    dest[1] = Map.mapvar.scrhei
                    self.angle = 90
                elif self.facing == 'd':
                    dest[0] = self.tower.pos[0]
                    self.angle = 270

                self.rot.angle = self.angle

                distToTravel = int(abs(self.pos[0] - dest[0] + self.pos[1] - dest[1]))
                duration = float(distToTravel) / self.speed
                self.anim = Animation(pos=(dest[0], dest[1]), size=(90,120), duration=duration)
                self.anim.bind(on_complete=self.removeShot)
                self.anim.bind(on_progress=self.checkHit)
            else:
                self.damage = self.damage * Player.player.frametime
                self.size = (0,0)
                self.center = self.tower.center
                self.drawLine()
                return

        elif self.tower.upgradePath == 'FireDamage':
            self.shotWithArc()
            self.burnDmg = self.tower.burn
            self.size = (25, 25)
            self.center = self.tower.center
            distance = Vector(self.center).distance(self.enemy.center)
            self.duration = (distance/self.speed) / (len(self.pointlist))
            self.nextArcAnim()

        else:
            #self.rotate()
            self.anim = Animation(center=self.enemy.center, duration=self.tower.shotDuration)
            self.anim.bind(on_complete=self.checkHit)


        self.anim.start(self)

    def drawLine(self):
        with self.canvas:
            Color(1,1,0,1)
            self.electricLine = Line(points = [self.center_x, self.center_y, self.enemy.center_x, self.enemy.center_y], width=1.2)

    def updateLine(self):
        self.electricLine.points = [self.center_x, self.center_y, self.enemy.center_x, self.enemy.center_y]

    def nextArcAnim(self,*args):
        if self.animIndex < len(self.pointlist)-1:
            self.animIndex += 1
            self.anim = Animation(center=self.pointlist[self.animIndex], duration=self.duration, transition='linear')
            self.anim.bind(on_complete=self.nextArcAnim)
            self.anim.start(self)
        else:
            self.checkHit()

    def shotWithArc(self):
        self.animIndex = 0
        origin = Vector(self.tower.center)
        destination = Vector(self.enemy.getFuturePos(self.tower.shotDuration*1.1))
        destination = Vector(destination.x+random.randint(0,Map.mapvar.squsize), destination.y+random.randint(0,Map.mapvar.squsize))
        centerPoint = origin - (origin-destination)/2
        radius = origin.distance(destination)/2
        initAngle = round(math.atan2((origin.y - centerPoint.y),(origin.x - centerPoint.x)),1)
        destAngle = round(math.atan2((destination.y - centerPoint.y),(destination.x - centerPoint.x)),1)
        self.pointlist = []
        interval = .3
        angle = initAngle
        if self.enemy.x <= self.x:
            if angle > destAngle:
                while angle > destAngle:
                    a = centerPoint[0] + (radius * math.cos(angle))
                    b = centerPoint[1] + (radius * math.sin(angle))
                    self.pointlist.append([a,b])
                    angle -= interval
                    angle = round(angle, 1)
            else:
                while angle < destAngle:
                    a = centerPoint[0] + (radius * math.cos(angle))
                    b = centerPoint[1] + (radius * math.sin(angle))
                    self.pointlist.append([a,b])
                    angle += interval
                    angle = round(angle, 1)
        else:
            angle = -angle
            if angle > destAngle:
                while angle > destAngle:
                    a = centerPoint[0] + (radius * math.cos(angle))
                    b = centerPoint[1] + (radius * math.sin(angle))
                    self.pointlist.append([a,b])
                    angle -= interval
                    angle = round(angle, 1)
            else:
                while angle < destAngle:
                    a = centerPoint[0] + (radius * math.cos(angle))
                    b = centerPoint[1] + (radius * math.sin(angle))
                    self.pointlist.append([a,b])
                    angle += interval
                    angle = round(angle, 1)
        self.pointlist.append(destination)

    def rotate(self):
        # if self.tower.type != 'Wind':
        #     self.angle = 180 + Utilities.get_rotation(self, self.enemy)
        if self.tower.type == 'Wind' and self.tower.upgradePath != 'WindDamage':
            self.rot.origin = self.center
            self.rot.angle = self.angle

    def removeShot(self, *args):
        if not self.complete:
            self.size = (0,0)
            if self.road and self.tower.upgradePath == 'FireDamage':
                    for road in self.road:
                        if not road.iceNeighbor:
                            road.createBurnRoad(self)
            if self in Localdefs.shotlist:
                Localdefs.shotlist.remove(self)
            if self.parent:
                Map.mapvar.shotcontainer.remove_widget(self)
            self.complete = True
            self.tower.shotcount -= 1

    def checkHit(self, *args):
        #print "checkhit", self.center, "angle", self.rot.angle
        if self.tower.upgradePath == 'FireDamage':
            self.hitEnemy(self.enemy)
            self.source = "towerimgs/Fire/explosion.png"
            self.size = (20, 20)
            self.explosionAnimation = Animation(size=(60, 60), center=self.center, duration=.2)
            self.explosionAnimation.bind(on_complete=self.removeShot)
            self.explosionAnimation.start(self)
            for road in Map.mapvar.roadcontainer.children:
                if self.collide_widget(road):
                    self.road.append(road)
        elif self.tower.type != 'Wind':
            if self.enemy.collide_widget(self):
                if self.tower.push > 0:
                        dir = (self.enemy.center[0] - self.tower.center[0], self.enemy.center[1] - self.tower.center[1])
                        if dir[0] <= 0:
                            self.pushx = self.tower.push
                        elif dir[0] > 0:
                            self.pushx = -self.tower.push
                        if dir[1] <= 0:
                            self.pushy = self.tower.push
                        elif dir[1] > 0:
                            self.pushy = -self.tower.push
                self.hitEnemy(self.enemy)
        else: #wind gust
            for enemy in Localdefs.flyinglist:
                if not enemy.recovering and enemy not in self.hitlist:
                    if enemy.collide_widget(self):
                        self.hitlist.append(enemy)
                        dir = (enemy.center[0] - self.tower.center[0], enemy.center[1] - self.tower.center[1])
                        if self.pushx == 0:
                            if dir[0] <= 0:
                                self.pushx = self.tower.push
                            elif dir[0] > 0:
                                self.pushx = -self.tower.push
                        if self.pushy == 0:
                            if dir[1] <=0:
                                self.pushy = self.tower.push
                            elif dir[1] >0:
                                self.pushy = -self.tower.push
                        self.hitEnemy(enemy)
