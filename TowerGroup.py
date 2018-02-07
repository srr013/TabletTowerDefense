import localdefs

class TowerGroup():
    def __init__(self, type):
        self.towerSet = set()
        self.towerType = type
        localdefs.towerGroupDict[self.towerType].append(self)
        self.dmgModifier = 1
        self.reloadModifier = 1
        self.rangeModifier = 1
        self.pushModifier = 1
        self.slowTimeModifier = 1
        self.slowPercentModifier = 1
        self.stunTimeModifier = 1

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
        self.reloadModifier = 1 + (len(self.towerSet)-1) * .05
        self.rangeModifier = 1 + (len(self.towerSet)-1) * .05
        self.pushModifier = 1 + (len(self.towerSet)-1) * .05
        self.slowTimeModifier = 1 + (len(self.towerSet)-1) *.05
        self.slowPercentModifier = 1 + (len(self.towerSet)-1) *.05
        self.stunTimeModifier = 1 + (len(self.towerSet)-1) *.05

        for tower in self.towerSet:
            tower.updateModifiers()
