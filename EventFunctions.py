import localdefs
import MainFunctions
import localclasses
import sys
import threading
import pygame


##check to see if mouse position is over an object in tower and icon list. returns object selected and True if something was clicked
def leftCheckSelect(event,selected):
    for object in (localdefs.towerlist+localdefs.iconlist):
        if object.rect.collidepoint(event.dict['pos']):
            return object,True
    return selected,False

def leftSelectedTower(event,selected):
    for text,rect,info,infopos,cb in selected.buttonlist:
        if rect.collidepoint(event.dict['pos']):
            cb(selected)
            return True
    return False

##if a tower isn't already there, and the selected spot isn't on the path, return true.
##called by leftSelectedIcon below

#works on first placement but doesn't work after first tower is placed

def placeTower(event,selected):
    #currently assume that all towers are 60x60. Need to add something to the Icon class to accomodate other sizes if that changes
    roundpoint = (MainFunctions.roundPoint(event.dict['pos']))
    newTowerRect = pygame.Rect(roundpoint, (60,60))
    if localdefs.mapvar.openPath \
            and not any([wall.colliderect(newTowerRect) for wall in localdefs.wallrectlist]) \
            and not any([tower.rect.colliderect(newTowerRect) for tower in localdefs.towerlist]):
        #place the tower if it's an open map and no wall is at that point
        eval("localclasses."+selected.type+selected.base)(roundpoint)
        localdefs.mapvar.updatePath = True
        localdefs.player.towerSelected = None
        return None,True
    elif not localdefs.mapvar.openPath and not any\
        ([p.inflate(25,25).collidepoint(event.dict['pos']) for pathrectlist in localdefs.mapvar.pathrectlists for p in pathrectlist])\
        and not any ([wall.collidepoint(event.dict['pos']) for wall in localdefs.wallrectlist])\
        and not any([ttower.rect.collidepoint(event.dict['pos']) for ttower in localdefs.towerlist]):
        #place the tower if it's a closed path map, and no path

        eval("localclasses." + selected.type + selected.base)(MainFunctions.roundPoint(event.dict['pos']))
        localdefs.player.towerSelected = None
        return None,True
    else:
        MainFunctions.addAlert("Invalid Location {0}".format(roundpoint), 48, "center", (240, 0, 0))
        return selected,False

##Checks to see if player has enough money to purchase the tower
##called by leftAlreadySelected below. Calls PlaceTower
def leftSelectedIcon(event,selected):
    if event.dict['pos'][1]< localdefs.scrhei+localdefs.mapoffset[1]*localdefs.squsize and event.dict['pos'][1] > localdefs.mapoffset[1]*localdefs.squsize:
        if event.dict['pos'][0]< localdefs.scrwid+localdefs.mapoffset[0]*localdefs.squsize and event.dict['pos'][1] > localdefs.mapoffset[0]*localdefs.squsize:
            if localdefs.player.money>=eval("localclasses."+selected.type+"Tower").basecost*(1-localdefs.player.modDict[selected.type.lower()+"CostMod"])*(1-localdefs.player.modDict["towerCostMod"]):
                return placeTower(event, selected)
            else:
                localdefs.player.towerSelected = None
                selected = None
                MainFunctions.addAlert("Not Enough Money", 48, "center", (240, 0, 0))
        else:
            localdefs.player.towerSelected = None
            selected = None
            MainFunctions.addAlert("Invalid Location", 48, "center", (240, 0, 0))
    else:
        localdefs.player.towerSelected = None
        selected = None
        MainFunctions.addAlert("Invalid Location", 48, "center", (240, 0, 0))
    return selected,False

##Checks to see if something was selected with a previous action. If it's been selected is it an icon from tower menu or a tower already on the screen?
##Called by mouseButtonUp if something hasn't been selected yet, which is checked via leftCheckSelect
def leftAlreadySelected(event,selected):
    if selected.__class__ == localclasses.Icon:
        return leftSelectedIcon(event, selected)
    elif localclasses.Tower in selected.__class__.__bases__:
        if not leftSelectedTower(event, selected):
            return None,True
        else:
            return selected,False

#called in MainFunctions when user releases mouse button. Calls above functions to determine appropriate action
def mouseButtonUp(event,selected):
    if event.dict['button']==1:
        selected,lCSb = leftCheckSelect(event, selected)
        if not lCSb and selected:
            return leftAlreadySelected(event, selected)
        else: return selected,lCSb
    else:
        return None,(False if not selected else True)

#called fromMainFunctions.WorkEvents when user presses "n"
def nextWave(Sender,curtime):
    wavestart = curtime
    localdefs.player.wavenum+=1
    localdefs.mapvar.wavesSinceLoss+=1
    ##creates a Sender() and adds it to senderlist
    if ('wave'+str(localdefs.player.wavenum)+'a') in localdefs.mapvar.mapdict:
        Sender(localdefs.player.wavenum,'a')
    if ('wave'+str(localdefs.player.wavenum)+'b') in localdefs.mapvar.mapdict:
        Sender(localdefs.player.wavenum,'b')
    if ('wave'+str(localdefs.player.wavenum)+'c') in localdefs.mapvar.mapdict:
        Sender(localdefs.player.wavenum,'c')
    if ('wave'+str(localdefs.player.wavenum)+'d') in localdefs.mapvar.mapdict:
        Sender(localdefs.player.wavenum,'d')
    ##if no more waves in the dictionary and no more enemies on screen then "win" upon next call to this function
    ##issue: no functionality built in for losses yet
    if all([('wave'+str(localdefs.player.wavenum)+letter) not in localdefs.mapvar.mapdict for letter in ['a','b','c','d']]):
        if len(localdefs.enemylist) == 0:
            MainFunctions.addAlert("You Win!", 48, "center", (255,215, 0))
            localdefs.player.completedMaps.add(localdefs.mapvar.current)
            localdefs.player.save()
            sys.exit()
        else:
            localdefs.player.wavenum-=1
            wavestart = 0
    return wavestart

