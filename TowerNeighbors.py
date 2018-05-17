'''Responsible for tower images and setting/getting the appropriate tower group'''

import os
from kivy.graphics import *
import Map
import TowerGroup
import Localdefs


def getNeighbors(tower):
    '''Returns a list of towers adjacent to the provided tower and sets the tower up to have its image, rotation updated'''
    neighbors = {}
    neighborlist = []

    for t in Localdefs.towerlist:
        if t.type == tower.type:
            if t.rect_x == tower.rect_x - 2 * Map.mapvar.squsize and t.rect_y == tower.rect_y:
                neighbors['l0'] = t
                neighborlist.append('l0')
            elif t.rect_x == tower.rect_x + 2 * Map.mapvar.squsize and t.rect_y == tower.rect_y:
                neighbors['r0'] = t
                neighborlist.append('r0')
            elif t.rect_y == tower.rect_y + 2 * Map.mapvar.squsize and t.rect_x == tower.rect_x:
                neighbors['u0'] = t
                neighborlist.append('u0')
            elif t.rect_y == tower.rect_y - 2 * Map.mapvar.squsize and t.rect_x == tower.rect_x:
                neighbors['d0'] = t
                neighborlist.append('d0')
            elif t.rect_x == tower.rect_x - 2 * Map.mapvar.squsize:
                if t.rect_y == (tower.rect_y + Map.mapvar.squsize):
                    neighbors['l1'] = t
                    neighborlist.append('l1')
                elif t.rect_y == (tower.rect_y - Map.mapvar.squsize):
                    neighbors['l2'] = t
                    neighborlist.append('l2')
            elif t.rect_x == tower.rect_x + 2 * Map.mapvar.squsize:
                if t.rect_y == (tower.rect_y + Map.mapvar.squsize):
                    neighbors['r1'] = t
                    neighborlist.append('r1')
                elif t.rect_y == (tower.rect_y - Map.mapvar.squsize):
                    neighbors['r2'] = t
                    neighborlist.append('r2')
            elif t.rect_y == tower.rect_y + 2 * Map.mapvar.squsize:
                if t.rect_x == (tower.rect_x - Map.mapvar.squsize):
                    neighbors['u1'] = t
                    neighborlist.append('u1')
                elif t.rect_x == (tower.rect_x + Map.mapvar.squsize):
                    neighbors['u2'] = t
                    neighborlist.append('u2')
            elif t.rect_y == tower.rect_y - 2 * Map.mapvar.squsize:
                if t.rect_x == (tower.rect_x - Map.mapvar.squsize):
                    neighbors['d1'] = t
                    neighborlist.append('d1')
                elif t.rect_x == (tower.rect_x + Map.mapvar.squsize):
                    neighbors['d2'] = t
                    neighborlist.append('d2')

    totalNeighbors = 0
    sideList = set()
    for neighbor in neighborlist:
        totalNeighbors += 1
        sideList.add(neighbor[0])
    if totalNeighbors != tower.lastNeighborCount:
        tower.neighborFlag = 'update'
        tower.neighborList = neighborlist
        tower.lastNeighborCount = totalNeighbors
        tower.neighborSideCount = len(sideList)  # 1-4 to be used in getImage
        tower.neighborSideList = list(sideList)

    return neighbors

# def getGroup(tower):
#     '''Sets the appropriate tower group for the tower given its neighbor's groups'''
#     if not tower.neighbors: #create a new towerGroup
#         tower.towerGroup = TowerGroup.TowerGroup(tower)
#         getImage(tower)
#
#     else: #use the existing one from a neighbor and set all
#         letter = tower.neighborList[0]
#         tower.towerGroup = tower.neighbors[letter].towerGroup
#         #fetchGroup(tower, tower.towerGroup.towerSet)
#         getImage(tower)
#         if len(tower.neighborList) >= 1:
#             x = 0
#             while x < len(tower.neighborList):
#                 letter = tower.neighborList[x]
#                 getData(tower,letter)
#                 x += 1


def updateNeighbors(tower):
    '''Creates a new group or groups for the remaining towers after a tower is sold'''
    x = 0
    tg = tower.towerGroup
    while x < len(tower.neighborList): #update the neighbors of the removed tower
        neighbor = tower.neighbors[tower.neighborList[x]]
        neighbor.neighbors = getNeighbors(neighbor)
        getImage(neighbor)
        if neighbor.towerGroup == tg:
            neighbor.towerGroup = TowerGroup.TowerGroup(neighbor)
            neighborset = set()
            setGroup(neighbor, tower, neighborset)
        neighbor.towerGroup.updateTowerGroup()
        x+=1
    tg.updateTowerGroup()

def setGroup(tower, removed, set):
    '''Uses recursion to find all towers in a group and set their towerGroup. Only used when towers are sold'''
    neighbors = tower.neighbors.values()
    for value in neighbors:
        if value not in set:
            if value != removed:
                value.towerGroup = tower.towerGroup
                set.add(value)
                setGroup(value,removed, set)


def initNeighbors(tower, tset, tgset):
    '''Iterates through all connected towers and returns a list of all towers and their towergroups.
    Used primarily in EventFunctions when multiple towers are placed.'''
    tower.neighbors = getNeighbors(tower)
    for n in tower.neighbors.values():
        if n not in tset:
            tset.add(n)
            if n.towerGroup != None:
                tgset.add(n.towerGroup)
            initNeighbors(n, tset, tgset)


# def getData(t, string):
#     '''Sets the tower group and updates the tower's appearance. Only used when tower is purchased (not sold)'''
#     tower = t.neighbors[string]
#     tower.neighbors = getNeighbors(tower)
#     getImage(tower)
#     for element in tower.towerGroup.towerSet:
#         element.towerGroup = t.towerGroup


def getImage(tower):
    '''Gets the appropriate image for the tower given its neighbors'''
    if not tower.neighbors:
        tower.imageNum = 0
        updateImage(tower)
        return
    if tower.neighborSideCount == 4:
        tower.imageNum = 4

    elif tower.neighborSideCount == 3:
        tower.imageNum = 3

    elif tower.neighborSideCount == 2:
        list = sorted(tower.neighborSideList)
        if list[0][0] == 'd' and list[1][0] == 'u':
            tower.imageNum = '2_1'
        elif list[0][0] == 'l' and list[1][0] == 'r':
            tower.imageNum = '2_1'
        else:
            tower.imageNum = '2_2'

    elif tower.neighborSideCount == 1:
        tower.imageNum = 1

    updateImage(tower)

def getRotation(tower):
    '''Determines the appropriate rotation of the tower image so it aligns with its neighbors'''
    rotation = 0
    desiredRotation = 0
    list = sorted(tower.neighborSideList)
    count = tower.neighborSideCount
    if tower.neighborFlag == 'update':
        if count == 1:
            if list[0][0] == 'd':
                desiredRotation = 270
            elif list[0][0] == 'l':
                desiredRotation = 180
            elif list[0][0] == 'r':
                desiredRotation = 0
            elif list[0][0] == 'u':
                desiredRotation = 90
        if count == 2:
            if list[0][0] == 'd' and list[1][0] == 'u':
                desiredRotation = 90
            elif list[0][0] == 'd' and list[1][0] == 'l':
                desiredRotation = 180
            elif list[0][0] == 'd' and list[1][0] == 'r':
                desiredRotation = 270
            elif list[0][0] == 'l' and list[1][0] == 'r':
                desiredRotation = 0
            elif list[0][0] == 'l' and list[1][0] == 'u':
                desiredRotation = 90
            elif list[0][0] == 'r' and list[1][0] == 'u':
                desiredRotation = 0
        if count == 3:
            if list[0][0] == 'd' and list[1][0] == 'l' and list[2][0] == 'r':
                desiredRotation = 270
            elif list[0][0] == 'd' and list[1][0] == 'l' and list[2][0] == 'u':
                desiredRotation = 180
            elif list[0][0] == 'd' and list[1][0] == 'r' and list[2][0] == 'u':
                desiredRotation = 0
            elif list[0][0] == 'l' and list[1][0] == 'r' and list[2][0] == 'u':
                desiredRotation = 90
        if count == 4:
            desiredRotation = 0
        rotation = abs(tower.currentRotation - desiredRotation)
        if tower.currentRotation > desiredRotation:
            rotation = -rotation
        tower.currentRotation = desiredRotation

        return rotation

    else:
        return 0

def updateImage(tower):
    '''Rotates the tower and applies the appropriate image'''
    tower.rotation = 0
    if tower.neighbors:
        tower.rotation = getRotation(tower)
    if tower.neighborFlag == 'update':
        tower.imagestr = os.path.join('towerimgs', tower.type, str(tower.imageNum) + '.png')
        tower.source = tower.imagestr
        tower.neighborFlag = ''
    if tower.rotation != 0:
        with tower.canvas.before:
            PushMatrix()
            tower.rot = Rotate(axis=(0, 0, 1), origin=tower.center, angle=tower.rotation)
        with tower.canvas.after:
            PopMatrix()  # tower positioning and rotation
        with tower.levelLabel.canvas.before:
            PushMatrix()
            tower.levelLabel.rot = Rotate(axis=(0,0,1), origin = tower.center, angle= -tower.rotation)
        with tower.canvas.after:
            PopMatrix()
        
