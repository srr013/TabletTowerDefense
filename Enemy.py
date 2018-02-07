import os
import math

import localdefs
import Utilities
import Player
import Map
import SenderClass
import GUI

from kivy.graphics import *
from kivy.uix.widget import Widget
from kivy.animation import Animation

class Enemy(Widget):
    def __init__(self,**kwargs):
        super(Enemy,self).__init__()
        #if self.imgindex == 2:
            #self.animation = Animation.Animate(folder = os.path.join("enemyimgs", "Bird A"))
            #self.image = self.animation.adjust_images("right")
        self.specialSend = kwargs['specialSend']
        self.size = (25, 25)
        if not self.specialSend:
            self.curnode = 0
            self.rect = Utilities.createRect(self.movelist[self.curnode], self.size, instance=self)
            self.pos = self.movelist[self.curnode]
        self.image.size = self.size
        self.add_widget(self.image)
        Map.mapvar.enemycontainer.add_widget(self)
        self.starthealth = self.health
        self.startspeed = self.speed

        self.slowtimers = list()
        self.slowpercent = 1
        self.slowtime = 0
        self.stuntimers = list()
        self.stuntime = 0
        #self.poisontimer = None

        self.distBase = self.distToBase()
        self.explosionlength = 1
        self.isair = False
        self.isAlive = True
        self.pushed = [0,0]
        self.hit = False
        self.recovering = False
        self.pushtimer = 1.5
        self.anim = self.move()

        with self.canvas.before:
            PushMatrix()
            self.rot = Rotate()
            self.rot.axis = (0, 0, 1)
            self.rot.angle = 0
            self.rot.origin = self.center
        with self.canvas: #draw health bars
            Color(0,0,0,.6)
            self.healthbar = Line(points = [self.x, self.y+self.height+2, self.x+self.width, self.y+self.height+2], width = 2, cap=None)
            Color(1,1,1,1)
            self.remaininghealth = Line(points = [self.x, self.y+self.height+2, self.x+self.width, self.y+self.height+2], width = 1.4, cap=None)
        with self.canvas.after:
            PopMatrix()


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
            self.image.pos = self.pos
            self.rect_centerx, self.rect_centery = self.center

    def workSlowTimers(self):
        '''Adjust slow already applied to enemy
        Frametime: the amount of time elapsed per frame'''
        for st in self.slowtimers:
            st.slowtime -= Player.player.frametime
            if st.slowtime<=0:
                self.slowtimers.remove(st)
                self.image.color=[1,1,1,1]

    def workStunTimers(self):
        for st in self.stuntimers:
            st.stuntime -= Player.player.frametime
            if st.stuntime <=0:
                self.stuntimers.remove(st)
                self.anim = self.move()


    def distToBase(self):
        '''Determine distance to the end point using hypotenuse of xs and ys. Returns the distance.'''
        return math.sqrt(math.pow(Map.mapvar.basepoint[0]*30-self.rect_centerx,2)+math.pow(Map.mapvar.basepoint[1]*30-self.rect_centery,2))


    def move(self,*args):
        '''Moves the enemy down the generated move list
        Frametime: the amount of time elapsed per frame'''
        # self.moveamt_x = round(self.speed * Player.player.frametime, 2)
        # self.moveamt_y = round(self.speed * Player.player.frametime, 2)
        if self.stuntime>0:
            return

        self.curnode+=1
        distToTravel = 30 #abs(self.pos[0] - self.movelist[self.curnode][0]+self.pos[1] - self.movelist[self.curnode][1])
        duration = distToTravel/(self.speed*self.slowpercent)
        self.anim = Animation(pos=self.movelist[self.curnode], duration = duration, transition="linear")

        if self.curnode >= len(self.movelist) - 1:
            self.anim.bind(on_complete=self.checkHit)
        else:
            self.anim.bind(on_complete=self.move)

        self.anim.start(self)
        self.image.pos = self.pos
        self.rect_centerx, self.rect_centery = self.center

        return self.anim

    def checkHit(self,*args):
        if Map.mapvar.baseimg.collide_widget(self.image):
            Player.player.health -= 1
            GUI.gui.myDispatcher.Health = str(Player.player.health)
            Map.mapvar.enemycontainer.remove_widget(self)
            if Player.player.health <= 0:
                Player.player.die()
            return

    def pushMove(self):
        if self.recovering == False:
            print ("pushed")
            self.anim.cancel(self)
            self.curnode -=1
            self.pushAnimation = Animation(pos = (self.x-self.pushed[0], self.y-self.pushed[1]), duration = .4, t="linear")
            self.pushAnimation.start(self)
            self.pushAnimation.bind(on_progress=self.imagepos)
            self.pushAnimation.bind(on_complete=self.move)
            self.curnode -=1
            self.recovering = True
        self.pushtimer -= Player.player.frametime
        if self.pushtimer <= 0:
            self.recovering = False
            self.pushtimer = 1.0
            self.pushed = [0, 0]
            self.hit = False
    def imagepos(self, *args):
        self.image.pos = self.pos

    def checkHealth(self):
        '''Checks enemy health and kills the enemy if health <=0'''
        if self.health<=0:
            self.die()

    def die(self):
        '''If enemy runs out of health add them to explosions list, remove from enemy list, and add money to player's account'''
        if self.type == 'Splinter' and self.isAlive:
            self.isAlive = False
            self.splinter()

        if self.isair == True and self.isAlive == True:
            localdefs.flyinglist.remove(self)
        #localdefs.explosions.append([(self.rect_centerx, self.rect_centery),self.explosionlength, self])
        self.isAlive = False
        self.anim.cancel_all(self)
        self.remove_widget(self.image)
        Map.mapvar.enemycontainer.remove_widget(self)
        Player.player.money += self.reward
        Player.player.score += self.points
        GUI.gui.myDispatcher.Money = str(Player.player.money)
        GUI.gui.myDispatcher.Score = str(Player.player.score)

    def updateHealthBar(self):
        self.healthbar.points = [self.x, self.y + self.height + 2, self.x + self.width, self.y + self.height + 2]
        self.percentHealthRemaining = self.health/self.starthealth
        self.remaininghealth.points = [self.x, self.y+self.height+2, self.x+self.width*self.percentHealthRemaining, self.y+self.height+2]



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


class Standard(Enemy):
    defaultNum = 10
    deploySpeed = 1
    health = 100
    speed = 30
    armor = 0
    reward = 5
    points = 10
    imagesrc = os.path.join("enemyimgs","medbox.png")

    def __init__(self,**kwargs):
        self.type = 'Standard'
        self.defaultNum = Standard.defaultNum
        self.deploySpeed = Standard.deploySpeed
        self.health = Standard.health #100 HP per enemy
        self.speed = Standard.speed
        self.armor = Standard.armor
        self.reward = Standard.reward #cash granted per kill
        self.points = Standard.points #points granted per kill
        self.imagesrc = Standard.imagesrc
        self.image = Utilities.imgLoad(self.imagesrc)
        self.isBoss = False
        self.movelistNum = 0
        self.movelist = Map.mapvar.pointmovelists[self.movelistNum] #0 for ground, 1 for air
        super(Standard, self).__init__(**kwargs)


class Airborn(Enemy):
    defaultNum = 10
    deploySpeed = 1
    health = 100
    speed = 30
    armor = 0
    reward = 5
    points = 10
    imagesrc = os.path.join("enemyimgs", "airborn.png")
    def __init__(self, **kwargs):
        self.type = 'Airborn'
        self.defaultNum = Airborn.defaultNum  # 10 enemies per wave
        self.deploySpeed = Airborn.deploySpeed
        self.health = Airborn.health  # 100 HP per enemy
        self.speed = Airborn.speed
        self.armor = Airborn.armor
        self.reward = Airborn.reward  # cash granted per kill
        self.points = Airborn.points  # points granted per kill
        self.imagesrc = Airborn.imagesrc
        self.image = Utilities.imgLoad(self.imagesrc)
        self.movelistNum = 1
        self.isBoss = False
        self.movelist = Map.mapvar.pointmovelists[self.movelistNum]  # 0 for ground, 1 for air
        super(Airborn, self).__init__(**kwargs)
        self.isair = True
        localdefs.flyinglist.append(self)


class Splinter(Enemy):
    defaultNum = 3
    deploySpeed = 3
    health = 300
    speed = 25
    armor = 5
    reward = 10
    points = 20
    imagesrc = os.path.join("enemyimgs", "largebox.png")
    def __init__(self, **kwargs):
        self.type = 'Splinter'
        self.defaultNum = Splinter.defaultNum  # 10 enemies per wave
        self.deploySpeed = Splinter.deploySpeed
        self.health = Splinter.health  # 100 HP per enemy
        self.speed = Splinter.speed
        self.armor = Splinter.armor
        self.reward = Splinter.reward  # cash granted per kill
        self.points = Splinter.points  # points granted per kill
        self.imagesrc = Splinter.imagesrc
        self.image = Utilities.imgLoad(self.imagesrc)
        self.isBoss = False
        self.movelistNum = 0
        self.movelist = Map.mapvar.pointmovelists[self.movelistNum]  # 0 for ground, 1 for air
        super(Splinter, self).__init__(**kwargs)


    #break the Splinter apart when it dies. 15 Crowd are released.
    def splinter(self):
        SenderClass.Sender(specialSend = True, enemytype='Crowd', pos=self.pos, curnode = self.curnode, number=8, deploySpeed = 0)


class Strong(Enemy):
    defaultNum = 5
    deploySpeed = 3
    health = 400
    speed = 20
    armor = 10
    reward = 10
    points = 20
    imagesrc = os.path.join("enemyimgs", "largebox.png")
    def __init__(self,**kwargs):
        self.type = 'Strong'
        self.defaultNum = Strong.defaultNum
        self.deploySpeed = Strong.deploySpeed
        self.health = Strong.health #100 HP per enemy
        self.speed = Strong.speed
        self.armor = Strong.armor
        self.reward = Strong.reward #cash granted per kill
        self.points = Strong.points #points granted per kill
        self.imagesrc = Strong.imagesrc
        self.image = Utilities.imgLoad(self.imagesrc)
        self.movelistNum = 0
        self.movelist = Map.mapvar.pointmovelists[self.movelistNum] #0 for ground, 1 for air
        self.isBoss = False ###is this needed?
        super(Strong, self).__init__(**kwargs)

class Crowd (Enemy):
    defaultNum = 20
    deploySpeed = .4
    health = 25
    speed = 30
    armor = 0
    reward = 3
    points = 6
    imagesrc = os.path.join("enemyimgs","smallbox.png")
    def __init__(self,**kwargs):
        self.type = 'Crowd'
        self.defaultNum = Crowd.deploySpeed
        self.health = Crowd.health #100 HP per enemy
        self.speed = Crowd.speed
        self.armor = Crowd.armor
        self.reward = Crowd.reward #cash granted per kill
        self.points = Crowd.points #points granted per kill
        self.imagesrc = Crowd.imagesrc
        self.image = Utilities.imgLoad(self.imagesrc)
        self.movelistNum = 0
        self.movelist = Map.mapvar.pointmovelists[self.movelistNum] #0 for ground, 1 for air
        self.isBoss = False

        if kwargs['specialSend']:
            self.size = (20,20)
            self.pos = kwargs['pos']
            self.curnode = kwargs['curnode']
            self.rect = Utilities.createRect(self.pos, self.size, instance=self)

        super(Crowd, self).__init__(**kwargs)