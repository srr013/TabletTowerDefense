import pygame
import os
import sys
from pygame.locals import *
import localdefs
import localclasses
import random
import Towers
import math, operator
import Animation
import Utilities
import Player
import Map
from kivy.graphics import *

from kivy.uix.widget import Widget

class Enemy(Widget):
    def __init__(self,wave,letter, **kwargs):
        super(Enemy,self).__init__(**kwargs)
        self.imgindex = int(Map.mapvar.mapdict['wave'+str(wave)+letter][6])
        self.isair = False
        self.letter = letter


        #if self.imgindex == 2:
            #self.animation = Animation.Animate(folder = os.path.join("enemyimgs", "Bird A"))
            #self.image = self.animation.adjust_images("right")

        self.curnode = 0
        if letter=='a':
            self.movelist = Map.mapvar.pointmovelists[0]
        elif letter=='b':
            self.movelist = Map.mapvar.pointmovelists[1]
            self.isair = True
        elif letter=='c':
            self.movelist = Map.mapvar.pointmovelists[2]
        elif letter=='d':
            self.movelist = Map.mapvar.pointmovelists[3]

        self.image = Utilities.imgLoad(os.path.join("enemyimgs","explosion.png"))
        self.size = (20, 20)
        self.image.size = self.size
        self.rect = Utilities.createRect(self.movelist[self.curnode], self.size, instance=self)
        self.pos = (self.rect_centerx, self.rect_centery)
        self.add_widget(self.image)
        Map.mapvar.enemycontainer.add_widget(self)

        localdefs.enemylist.append(self)
        self.cost = Map.mapvar.mapdict['wave'+str(wave)+letter][5]
        self.health = Map.mapvar.mapdict['wave'+str(wave)+letter][2]
        self.speed = Map.mapvar.mapdict['wave'+str(wave)+letter][3]+.5
        self.starthealth = self.health
        self.startspeed = self.speed
        self.route = 1
        self.slowtimers = list()
        self.slowpercent = .2
        self.slowtime = 0
        self.poisontimer = None
        self.armor = Map.mapvar.mapdict['wave'+str(wave)+letter][4]
        self.points = 10 #placeholder. Will need to dynamically update this based on enemy and level
        self.distBase = self.distToBase()
        self.explosionlength = 120 #length in frames


    def takeTurn(self):
        '''Moves the enemy and adjusts any slow applied to it
        Frametime: the amount of time elapsed per frame'''
        self.workSlowTimers()
        self.move(Player.player.frametime)
    def workSlowTimers(self):
        '''Adjust slow already applied to enemy
        Frametime: the amount of time elapsed per frame'''
        for st in self.slowtimers:
            st.slowtime -= Player.player.frametime
            if st.slowtime<=0:
                self.slowtimers.remove(st)
    def distToBase(self):
        '''Determine distance to the end point using hypotenuse of xs and ys. Returns the distance.'''
        return math.sqrt(math.pow(Map.mapvar.basepoint[0]*30-self.rect_centerx,2)+math.pow(Map.mapvar.basepoint[1]*30-self.rect_centery,2))


    def move(self,frametime):
        '''Moves the enemy down the generated move list
        Frametime: the amount of time elapsed per frame'''
        ##right now just using a for ground troops, b for flying.
        #if self.letter=='a':
        #    self.movelist = Map.mapvar.pointmovelists[0]
        if self.slowtime > 0:
            moveamt = round(self.slowpercent*frametime*self.speed,2)
        else:
            moveamt = round(self.speed*frametime,2)
        ##Check to see if the enemy hits the Base and remove enemy and decrement player health
        for i in range(int(self.speed*30)):
            if Map.mapvar.baseimg.collide_widget(self.image):
                localdefs.enemylist.remove(self)
                Player.player.health -= 1
                Map.mapvar.enemycontainer.remove_widget(self)
                if Player.player.health<=0:
                    Player.player.die()
                Map.mapvar.wavesSinceLoss = 0
                return

            #move enemy x and y based on the moveamt calculated above
            if (round(self.pos[0],0), round(self.pos[1],0))==(self.movelist[self.curnode+1]):
                self.curnode+=1
            #print ("pos,movelist", self.pos, self.movelist[self.curnode+1])
            if self.movelist[self.curnode+1][0]>self.pos[0]:
                #print ("moving right:", self.rect_centerx, self.movelist[self.curnode+1][0])
                self.rect_centerx+=moveamt
                #self.image = self.animation.adjust_images("right")
            elif self.movelist[self.curnode+1][0]<self.pos[0]:
                self.rect_centerx-=moveamt
                #self.image = self.animation.adjust_images("left")
            if self.movelist[self.curnode+1][1]>self.pos[1]:
                self.rect_centery+=moveamt
                #self.image = self.animation.adjust_images("down")
            elif self.movelist[self.curnode+1][1]<self.pos[1]:
                self.rect_centery-=moveamt
                #self.image = self.animation.adjust_images("up")
            self.pos = (self.rect_centerx,self.rect_centery)
            self.image.pos = self.pos
    def checkHealth(self):
        '''Checks enemy health and kills the enemy if health <=0'''
        if self.health<=0:
            Player.player.kill_score += self.points
            self.die()

    def die(self):
        '''If enemy runs out of health add them to explosions list, remove from enemy list, and add money to player's account'''
        localdefs.explosions.append([(self.rect_centerx, self.rect_centery),self.explosionlength, self])
        if self in localdefs.enemylist:
            localdefs.enemylist.remove(self)
        self.remove_widget(self.image)
        Map.mapvar.enemycontainer.remove_widget(self)
        Player.player.money+=(self.cost)

    def dispExplosions(self, explosion):
        '''Display any explosions in the queue, then remove them.'''
        if explosion[1] == self.explosionlength:
            self.explosionimg = Utilities.imgLoad(os.path.join("enemyimgs", 'explosion.png'))
            self.explosionimg.pos = (explosion[0][0], explosion[0][1])
            self.explosionimg.size = (20, 20)
            Map.mapvar.explosioncontainer.add_widget(self.explosionimg)

        if explosion[1] < 0:
            localdefs.explosions.remove(explosion)
            Map.mapvar.explosioncontainer.remove_widget(self.explosionimg)
        else:
            explosion[1] -= 1
