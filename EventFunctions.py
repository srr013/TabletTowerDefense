import localdefs
import MainFunctions
# import localclasses
# import sys
# import threading
# import pygame
import Map
import Player
import Towers
# import Utilities
import SenderClass
import GUI_Kivy


# def leftCheckSelect(event,selected):
#     '''Check to see if mouse position is over an object in tower and icon list. Returns object selected and a boolean indicating a if something was clicked.
#     Event: Dict of user actions from keyboard/mouse
#     Selected: tower or icon selected'''
#     for object in (localdefs.towerlist+localdefs.iconlist):
#         if object.rect.collidepoint(event.dict['pos']):
#             return object,True
#     return selected,False
#
# def leftSelectedTower(event,selected):
#     '''Displays the tower menu if a tower was clicked.
#     Event: Dict of user actions from keyboard/mouse
#     Selected: tower or icon selected'''
#     for text,rect,info,infopos,cb in selected.buttonlist:
#         if rect.collidepoint(event.dict['pos']):
#             cb(selected)
#             return True
#     return False

##if a tower isn't already there, and the selected spot isn't on the path, return true.
##called by leftSelectedIcon below

def placeTower(*args):
    '''Places a tower at location of event (mouseclick)
    Event: Dict of user actions from keyboard/mouse
    Selected: tower or icon selected'''
    #currently assume that all towers are 60x60. Need to add something to the Icon class to accomodate other sizes if that changes
    instance = args[0]
    #the conversion of pos on the line below must match (opposite) of the tbbox conversion in GUI_Kivy.builderMenu
    pos = (instance.parent.pos[0]+Map.squsize*2, instance.parent.pos[1]+Map.squsize*2)
    towerselected = instance.instance
    sufficient_funds = True if instance.instance.cost < Player.player.money else False
    towerWidgetList = Map.mapvar.towercontainer.walk(restrict=True)
    newTower = eval("Towers." + towerselected.type + towerselected.base)(pos)
    toweroverlap = []
    for tower in towerWidgetList:
        toweroverlap.append(newTower.collide_widget(tower))

    walloverlap = set(Map.path.wall_list).intersection(newTower.towerwalls)
    #print (walloverlap, newTower.towerwalls)

    if Map.mapvar.openPath and sufficient_funds and not any(toweroverlap) and str(walloverlap) == 'set()':
        #place the tower if it's an open map and no wall is at that point
        #add the tower to the tower container after the if statement, otherwise it collides with itself

        if MainFunctions.updatePath(Map.mapvar.openPath)== False:
            i = 0
            while i < len(localdefs.towerlist[-1].towerwalls):
                Map.path.wall_list.pop(-1)
                i += 1
            print("Path blocked!!")
            localdefs.towerlist.pop()
            Map.mapvar.towercontainer.remove_widget(newTower)
            return towerselected, False
        else:
            Map.mapvar.towercontainer.add_widget(newTower)
            Player.player.towerSelected = None
            return None, True

    elif not Map.mapvar.openPath and not any(toweroverlap) and str(walloverlap) == 'set()':
        #place the tower if it's a closed path map, and no path
        Map.mapvar.towercontainer.add_widget(newTower)
        eval("Towers." + towerselected.type + towerselected.base)(pos)
        Player.player.towerSelected = None
        return None,True

    else:
        print ("tower not placed")
        localdefs.towerlist.pop()
        Map.mapvar.towercontainer.remove_widget(newTower)
        # MainFunctions.addAlert("Invalid Location".format(pos), 48, "center", (240, 0, 0))
        return towerselected,False

# ##Checks to see if player has enough money to purchase the tower
# ##called by leftAlreadySelected below. Calls PlaceTower
# def leftSelectedIcon(event,selected):
#     '''If an Icon was previously selected check for available money then call PlaceTower
#     Event: Dict of user actions from keyboard/mouse
#     Selected: tower or icon selected'''
#     if event.dict['pos'][1]< Map.scrhei+Map.mapoffset[1]*Map.squsize and event.dict['pos'][1] > Map.mapoffset[1]*Map.squsize:
#         if event.dict['pos'][0]< Map.scrwid+Map.mapoffset[0]*Map.squsize and event.dict['pos'][1] > Map.mapoffset[0]*Map.squsize:
#             if Player.player.money>=eval("localclasses."+selected.type+"Tower").basecost*(1-Player.player.modDict[selected.type.lower()+"CostMod"])*(1-Player.player.modDict["towerCostMod"]):
#                 return placeTower(event, selected)
#             else:
#                 Player.player.towerSelected = None
#                 selected = None
#                 MainFunctions.addAlert("Not Enough Money", 48, "center", (240, 0, 0))
#         else:
#             Player.player.towerSelected = None
#             selected = None
#             MainFunctions.addAlert("Invalid Location", 48, "center", (240, 0, 0))
#     else:
#         Player.player.towerSelected = None
#         selected = None
#         MainFunctions.addAlert("Invalid Location", 48, "center", (240, 0, 0))
#     return selected,False
#
# ##Checks to see if something was selected with a previous action. If it's been selected is it an icon from tower menu or a tower already on the screen?
# ##Called by mouseButtonUp if something hasn't been selected yet, which is checked via leftCheckSelect
# def leftAlreadySelected(event,selected):
#     '''Determine if a tower or icon is selected currently
#     Event: Dict of user actions from keyboard/mouse
#     Selected: tower or icon selected'''
#     if selected.__class__ == localclasses.Icon:
#         return leftSelectedIcon(event, selected)
#     elif localclasses.Tower in selected.__class__.__bases__:
#         if not leftSelectedTower(event, selected):
#             return None,True
#         else:
#             return selected,False
#
# #called in MainFunctions when user releases mouse button. Calls above functions to determine appropriate action
# def mouseButtonUp(event,selected):
#     '''If mousebuttonUp event is detected determine next steps and call appropriate function
#     Event: Dict of user actions from keyboard/mouse
#     Selected: tower or icon selected'''
#     print ("in MBup")
#     if event.dict['button']==1:
#         selected,lCSb = leftCheckSelect(event, selected)
#         if not lCSb and selected:
#             return leftAlreadySelected(event, selected)
#         else: return selected,lCSb
#     else:
#         return None,(False if not selected else True)


def nextWave(*args):
    '''Send the next enemy wave'''
    Player.player.wavenum+=1
    GUI_Kivy.gui.myDispatcher.WaveNum = Player.player.wavenum
    GUI_Kivy.gui.myDispatcher.Wave = str(Player.player.wavenum)
    SenderClass.Sender(specialSend = False)


