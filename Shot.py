import Utilities
import os, math
import localdefs
import Map

from kivy.graphics import *
from kivy.uix.widget import Widget
from kivy.animation import Animation

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
        self.image.pos = self.pos
        self.add_widget(self.image)
        self.shot_speed_x = 15
        self.shot_speed_y = 15
        self.damage = tower.damage
        self.attacktype = tower.attacktype
        self.complete = False
        Map.mapvar.shotcontainer.add_widget(self)
        localdefs.shotlist.append(self)
        self.currentPointerAngle = 0
        if tower.type != 'Wind':
            with self.image.canvas.before:
                PushMatrix()
                self.rot = Rotate()
                self.rot.axis = (0, 0, 1)
                self.rot.origin=self.center
                self.rot.angle=180
            with self.image.canvas.after:
                PopMatrix()
        if tower.type == 'Wind':
            self.windAnimate()
            self.pushx = 0
            self.pushy = 0


    ##called from towedefense.py
    def takeTurn(self):
        '''Move the shot toward the enemy'''
        if self.tower.type != 'Wind':
            self.shotAnimate()

    def check_distance(self):
        '''Check the distance between the shot and the enemy and update trajectory'''
        moveallotment = 30
        x_dist = abs(self.enemy.rect_centerx+self.enemy.moveamt_x - self.pos[0])
        y_dist = abs(self.enemy.rect_centery+self.enemy.moveamt_y - self.pos[1])+5

        if x_dist >= y_dist*1.5:
            self.shot_speed_x = .7*moveallotment
            self.shot_speed_y = .3*moveallotment
        if y_dist >= x_dist*1.5:
            self.shot_speed_y = .7*moveallotment
            self.shot_speed_x = .3*moveallotment
        if x_dist < self.shot_speed_x:
            self.shot_speed_x = x_dist
        if y_dist < self.shot_speed_y:
            self.shot_speed_y = y_dist

    def hitEnemy(self, enemy):
        '''Reduces enemy health by damage - armor'''
        if self.attacktype == "slow":
            enemy.slowtimers.append(self.enemy)
            enemy.slowtime = 60
        if self.attacktype == "wind":
            enemy.pushed = [self.pushx, self.pushy]
            enemy.health -= max(self.damage - self.enemy.armor, 0)
            enemy.checkHealth()
            print("windattack", enemy.pushed, self.pushx, self.pushy)
            return
        self.enemy.health -= max(self.damage - self.enemy.armor, 0)
        self.enemy.checkHealth()
        localdefs.shotlist.remove(self)
        Map.mapvar.shotcontainer.remove_widget(self)

    def shotAnimate(self):
        self.angle = Utilities.get_rotation(self, self.enemy)
        self.currentPointerAngle = self.currentPointerAngle + self.angle
        self.rot.origin = self.center
        self.rot.angle +=self.angle
        if self.enemy.collide_widget(self):
            self.hitEnemy(self.enemy)

        anim = Animation(pos = self.enemy.pos, duration=.2)
        anim.start(self)
        self.image.pos = self.pos
        self.image.size = self.size

    def windAnimate(self):
        #self.angle = Utilities.get_rotation(self, self.enemy)
        #self.currentPointerAngle = self.currentPointerAngle + self.angle
        #self.rot.origin = self.center
        #self.rot.angle += self.angle
        dest = [0,0]
        if self.enemy.pos[0] < self.pos[0]:
            dest[0] = self.enemy.pos[0] - 50
        elif self.enemy.pos[0] > self.pos[0]:
            dest[0] = self.enemy.pos[0] + 100
        if self.enemy.pos[1] > self.pos[1]:
            dest[1] = self.enemy.pos[1] + 100
        elif self.enemy.pos[1] < self.pos[1]:
            dest[1] = self.enemy.pos[1] - 50

        print (dest)
        self.anim = Animation(pos=dest, size = (150,150) ,duration = 1)
        self.anim.start(self.image)
        self.anim.bind(on_complete = self.removeWind)
        self.anim.bind(on_progress = self.checkWindHit)

        self.image.pos = self.pos
        self.image.size = self.size

    def removeWind(self, *args):
        if not self.complete:
            self.complete = True
            self.tower.shotcount -= 1
            Map.mapvar.shotcontainer.remove_widget(self)
            localdefs.shotlist.remove(self)


    def checkWindHit(self, *args):
        for enemy in localdefs.flyinglist:
            if enemy.collide_widget(self.image):
                if self.pushx == 0:
                    dir = (enemy.pos[0] - self.tower.pos[0], enemy.pos[1] - self.tower.pos[1])
                    if dir[0] <= 0:
                        self.pushx = self.tower.push
                    elif dir[0] > 0:
                        self.pushx = -self.tower.push
                if self.pushy == 0:
                    dir = (enemy.pos[0] - self.tower.pos[0], enemy.pos[1] - self.tower.pos[1])
                    if dir[1] <=0:
                        self.pushy = self.tower.push
                    elif dir[1] >0:
                        self.pushy = -self.tower.push
                self.hitEnemy(enemy)
