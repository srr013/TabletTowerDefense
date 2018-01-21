import Utilities
import os, math
import localdefs
import Map

from kivy.graphics import *


##manages each shot from each tower so we can show the shot in flight.
class Shot():
    def __init__(self, tower, enemy):
        self.enemy = enemy
        self.image = Utilities.imgLoad(os.path.join('towerimgs',tower.type,tower.shotimage))
        self.image.size = (15,15)
        self.image.pos = tower.pos
        Map.mapvar.shotcontainer.add_widget(self.image)
        self.shot_speed_x = 10
        self.shot_speed_y = 10
        self.damage = tower.damage
        self.attacktype = tower.attacktype
        localdefs.shotlist.append(self)
        self.shot_frame_count = 0

        with self.image.canvas.before:
            PushMatrix()
            self.rot = Rotate(axis=(0,0,1), origin=self.image.center)
        with self.image.canvas.after:
            PopMatrix()

    ##called from towedefense.py
    def takeTurn(self):
        '''Move the shot toward the enemy'''
        self.move()

    def check_distance(self):
        '''Check the distance between the shot and the enemy and update trajectory'''
        x_dist = abs(self.enemy.rect_centerx - self.image.center_x)
        y_dist = abs(self.enemy.rect_centery - self.image.center_y)
        if x_dist < self.shot_speed_x:
            self.shot_speed_x = x_dist
        if y_dist < self.shot_speed_y:
            self.shot_speed_y = y_dist

    def hitEnemy(self):
        '''Reduces enemy health by damage - armor'''
        if self.attacktype == "slow":
            self.enemy.slowtimers.append(self.enemy)
            self.enemy.slowtime = 60
        self.enemy.health -= max(self.damage - self.enemy.armor, 0)
        self.enemy.checkHealth()
        localdefs.shotlist.remove(self)
        Map.mapvar.shotcontainer.remove_widget(self.image)

    def move(self):
        '''Move the shot towards the enemy. Check for collision. Rotate the shot so it's facing the enemy (first frame only)'''
        if self.shot_frame_count < 10:
            self.rotate_image()

        self.shot_frame_count+=1
        self.check_distance()
        if self.image.center_x > Map.scrwid or self.image.center_x < 0 or self.image.center_y > Map.scrhei or self.image.center_y < 0:
            localdefs.shotlist.remove(self)
            Map.mapvar.shotcontainter.remove_widget(self.image)
        if self.enemy.rect_centerx > self.image.center_x:
            self.image.pos[0] += self.shot_speed_x
        elif self.enemy.rect_centerx < self.image.center_x:
            self.image.pos[0] -= self.shot_speed_x
        if self.enemy.rect_centery > self.image.center_y:
            self.image.pos[1] += self.shot_speed_y
        elif self.enemy.rect_centery < self.image.center_y:
            self.image.pos[1] -= self.shot_speed_y

        if self.enemy.collide_widget(self.image):
            self.hitEnemy()

    def rotate_image(self):
        '''Rotates the shot image'''
        #distance between the image and the enemy. this is "A" and "B" in the arctan equation
        x = self.image.pos[0] - self.enemy.rect_centerx
        y = self.image.pos[1] - self.enemy.rect_centery
        #calculates the rotation of the image.
        self.rot.angle=math.atan2(y, x)*57.3+180
        self.rot.origin = self.image.center

