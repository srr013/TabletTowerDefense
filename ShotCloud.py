import Utilities
import os
import math
import localdefs
import Map

import random

from kivy.graphics import *
from kivy.uix.widget import Widget
from kivy.animation import Animation

##manages each shot from each tower so we can show the shot in flight.
class ShotCloud(Widget):
    def __init__(self, tower, **kwargs):
        super(ShotCloud, self).__init__(**kwargs)
        self.tower = tower
        self.size = (tower.range*2,tower.range*2)
        self.center = tower.center
        self.damage = tower.damage
        self.attacktype = tower.attacktype
        Map.mapvar.cloudcontainer.add_widget(self)

        if self.tower.type == 'Ice':
            with self.canvas:
                self.color = Color(.4,.8,.8,0)
                self.rect = Rectangle(size = self.size, pos = self.pos)
            self.animation = Animation (rgba=[.1,.2,.7,.6],duration=2) \
                             + Animation (rgba=[.4,.8,.8,.6], duration=2)
            self.animation.repeat = True

        if self.tower.type == 'Gravity':
            with self.canvas:
                self.color = Color(.1,.1,.1,0)
                self.rect = Rectangle(size = self.size, pos = self.pos)
            self.animation = Animation (size = self.size, pos = (tower.center[0]-self.size[0]/2, tower.center[1]-self.size[1]/2), duration=self.tower.reload-.1) \
                            + Animation(size=(60, 60), pos=tower.pos, duration=.1)
            self.animation.repeat = True

    def takeTurn(self):
        self.shotAnimate()

    def enable(self):
        self.tower.active = True
        if self.tower.type == 'Ice':
            self.animation.start(self.color)
        if self.tower.type == 'Gravity':
            self.color.a = .3
            self.animation.start(self.rect)

    def disable(self):
        print ("tower disabled")
        self.tower.active = False
        self.animation.cancel_all(self.color)
        self.animation.cancel_all(self.rect)
        self.color.a = 0

    def hitEnemy(self, enemy):
        '''Reduces enemy health by damage - armor'''
        if self.tower.type == "Ice" and enemy.slowtime <= self.tower.slowtime-1:
            enemy.slowtimers.append(enemy)
            if enemy.image.color != [0,0,1,1]:
                enemy.image.color = [0,0,1,1]
            enemy.slowtime = self.tower.slowtime
            enemy.slowpercent = self.tower.slowpercent
            enemy.health -= max(self.damage - enemy.armor, 0)
            enemy.checkHealth()
        if self.tower.type == "Gravity":
            rand = True if random.randint (0,100) > 90 else False
            if rand == True:
                print ("enemy stunned")
                enemy.stuntimers.append(enemy)
                enemy.stuntime = self.tower.stuntime

            dir = (enemy.pos[0] - self.tower.pos[0], enemy.pos[1] - self.tower.pos[1])
            if dir[0] <= 0:
                self.pushx = self.tower.push
            elif dir[0] > 0:
                self.pushx = -self.tower.push
            if dir[1] <= 0:
                self.pushy = self.tower.push
            elif dir[1] > 0:
                self.pushy = -self.tower.push

            enemy.pushed = [self.pushx, self.pushy]
            enemy.health -= max(self.damage - enemy.armor, 0)
            enemy.checkHealth()

