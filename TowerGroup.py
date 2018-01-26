#Tower will point to the group it is part of. This happens on tower creation
##towerGroup points to all towers it is part of via towerList
#tower inherits modifiers from the group

import localdefs

class TowerGroup():
    def __init__(self, type):
        self.towerSet = set()
        self.towerType = type
        localdefs.towerGroupDict[self.towerType].append(self)
        self.dmgModifier = 1
        self.reloadModifier = 1
        self.rangeModifier = 1

    def updateTowerGroup(self):
        self.updateList()
        self.updateModifiers()

    def updateList(self):
        for tower in localdefs.towerlist:
            if tower in self.towerSet and tower.towerGroup != self:
                self.towerSet.remove(tower)
            if tower not in self.towerSet and tower.towerGroup == self:
                self.towerSet.add(tower)

        if self.towerSet == set():
            localdefs.towerGroupDict[self.towerType].remove(self)

    def updateModifiers(self):
        self.dmgModifier = 1 + (len(self.towerSet)-1) * .05

        for tower in self.towerSet:
            tower.updateModifiers()
