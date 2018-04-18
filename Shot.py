import os
from kivy.animation import Animation
from kivy.graphics import *
from kivy.uix.widget import Widget

import Localdefs
import Map
import Utilities
import Player

##manages each shot from each tower so we can show the shot in flight.
class Shot(Widget):
    def __init__(self, tower, enemy, **kwargs):
        super(Shot, self).__init__(**kwargs)
        self.enemy = enemy
        self.tower = tower
        self.size = (10,10)
        self.center = tower.center
        self.image = Utilities.imgLoad(os.path.join('towerimgs',tower.type,tower.shotimage))
        self.image.allow_stretch = True
        self.image.size = self.size
        self.image.center = self.center
        self.add_widget(self.image)
        self.damage = tower.damage
        self.attacktype = tower.attacktype
        self.complete = False
        Map.mapvar.shotcontainer.add_widget(self)
        Localdefs.shotlist.append(self)
        self.currentPointerAngle = 0
        self.bind(pos = self.binding)
        # if tower.type != 'Wind':
        #     with self.image.canvas.before:
        #         PushMatrix()
        #         self.rot = Rotate()
        #         self.rot.axis = (0, 0, 1)
        #         self.rot.origin=self.image.center
        #         self.rot.angle=180
        #     with self.image.canvas.after:
        #         PopMatrix()

        if tower.type == 'Wind':
            self.speed = 250
            self.pushx = 0
            self.pushy = 0
            self.facing = self.tower.towerGroup.facing
            with self.image.canvas.before:
                PushMatrix()
                self.rot = Rotate()
                self.rot.axis = (0, 0, 1)
                self.rot.origin=self.center
                self.rot.angle = 0
            with self.image.canvas.after:
                PopMatrix()

        self.shotAnimate()


    def takeTurn(self):
        #if self.tower.type != 'Wind':
        self.rotate()

    def binding(self, *args):
        self.image.center = self.center
        self.image.size = self.size

    def hitEnemy(self, enemy):
        '''Reduces enemy health by damage - armor'''
        Player.player.analytics.gameDamage += self.damage
        enemy.health -= max(self.damage - (self.damage*(self.enemy.armor/100)), 0)
        enemy.checkHealth()
        if self.tower.type == "Wind":
            enemy.pushed = [self.pushx, self.pushy]
        else:
            self.removeShot()

    def shotAnimate(self):
        if self.tower.type == 'Wind':
            dest = [0,0]
            self.angle = 0
            if self.facing == 'l':
                dest[0] = 0
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
                dest[1] = 0
                self.angle = 270

            self.rot.angle = self.angle

            distToTravel = int(abs(self.pos[0] - dest[0] + self.pos[1] - dest[1]))
            duration = float(distToTravel) / self.speed
            self.anim = Animation(pos=(dest[0], dest[1]), size=(60,60), duration=duration)
            self.anim.bind(on_complete=self.removeShot)
            self.anim.bind(on_progress=self.checkHit)


        if self.tower.type != 'Wind':
            self.rotate()
            self.anim = Animation(center=self.enemy.center, duration=.2)
            self.anim.bind(on_complete=self.checkHit)

        self.anim.start(self)

    def rotate(self):
        # if self.tower.type != 'Wind':
        #     self.angle = 180 + Utilities.get_rotation(self, self.enemy)
        if self.tower.type == 'Wind':
            self.rot.origin = self.image.center
            self.rot.angle = self.angle

    def removeShot(self, *args):
        if not self.complete:
            if self in Localdefs.shotlist:
                Localdefs.shotlist.remove(self)
            Map.mapvar.shotcontainer.remove_widget(self)
            self.complete = True
            self.tower.shotcount -= 1


    def checkHit(self, *args):
        #print "checkhit", self.center, self.image.center, self.size, self.image.size, "angle", self.rot.angle
        if self.tower.type != 'Wind':
            if self.enemy.collide_widget(self):
                self.hitEnemy(self.enemy)
        else:
            for enemy in Localdefs.flyinglist:
                if not enemy.hit:
                    if enemy.collide_widget(self):
                        enemy.hit = True
                        if self.pushx == 0:
                            dir = (enemy.center[0] - self.tower.center[0], enemy.center[1] - self.tower.center[1])
                            if dir[0] <= 0:
                                self.pushx = self.tower.push
                            elif dir[0] > 0:
                                self.pushx = -self.tower.push
                        if self.pushy == 0:
                            dir = (enemy.center[0] - self.tower.center[0], enemy.center[1] - self.tower.center[1])
                            if dir[1] <=0:
                                self.pushy = self.tower.push
                            elif dir[1] >0:
                                self.pushy = -self.tower.push
                        self.hitEnemy(enemy)
