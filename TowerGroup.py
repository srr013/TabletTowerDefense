import operator
import os
import random
from kivy.animation import Animation
from kivy.graphics import *

import Localdefs
import Map
import Player
import Shot
import Utilities


class TowerGroup():
    def __init__(self, tower):
        self.tower = tower
        self.towerSet = set()
        self.towerType = tower.type
        Localdefs.towerGroupDict[self.towerType].append(self)
        self.dmgModifier = 1
        self.reloadModifier = 1
        self.rangeModifier = 1
        self.pushModifier = 1
        self.slowTimeModifier = 1
        self.slowPercentModifier = 1
        self.stunTimeModifier = 1
        self.adjacentRoads = set()
        self.adjacentRoadFlag = True
        self.active = False
        self.targetTimer = 0
        self.facing = 'l'
        self.towersNeedingAnim = []

    def updateTowerGroup(self):
        self.updateList()
        self.updateModifiers()

    def updateList(self):
        for tower in Localdefs.towerlist:
            if tower in self.towerSet and tower.towerGroup != self:
                self.towerSet.remove(tower)
            if tower not in self.towerSet and tower.towerGroup == self:
                if self.active and self.towerType == 'Gravity':
                    self.active = False
                    for t in self.towerSet:
                        t.animation.repeat = False
                if self.active and self.towerType == 'Wind':
                    for t in self.towerSet:
                        t.turret.source = os.path.join('towerimgs', self.towerType, "turret.gif")
                self.towerSet.add(tower)
        if self.towerType == 'Ice':
            self.getAdjacentRoads()

    def removeTowerGroup(self):
        Localdefs.towerGroupDict[self.towerType].remove(self)

    def updateModifiers(self):
        self.dmgModifier = 1 + (len(self.towerSet) - 1) * .05
        self.reloadModifier = 1 - (len(self.towerSet) - 1) * .05
        self.rangeModifier = 1 + (len(self.towerSet) - 1) * .05
        self.pushModifier = 1 + (len(self.towerSet) - 1) * .05
        self.slowTimeModifier = 1 + (len(self.towerSet) - 1) * .05
        self.slowPercentModifier = 1 + (len(self.towerSet) - 1) * .05
        self.stunTimeModifier = 1 + (len(self.towerSet) - 1) * .05

        for tower in self.towerSet:
            tower.updateModifiers()

    def target(self):
        '''Create a sorted list of enemies based on distance from the tower. If enemy is within tower range then hit enemy'''
        sortedlist = sorted(Map.mapvar.enemycontainer.children, key=operator.attrgetter("distBase"))
        self.in_range_air = 0
        self.in_range_ground = 0

        for tower in self.towerSet:
            if tower.attacktype != 'multi':
                return
            if tower.totalUpgradeTime > 0:
                return
            for enemy in sortedlist:
                if Utilities.in_range(tower, enemy):
                    if enemy.isair and tower.attackair:
                        self.in_range_air += 1
                        if self.active:
                            self.hitEnemy(tower, enemy)
                        if not self.active:
                            self.enable()
                        tower.shotcount += 1

                    if not enemy.isair and tower.attackground:
                        self.in_range_ground += 1
                        if self.active:
                            self.hitEnemy(tower, enemy)
                        if not self.active:
                            self.enable()
                        tower.shotcount += 1

                    if tower.shotcount > 0:
                        self.targetTimer = tower.reload
                        if self.towersNeedingAnim:
                            self.disable()
                            self.towersNeedingAnim = []

                if tower.shotcount >= tower.allowedshots:
                    break
        if self.in_range_ground == 0 and self.in_range_air == 0 and self.active:
            self.disable()
        if self.in_range_air == 0 and self.towerType == 'Wind' and self.active:
            self.disable()

    def hitEnemy(self, tower, enemy):
        '''Reduces enemy health by damage - armor'''
        if tower.type == "Ice" and enemy.slowtime <= tower.slowtime - 1:
            enemy.slowtimers.append(enemy)
            if enemy.image.color != [0, 0, 1, 1]:
                enemy.image.color = [0, 0, 1, 1]
            enemy.slowtime = tower.slowtime
            enemy.slowpercent = tower.slowpercent
            enemy.health -= max(tower.damage - enemy.armor, 0)
            enemy.checkHealth()
        if tower.type == "Gravity":
            rand = True if random.randint(0, 100) > 90 else False
            if rand == True:
                enemy.stuntimers.append(enemy)
                enemy.stuntime = tower.stuntime
                if enemy.anim:
                    enemy.anim.cancel_all(enemy)
                enemy.addStunImage()
            dir = (enemy.pos[0] - tower.pos[0], enemy.pos[1] - tower.pos[1])
            pushx = pushy = 0
            if dir[0] <= 0:
                pushx = tower.push
            elif dir[0] > 0:
                pushx = -tower.push
            if dir[1] <= 0:
                pushy = tower.push
            elif dir[1] > 0:
                pushy = -tower.push
            enemy.pushed = [pushx, pushy]
            enemy.health -= max(tower.damage - enemy.armor, 0)
            enemy.checkHealth()

        if tower.type == 'Wind':
            Shot.Shot(tower, enemy)

    def enable(self):
        self.active = True
        if self.towerType == 'Ice':
            self.genRoadList()
        if self.towerType == 'Gravity':
            self.targetTimer = self.tower.reload
            for tower in self.towerSet:
                self.animateGravity(tower)
        if self.towerType == 'Wind':
            self.targetTimer = 0
            for tower in self.towerSet:
                tower.turret.source = os.path.join('towerimgs', self.towerType, "turret.gif")

    def animateGravity(self, tower):
        tower.animation = Animation(size=(Map.mapvar.squsize * 3, Map.mapvar.squsize * 3), pos=(
        tower.center[0] - Map.mapvar.squsize * 1.5, tower.center[1] - Map.mapvar.squsize * 1.5),
                                    duration=tower.reload - .1) + Animation(
            size=(Map.mapvar.squsize * 1.5, Map.mapvar.squsize * 1.5),
            pos=(tower.center[0] - Map.mapvar.squsize * .74, tower.center[1] - Map.mapvar.squsize * .74), duration=.1)
        tower.animation.repeat = True
        tower.animation.start(tower.attackImage)

    def disable(self):
        self.active = False
        if self.towerType == 'Ice':
            self.targetTimer = self.tower.reload
            self.genRoadList()
        if self.towerType == 'Gravity':
            self.targetTimer = 0
            for tower in self.towerSet:
                tower.animation.cancel_all(tower.attackImage)
                tower.closeanimation.start(tower.attackImage)
        if self.towerType == 'Wind':
            self.targetTimer = 0
            for tower in self.towerSet:
                tower.turret.source = os.path.join('towerimgs', self.towerType, "turret.png")

    def getAdjacentRoads(self):
        self.adjacentRoads = set()
        for tower in self.towerSet:
            for road in Localdefs.roadlist:
                if road.pos in tower.adjacentRoadPos:
                    self.adjacentRoads.add(road)
                    self.createIceRoad(road)
        self.adjacentRoadFlag = True

    def createIceRoad(self, road):
        road.iceNeighbor = True
        road.imagestr = road.getRoadColor()
        road.image.source = road.imagestr
        with road.image.canvas.before:
            road.image.rgba = Color(1, 1, 1, 0)
            road.image.rect = Rectangle(size=road.size, pos=road.pos)
        road.image.animation = Animation(rgba=[0, 1, 1, .5], duration=.5)
        road.image.closeanimation = Animation(rgba=[1, 1, 1, 0], duration=.1)

    def genRoadList(self):
        if not self.active:
            for road in self.adjacentRoads:
                if road in Localdefs.activeiceroadlist:
                    Localdefs.activeiceroadlist.remove(road)
                    if road.active:
                        if road.image.animation.have_properties_to_animate(road.image.rgba):
                            road.image.animation.cancel(road.image.rgba)
                        road.image.closeanimation.start(road.image.rgba)
                        road.active = False
        if self.active:
            for road in self.adjacentRoads:
                if road not in Localdefs.activeiceroadlist:
                    Localdefs.activeiceroadlist.append(road)
                    self.createIceRoad(road)
        self.toggleRoads()

    def toggleRoads(self):
        self.adjacentRoadFlag = False
        for road in Localdefs.roadlist:
            if road in Localdefs.activeiceroadlist:
                if not road.active:
                    road.active = True
                    if road.image.closeanimation.have_properties_to_animate(road.image.rgba):
                        road.image.closeanimation.cancel_all(road.image.rgba)
                    road.image.animation.start(road.image.rgba)
            else:
                if road.active:
                    if road.image.animation.have_properties_to_animate(road.image.rgba):
                        road.image.animation.cancel(road.image.rgba)
                    road.image.closeanimation.start(road.image.rgba)
                    road.active = False

    def takeTurn(self):
        self.targetTimer -= Player.player.frametime
        if self.targetTimer <= 0:
            self.target()
        if self.adjacentRoadFlag == True and self.towerType == 'Ice':
            self.genRoadList()
