def Simple(player):
    player.modDict['towerAbilities'].add("Sell")
    player.modDict['towerAbilities'].add("AddFighter")
    player.modDict['towerAbilities'].add("RemoveFighter")

def Level1(player):
    player.modDict['towerAbilities'].add("ExtendRange1")

def Level2(player):
    player.modDict['towerCostMod'] += 0.05

def Level3(player):
    player.modDict['towerAbilities'].add("ExtraDamage1")

def Pathfinding(player):
    pass

    
