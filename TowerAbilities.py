from localdefs import player,towerlist, mapvar

class TowerAbility:
    pass

class Sell(TowerAbility):
    name = "Sell"
    shortname = "Sell"
    @classmethod
    def cost(cls,tower):
        return -1*(tower.totalspent)
    @classmethod
    def doesFit(cls,tower):
        return True
    @classmethod
    def apply(cls,**kwargs):
        print "selling"
        tower = kwargs['tower']
        player.money+=(tower.totalspent)
        towerlist.remove(tower)
        player.towerSelected = None
        mapvar.updatePath = True
        return True

class AddFighter(TowerAbility):
    name = "Add 1 Fighter"
    shortname = "AddFighter"
    @classmethod
    def cost(cls,tower):
        return 0
    @classmethod
    def doesFit(cls,tower):
        if tower.type == "Fighter" and tower.num_fighters < 5:
            return True
        else:
            return False
    @classmethod
    def apply(cls,tower):
        player.num_fighters -= 1
        tower.num_fighters +=1
        return True

class RemoveFighter(TowerAbility):
    name = "Remove 1 Fighter"
    shortname = "RemoveFighter"
    @classmethod
    def cost(cls,tower):
        return 0
    @classmethod
    def doesFit(cls,tower):
        if tower.type == "Fighter" and tower.num_fighters > 0:
            return True
        else:
            return False
    @classmethod
    def apply(cls,tower):
        player.num_fighters += 1
        tower.num_fighters -=1
        return True

class Upgrade(TowerAbility):
    name = "15% +Damage"
    shortname = "ExtraDamage1"
    @classmethod
    def cost(cls,tower):
        return 10
    @classmethod
    def doesFit(cls,tower):
        return (cls not in tower.upgrades)
    @classmethod
    def apply(cls,**kwargs):
        print "applying Upgrade"
        tower = kwargs['tower']
        if player.money>=cls.cost(tower):
            player.money-=cls.cost(tower)
            tower.damageMod += 0.15*tower.basedamage
            tower.reload()
            tower.upgrades.append(cls)
            return True
        return False

class ExtendRange1(TowerAbility):
    name = "150% Range"
    shortname = "ExtendRange1"
    @classmethod
    def cost(cls,tower):
        return 15
    @classmethod
    def doesFit(cls,tower):
        return (cls not in tower.upgrades)
    @classmethod
    def apply(cls,tower):
        if player.money>=cls.cost(tower):
            player.money-=cls.cost(tower)
            tower.rangeMod += 0.5*tower.baserange
            tower.reload()
            tower.upgrades.append(cls)
            return True
        else:
            print "Not enough money!"
            return False

TowerAbilityList = list([Sell,Upgrade])
