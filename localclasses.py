import pygame
import os
import sys
from pygame.locals import *
from localdefs import *
import random
import TowerAbilities
import math, operator
import Animation
from MainFunctions import gui

class Enemy(Path):
    def __init__(self,wave,letter):
        Path.__init__(self)
        self.imgindex = int(mapvar.mapdict['wave'+str(wave)+letter][6])
        self.isair = False
        self.letter = letter

        ##making all enemies look like bird for now
        if self.imgindex == 2:
            self.animation = Animation.Animate(folder = os.path.join("enemyimgs", "Bird A"))
            self.image = self.animation.adjust_images("right")
        else:
            self.image = imgLoad(os.path.join("enemyimgs","spider.png"))
            sprite_sheet = split_sheet(self.image, (32,32),7,4)
            self.animation = Animation.Animate(spritesheet = sprite_sheet, startframe=0, endframe=2, defaultrotation=90)
            self.image = self.animation.adjust_images("right")

        self.curnode = 0
        if letter=='a':
            self.movelist = mapvar.pointmovelists[0]
        elif letter=='b':
            self.movelist = mapvar.pointmovelists[1]
            self.isair = True
        elif letter=='c':
            self.movelist = mapvar.pointmovelists[2]
        elif letter=='d':
            self.movelist = mapvar.pointmovelists[3]
        self.rect = self.image.get_rect(center=(self.movelist[self.curnode]))
        self.rect = self.rect.inflate((-5,-10))
        enemylist.append(self)
        self.cost = mapvar.mapdict['wave'+str(wave)+letter][5]
        self.health = mapvar.mapdict['wave'+str(wave)+letter][2]
        self.speed = mapvar.mapdict['wave'+str(wave)+letter][3]
        self.starthealth = self.health
        self.startspeed = self.speed
        self.route = 1
        self.slowtimers = list()
        self.slowpercent = .2
        self.slowtime = 0
        self.holdcentx = self.rect.centerx*1.0
        self.holdcenty = self.rect.centery*1.0
        self.poisontimer = None
        self.armor = mapvar.mapdict['wave'+str(wave)+letter][4]
        self.points = 10 #placeholder. Will need to dynamically update this based on enemy and level
        self.distBase = self.distToBase()

    def takeTurn(self,frametime):
        self.workSlowTimers(frametime)
        self.move(frametime)
    def workSlowTimers(self,frametime):
        for st in self.slowtimers:
            st.slowtime -= frametime
            if st.slowtime<=0:
                self.slowtimers.remove(st)
    def distToBase(self):
        return math.sqrt(math.pow(mapvar.basepoint[0]*30-self.rect.x,2)+math.pow(mapvar.basepoint[1]*30-self.rect.y,2))


    def move(self,frametime):
        ##right now just using a for ground troops, b for flying. Update movelist for ground each move to ensure the latest movelist is used.
        if self.letter=='a':
            self.movelist = mapvar.pointmovelists[0]
        if self.slowtime > 0:
            moveamt = self.slowpercent*frametime*self.speed
        else:
            moveamt = self.speed*frametime
        ##Check to see if the enemy hits the Base and remove enemy and decrement player health
        for i in range(int(self.speed*30)):
            if mapvar.baserect.colliderect(self.rect):
                enemylist.remove(self)
                player.health -= 1
                if player.health<=0:
                    player.die()
                mapvar.wavesSinceLoss = 0
                return

            #move enemy x and y based on the moveamt calculated above
            if self.rect.collidepoint(self.movelist[self.curnode+1]):
                self.curnode+=1
            if self.movelist[self.curnode+1][0]>self.rect.centerx:
                self.holdcentx+=moveamt
                self.image = self.animation.adjust_images("right")
                self.rect.centerx = int(self.holdcentx)
            elif self.movelist[self.curnode+1][0]<self.rect.centerx:
                self.holdcentx-=moveamt
                self.image = self.animation.adjust_images("left")
                self.rect.centerx = int(self.holdcentx)
            if self.movelist[self.curnode+1][1]>self.rect.centery:
                self.holdcenty+=moveamt
                self.image = self.animation.adjust_images("down")
                self.rect.centery = int(self.holdcenty)
            elif self.movelist[self.curnode+1][1]<self.rect.centery:
                self.holdcenty-=moveamt
                self.image = self.animation.adjust_images("up")
                self.rect.centery = int(self.holdcenty)
    def checkHealth(self):
        if self.health<=0:
            player.kill_score += self.points
            self.die()
    ##If enemy runs out of health add them to explosions list, remove from enemy list, and add money to player's account
    def die(self):
        explosions.append(self.rect)
        if self in enemylist:
            enemylist.remove(self)
        player.money+=(self.cost)

class Tower():
    def __init__(self,tl):
        self.rangeMod = 0
        self.damageMod = 0
        self.timeMod = 0
        self.targetTimer = 0
        player.money-=self.cost
        self.rect = self.image.get_rect(topleft=tl)
        self.squareheight = 2
        self.squarewidth = 2
        self.towerwalls = self.genWalls()
        towerlist.append(self)
        self.totalspent = self.cost
        self.abilities = list()
        self.buttonlist = list()
        self.upgrades = list()
        self.reload()
        self.type = "tower"
        self.attackair = True
        self.attackground = True
        self.buttons = gui.createTowerButtons(self)


    def genWalls(self):
        walls = []
        h = self.squareheight - 1
        while h >= 0:
            w = self.squarewidth - 1
            while w >= 0:
                wall = (((self.rect.centerx) / squsize) - w, (self.rect.centery) / squsize - h)
                walls.append(wall)
                w -= 1
            h -= 1
        return walls

    ##called when a tower is selected via mouse
    def genButtons(self,screen):
        font = pygame.font.Font(None,20)
        ##generate a list of abilities from the currently hardcoded list in TowerAbilities.py
        ##doesFit() returns true if the tower is not in tower.upgrades list, which keeps track of whether the tower has been upgraded yet
        abilitylist = [i for i in TowerAbilities.TowerAbilityList if (i.doesFit(self) and (i.shortname in player.modDict['towerAbilities']))]
        ##buttonnum could change w/ tower abilities (=len(abilitylist) but this makes for inconsistent ability placement on the circle
        buttonnum = 5 ##UPDATE this number if additional functions are added that apply to all towers
        if buttonnum:
            inddeg = (2.0*math.pi)/buttonnum
            self.buttonlist = list()
            radius = 50
            ##generate the list of abilities per tower
            for ind,ta in enumerate(abilitylist):
                try:taimg = imgLoad(os.path.join("upgradeicons",ta.shortname+".jpg"))
                except:
                    taimg = pygame.Surface((20,20))
                    taimg.fill((90,90,255))
                tarect = pygame.Rect((0,0),(20,20))
                tarect.center=(self.rect.centerx,self.rect.centery)
                tarect.move_ip(radius*math.cos((ind+1)*inddeg),radius*math.sin((ind+1)*inddeg))
                ##setup text to the side of the upgradeicon
                info = font.render("%s: -%dcr" % (ta.name,ta.cost(self)),1,(0,0,0))
                infopos = info.get_rect(center=(self.rect.centerx+(radius+info.get_width()+10)*math.cos((ind+1)*inddeg),self.rect.centery+(radius+info.get_height()+10)*math.sin((ind+1)*inddeg)))
                infopos.left=max(0,infopos.left)
                infopos.right=min(scrwid,infopos.right)
                infopos.top=max(0,infopos.top)
                infopos.bottom=min(scrhei,infopos.bottom)
                self.buttonlist.append((taimg,tarect,info,infopos,ta.apply))

    ##Handles tower shooting
    def takeTurn(self,frametime,screen):
        self.targetTimer -= frametime
        ##if the rest period is up then shoot again
        if self.targetTimer<=0:
            self.targetTimer = self.startTargetTimer
            self.target()

    ##Create a sorted list of enemies based on distance from the tower. If enemy is within tower range then hit enemy
    ##check health (to see if it died), then return enemy.rect.center. Return 0 if no enemy in range.
    def target(self):
        tower=self
        sortedlist = sorted(enemylist, key=operator.attrgetter("distBase"))

        ##the distance attribute here isn't reliable. it's set above by movement.
        for enemy in sortedlist:
            if math.sqrt((self.rect.centerx-enemy.rect.centerx)**2+(self.rect.centery-enemy.rect.centery)**2)<=self.range:
                if enemy.isair and tower.attackair:
                    # create a shot and add it to the Shotlist for tracking
                    Shot(tower, enemy)
                    # if tower attacks one enemy at a time then break the loop after first
                    if tower.attacktype == "single":
                        return
                if not enemy.isair and tower.attackground:
                    #create a shot and add it to the Shotlist for tracking
                    Shot(tower, enemy)
                    #if tower attacks one enemy at a time then break the loop after first
                    if tower.attacktype == "single":
                        return
                    #if tower attacks all enemies in range then loop through all in list within range
                    elif tower.attacktype == "multi" or tower.attacktype == 'slow':
                        pass
        return

class FighterTower(Tower):
    basecost = 5
    baserange = 3*squsize
    basedamage = 1.5
    basetime = .8
    attacktype = "single"
    num_fighters = 1
    type = "Fighter"
    def __init__(self,tl):
        self.cost = self.basecost*(1-player.modDict['towerCostMod'])*(1-player.modDict['fighterCostMod'])
        self.tempimage = imgLoad(os.path.join('towerimgs','Fighter','1.png'))
        self.image = self.tempimage.copy()
        self.image.fill((255,255,255,50))
        self.image.blit(self.tempimage,(0,0))
        Tower.__init__(self,tl)
        self.attackair = False
        self.shotimage = "cannonball.png"
        self.type = "Fighter"
    def reload(self):
        self.range = (self.baserange+self.rangeMod)*(1+player.modDict['towerRangeMod'])*(1+player.modDict['fighterRangeMod'])
        self.damAmt = (self.basedamage+self.damageMod)*(1+player.modDict['towerDamageMod'])*(1+player.modDict['fighterDamageMod'])
        self.startTargetTimer = (self.basetime-self.timeMod)*(1-player.modDict['towerSpeedMod'])*(1-player.modDict['fighterSpeedMod'])
    def damage(self):
        self.damAmt = self.basedamage*self.num_fighters
        return self.damAmt


class ArcherTower(Tower):
    basecost = 10
    baserange = 5*squsize
    basedamage = 6
    basetime = 1.0
    attacktype = "single"
    type = "Archer"
    def __init__(self,tl):
        self.cost = self.basecost*(1-player.modDict['towerCostMod'])*(1-player.modDict['archerCostMod'])
        self.tempimage = imgLoad(os.path.join('towerimgs','Archer','1.png'))
        self.image = self.tempimage.copy()
        self.image.fill((255,255,255,50))
        self.image.blit(self.tempimage,(0,0))
        self.shotimage = "arrow.png"
        Tower.__init__(self,tl)
        self.type = "Archer"
    def reload(self):
        self.range = (self.baserange+self.rangeMod)*(1+player.modDict['towerRangeMod'])*(1+player.modDict['archerRangeMod'])
        self.damAmt = (self.basedamage+self.damageMod)*(1+player.modDict['towerDamageMod'])*(1+player.modDict['archerDamageMod'])
        self.startTargetTimer = (self.basetime-self.timeMod)*(1-player.modDict['towerSpeedMod'])*(1-player.modDict['archerSpeedMod'])
    def damage(self):
        return self.damAmt


class MageTower(Tower):
    basecost = 10
    baserange = 1*squsize
    basedamage = 10
    basetime = 0.5
    attacktype = "single"
    type = "Mage"

    def __init__(self,tl):
        self.cost = self.basecost*(1-player.modDict['towerCostMod'])*(1-player.modDict['mageCostMod'])
        self.tempimage = imgLoad(os.path.join('towerimgs','Mage','1.png'))
        self.image = self.tempimage.copy()
        self.image.fill((255,255,255,50))
        self.image.blit(self.tempimage,(0,0))
        Tower.__init__(self,tl)
        self.type = "Mage"
        self.shotimage = "arrow.png"
    def reload(self):
        self.range = (self.baserange+self.rangeMod)*(1+player.modDict['towerRangeMod'])*(1+player.modDict['mageRangeMod'])
        self.damAmt = (self.basedamage+self.damageMod)*(1+player.modDict['towerDamageMod'])*(1+player.modDict['mageDamageMod'])
        self.startTargetTimer = (self.basetime-self.timeMod)*(1-player.modDict['towerSpeedMod'])*(1-player.modDict['mageSpeedMod'])
    def damage(self):
        return self.damAmt


class MineTower(Tower):
    basecost = 15
    baserange = 3*squsize
    basedamage = 4
    basetime = 4
    attacktype = "multi"
    type = "Mine"
    def __init__(self,tl):
        self.cost = self.basecost*(1-player.modDict['towerCostMod'])*(1-player.modDict['mageCostMod'])
        self.tempimage = imgLoad(os.path.join('towerimgs','Mine','1.png'))
        self.image = self.tempimage.copy()
        self.image.fill((255,255,255,50))
        self.image.blit(self.tempimage,(0,0))
        Tower.__init__(self,tl)
        self.type = "Mine"
        self.shotimage = "waves.png"
        self.attackair=False
    def reload(self):
        self.range = (self.baserange+self.rangeMod)*(1+player.modDict['towerRangeMod'])*(1+player.modDict['mineRangeMod'])
        self.damAmt = (self.basedamage+self.damageMod)*(1+player.modDict['towerDamageMod'])*(1+player.modDict['mineDamageMod'])
        self.startTargetTimer = (self.basetime-self.timeMod)*(1-player.modDict['towerSpeedMod'])*(1-player.modDict['mineSpeedMod'])
    def damage(self):
        return self.damAmt


class SlowTower(Tower):
    basecost = 10
    baserange = 2*squsize
    basedamage = 0
    basetime = 1.0
    attacktype = "slow"
    type = "Slow"
    def __init__(self,tl):
        self.cost = self.basecost*(1-player.modDict['towerCostMod'])*(1-player.modDict['slowCostMod'])
        self.tempimage = imgLoad(os.path.join('towerimgs','Slow','1.png'))
        self.image = self.tempimage.copy()
        self.image.fill((255,255,255,50))
        self.image.blit(self.tempimage,(0,0))
        Tower.__init__(self,tl)
        self.attackair = True
        self.type = "Slow"
        self.shotimage = "freeze.png"

    def reload(self):
        self.range = (self.baserange+self.rangeMod)*(1+player.modDict['towerRangeMod'])*(1+player.modDict['slowRangeMod'])
        self.damAmt = (self.basedamage+self.damageMod)*(1+player.modDict['towerDamageMod'])*(1+player.modDict['slowDamageMod'])
        self.startTargetTimer = (self.basetime-self.timeMod)*(1-player.modDict['towerSpeedMod'])*(1-player.modDict['slowSpeedMod'])
    def damage(self):
        return self.damAmt


class AntiAirTower(Tower):
    basecost = 35
    baserange = 6*squsize
    basedamage = 8
    basetime = 1.0
    attacktype = "single"
    type = "AntiAir"
    def __init__(self,tl):
        self.cost = self.basecost*(1-player.modDict['towerCostMod'])*(1-player.modDict['fighterCostMod'])
        self.tempimage = imgLoad(os.path.join('towerimgs','AntiAir','1.png'))
        self.image = self.tempimage.copy()
        self.image.fill((255,255,255,50))
        self.image.blit(self.tempimage,(0,0))
        Tower.__init__(self,tl)
        self.attackair = True
        self.attackground = False
        self.type = "AntiAir"
        self.shotimage = "bolt.png"

    def reload(self):
        self.range = (self.baserange+self.rangeMod)*(1+player.modDict['towerRangeMod'])*(1+player.modDict['fighterRangeMod'])
        self.damAmt = (self.basedamage+self.damageMod)*(1+player.modDict['towerDamageMod'])*(1+player.modDict['fighterDamageMod'])
        self.startTargetTimer = (self.basetime-self.timeMod)*(1-player.modDict['towerSpeedMod'])*(1-player.modDict['fighterSpeedMod'])
    def damage(self):
        self.damAmt = self.basedamage
        return self.damAmt


available_tower_list = [ArcherTower, FighterTower,SlowTower, MineTower, AntiAirTower]
baseTowerList = [(tower.type,tower.basecost, tower.basedamage, tower.baserange, tower.basetime) for tower in available_tower_list]



class Icon():
    def __init__(self,tower):
        self.type = tower[0]
        self.base = "Tower"
        self.basecost = tower[1]
        self.basedamage = tower[2]
        self.baserange = tower[3]
        self.basetime = tower[4]
        iconlist.append(self)
        try:
            self.img = imgLoad(os.path.join('towerimgs',self.type,'1.png'))
        except:
            self.img = imgLoad(os.path.join('towerimgs','Basic','1.png'))
        self.rect = self.img.get_rect()

##my addition
##manages each shot from each tower so we can show the shot in flight.
class Shot():
    def __init__(self, tower, enemy):
        self.enemy = enemy
        self.image = imgLoad(os.path.join('towerimgs',tower.type,tower.shotimage))
        self.rect = self.image.get_rect(topleft = (tower.rect.x, tower.rect.y))
        self.shot_speed_x = squsize*2
        self.shot_speed_y = squsize*2
        self.damage = tower.damage()
        self.attacktype = tower.attacktype
        shotlist.append(self)
        self.shot_frame_count = 0
        self.last_rect_x = self.rect.x
        self.last_rect_y = self.rect.y

    ##called from towedefense.py
    def takeTurn(self,screen):
        self.move()

    ##Checks distance between shot and enemy and updates distance as needed
    def check_distance(self):
        x_dist = abs(self.enemy.rect.x - self.rect.x)
        y_dist = abs(self.enemy.rect.y - self.rect.y)
        if x_dist < self.shot_speed_x:
            self.shot_speed_x = x_dist
        if y_dist < self.shot_speed_y:
            self.shot_speed_y = y_dist

    ##moved from Tower
    # Reduces enemy health by damage - armor
    def hitEnemy(self):
        if self.attacktype == "slow":
            self.enemy.slowtimers.append(self.enemy)
            self.enemy.slowtime = 60
        self.enemy.health -= max(self.damage - self.enemy.armor, 0)
        shotlist.remove(self)
        self.enemy.checkHealth()

    ##Move the shot towards the enemy. Check for collision. Rotate the shot so it's facing the enemy (upon first flight)
    def move(self):
        self.shot_frame_count+=1
        self.check_distance()
        if self.rect.x > scrwid or self.rect.x < 0 or self.rect.y > scrhei or self.rect.y < 0:
            shotlist.remove(self)
        if self.enemy.rect.x > self.rect.x:
            self.rect.x += self.shot_speed_x
        elif self.enemy.rect.x < self.rect.x:
            self.rect.x -= self.shot_speed_x
        if self.enemy.rect.y > self.rect.y:
            self.rect.y += self.shot_speed_y
        elif self.enemy.rect.y < self.rect.y:
            self.rect.y -= self.shot_speed_y

        #could move this into init if there's a reason to
        if self.shot_frame_count < 2:
            self.image = self.rotate_image()
            self.last_rect_x = self.rect.x
            self.last_rect_y = self.rect.y

        if self.enemy.rect.colliderect(self.rect):
            self.hitEnemy()

    def rotate_image(self):
        orig_rect = self.rect
        rotation = math.atan2(self.rect.y - self.last_rect_y, self.rect.x - self.last_rect_x)*-57.3
        new_image = pygame.transform.rotate(self.image, rotation)
        #new_rect = orig_rect.copy()
        #new_rect.center = new_image.get_rect().center
        #new_image = new_image.subsurface(new_rect).copy()
        return new_image
class Timer():
    def __init__(self):
        self.timer = 0
        self.wave_length = 11
        self.curr_wave_length= int(self.wave_length)

    def updateTimer(self, wavestart):
        if wavestart == 999:
            self.timer = wavestart
            return False

        else:
            if player.pausetime > 0:
                self.curr_wave_length += player.pausetime
                return False
            else:
                self.timer = (wavestart + self.curr_wave_length) - time.time()

        if self.timer <= 0:
            self.timer = (wavestart + self.wave_length) - time.time()
            self.curr_wave_length = int(self.wave_length)
            return True

        return False