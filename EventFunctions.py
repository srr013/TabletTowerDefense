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
import GUI


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

        if MainFunctions.updatePath()== False:
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


def nextWave(*args):
    '''Send the next enemy wave'''
    Player.player.score += int(Player.player.wavetimeInt * Player.player.wavenum * .25)
    GUI.gui.myDispatcher.Score = str(Player.player.score)
    Player.player.wavenum+=1
    GUI.gui.myDispatcher.WaveNum = Player.player.wavenum
    GUI.gui.myDispatcher.Wave = str(Player.player.wavenum)
    Player.player.wavetime = Map.waveseconds
    Player.player.wavetimeInt = int(Map.waveseconds)
    GUI.gui.myDispatcher.Timer = str(Player.player.wavetime)
    Player.player.next_wave = False
    SenderClass.Sender(specialSend = False)


