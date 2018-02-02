import Utilities
import os, math
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
        self.size = (150,150)
        self.pos = tower.pos
        self.tower = tower
        self.center = tower.center
        self.damage = tower.damage
        self.attacktype = tower.attacktype
        Map.mapvar.cloudcontainer.add_widget(self)
        with self.canvas:
            self.color = Color(a=0)
            self.rect = Rectangle(source = os.path.join('towerimgs', 'Ice', 'cloud.png'),size = self.size, pos = self.pos)
        self.animation = Animation (a = .6, duration = 3) \
                         + Animation (a= .3, duration=3)
        self.animation.repeat = True

    def takeTurn(self):
        '''Move the shot toward the enemy'''
        # self.move()
        # self.rotate()
        self.shotAnimate()

    def enable(self):
        self.tower.active = True
        self.color.a = 0
        self.animation.start(self.color)

    def disable(self):
        self.tower.active = False
        self.animation.bind(on_complete= self.animation.cancel(self.color))

    def hitEnemy(self, enemy):
        '''Reduces enemy health by damage - armor'''
        if self.tower.attacktype == "slow":
            enemy.slowtimers.append(enemy)
            if enemy.image.color != [0,0,1,1]:
                enemy.image.color = [0,0,1,1]
            enemy.slowtime = 3
        enemy.health -= max(self.damage - enemy.armor, 0)
        enemy.checkHealth()

