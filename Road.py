import Utilities
import Map
import Localdefs

import os


class Road():
    def __init__(self, pos):
        self.image = Utilities.imgLoad(source=os.path.join('backgroundimgs','roadarrow.png'), pos=(pos[0], pos[1]))
        self.image.active = False
        self.image.size = (30,30)
        self.pos = self.image.pos
        self.size = self.image.size
        Map.mapvar.roadcontainer.add_widget(self.image)
        Localdefs.roadlist.append(self)
        self.iceNeighbor = False
        self.active = False
        self.imagestr = self.getRoadColor()
        self.image.source = self.imagestr

    def getRoadColor(self):
        if self.iceNeighbor:
            return os.path.join('backgroundimgs', 'blueroadarrow.png')

        if self.image.pos == [30,270] or self.image.pos == [60,270]:
           return os.path.join('backgroundimgs','redroadarrow.png')

        else:
            return os.path.join('backgroundimgs', 'roadarrow.png')

    def getIceNeighbor(self):
        for group in Localdefs.towerGroupDict['Ice']:
            if self in group.adjacentRoads:
                print self, group.adjacentRoads
                self.iceNeighbor = True
                return
        self.iceNeighbor = False