import operator
import os
from functools import partial
from kivy.animation import Animation
from kivy.graphics import *

import Localdefs
import Map
import Player
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
        self.animating = False
        self.needsUpdate = True
        self.leader = None

    def updateTowerGroup(self):
        self.updateList()
        self.updateModifiers()
        self.needsUpdate = False

    def updateList(self):
        for tower in Localdefs.towerlist:
            if tower in self.towerSet and tower.towerGroup != self:
                self.towerSet.remove(tower)
            if tower not in self.towerSet and tower.towerGroup == self:
                if self.active and self.towerType == 'Gravity':
                    self.active = False
                if self.active and self.towerType == 'Wind':
                    for t in self.towerSet:
                        t.turret.source = os.path.join('towerimgs', self.towerType, "turret.gif")
                self.towerSet.add(tower)
        if self.towerType == 'Ice':
            self.getAdjacentRoads()

    def removeTowerGroup(self):
        Localdefs.towerGroupDict[self.towerType].remove(self)

    def updateModifiers(self):
        if not self.leader:
            self.dmgModifier = 1 + (len(self.towerSet) - 1) * .05
            if self.towerType != 'Gravity' or self.towerType != 'Ice':
                self.rangeModifier = 1 + (len(self.towerSet) - 1) * .05
            self.pushModifier = 1 + (len(self.towerSet) - 1) * .05
            self.slowTimeModifier = 1 + (len(self.towerSet) - 1) * .05
            self.slowPercentModifier = 1 + (len(self.towerSet) - 1) * .05
            self.stunTimeModifier = 1 + (len(self.towerSet) - 1) * .05
        else:
            self.dmgModifier = 1 + (len(self.towerSet) - 1) * .05 + (self.leader.damageBonus/100)
            if self.towerType != 'Gravity' or self.towerType != 'Ice':
                self.rangeModifier = 1 + (len(self.towerSet) - 1) * .05 + (self.leader.rangeBonus/100)
            self.pushModifier = 1 + (len(self.towerSet) - 1) * .05 + (self.leader.pushBonus/100)
            self.slowTimeModifier = 1 + (len(self.towerSet) - 1) * .05 + (self.leader.slowtimeBonus/100)
            self.slowPercentModifier = 1 + (len(self.towerSet) - 1) * .05 + (self.leader.slowpercentBonus/100)
            self.stunTimeModifier = 1 + (len(self.towerSet) - 1) * .05 + (self.leader.stuntimeBonus/100)
            self.reloadModifier = 1 + (self.leader.reloadBonus/100)

        for tower in self.towerSet:
            tower.updateModifiers()

    def takeTurn(self):
        if self.active:
            in_range_air = 0
            in_range_ground = 0
            for tower in self.towerSet:
                list = Utilities.get_all_in_range(tower,Map.mapvar.enemycontainer.children)
                if list:
                    for enemy in list:
                        if enemy.isair:
                            in_range_air += 1
                        else:
                            in_range_ground +=1
            if in_range_air == 0 and self.towerType == 'Wind':
                self.disable()
                return
            elif in_range_ground == 0 and self.towerType != 'Wind':
                self.disable()
                return
            if self.towerType != 'Gravity':
                self.targetTimer -= Player.player.frametime
                if self.targetTimer <= 0:
                    self.target()
                if self.adjacentRoadFlag == True and self.towerType == 'Ice':
                    self.genRoadList()
            else:
                self.targetTimer -= Player.player.frametime
                if self.targetTimer <= 0 and not self.animating:
                    for tower in self.towerSet:
                        self.animateGravity(tower)
        else:
            for tower in self.towerSet:
                if self.towerType == 'Wind' and Utilities.get_all_in_range(tower,Map.mapvar.enemycontainer.children, flyingOnly=True):
                    self.enable()
                    return
                elif self.towerType !='Wind' and Utilities.get_all_in_range(tower,Map.mapvar.enemycontainer.children):
                    self.enable()
                    return


    def target(self):
        for tower in self.towerSet:
            if tower.totalUpgradeTime == 0:
                tower.target()


    def enable(self):
        self.active = True
        if self.towerType == 'Ice':
            self.genRoadList()
        if self.towerType == 'Gravity':
            self.targetTimer = 0
        if self.towerType == 'Wind':
            self.targetTimer = 0
            for tower in self.towerSet:
                tower.turret.source = os.path.join('towerimgs', self.towerType, "turret.gif")

    def animateGravity(self, *args):
        tower = args[0]
        if tower.percentComplete == 0:
            tower.towerGroup.animating = True
            tower.animating = True
            if not tower.animation:
                tower.animation = Animation(size=(Map.mapvar.squsize * 3, Map.mapvar.squsize * 3), pos=(
                                tower.center[0] - Map.mapvar.squsize * 1.5, tower.center[1] - Map.mapvar.squsize * 1.5),
                                duration=tower.reload - .1) \
                                + Animation(size=(Map.mapvar.squsize * 1.5, Map.mapvar.squsize * 1.5),
                                pos=(tower.center[0] - Map.mapvar.squsize * .74, tower.center[1] - Map.mapvar.squsize * .74), duration=.1)
                tower.animation.bind(on_complete = partial(self.updateGravAnim, tower))
            tower.animation.start(tower.turret)

    def updateGravAnim(self, *args):
        tower = args[0]
        tower.animating = False
        tower.towerGroup.animating = False
        tower.target()

    def disable(self):
        self.active = False
        if self.towerType == 'Ice':
            self.targetTimer = self.tower.reload
            self.genRoadList()
        if self.towerType == 'Gravity':
            self.targetTimer = self.tower.reload
            for tower in self.towerSet:
                if tower.animation:
                    tower.animation.cancel_all(tower.turret)
                tower.closeanimation.start(tower.turret)
                self.animating = False
        if self.towerType == 'Wind':
            self.targetTimer = 0
            for tower in self.towerSet:
                tower.turret.source = os.path.join('towerimgs', self.towerType, "turret.png")

    def getAdjacentRoads(self):
        self.adjacentRoads = set()
        for tower in self.towerSet:
            if tower.percentComplete == 0:
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
