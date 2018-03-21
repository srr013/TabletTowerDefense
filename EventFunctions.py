import Localdefs
import MainFunctions
import Map
import Player
import Towers
import SenderClass
import GUI


def placeTower(*args):
    '''Places a tower at location of event (mouseclick)
    Event: Dict of user actions from keyboard/mouse
    Selected: tower or icon selected'''
    #currently assume that all towers are 60x60. Need to add something to the Icon class to accomodate other sizes if that changes
    instance = args[0]
    #the conversion of pos on the line below must match (opposite) of the tbbox conversion in GUI_Kivy.builderMenu
    # pos = (instance.parent.pos[0]+Map.mapvar.squsize*2, instance.parent.pos[1]+Map.mapvar.squsize*2)
    towerselected = instance.instance
    sufficient_funds = True if instance.instance.cost <= Player.player.money else False
    towerWidgetList = Map.mapvar.towercontainer.walk(restrict=True)
    newTower = eval("Towers." + towerselected.type + towerselected.base)(Map.mapvar.background.towerpos)
    toweroverlap = []
    for tower in towerWidgetList:
        toweroverlap.append(newTower.collide_widget(tower))

    walloverlap = set(Map.path.wall_list).intersection(newTower.towerwalls)

    if Map.mapvar.openPath and sufficient_funds and not any(toweroverlap) and str(walloverlap) == 'set([])':
        #place the tower if it's an open map and no wall is at that point
        #add the tower to the tower container after the if statement, otherwise it collides with itself
        Map.mapvar.towercontainer.add_widget(newTower)
        if MainFunctions.updatePath()== False:
            i = 0
            while i < len(Localdefs.towerlist[-1].towerwalls):
                Map.path.wall_list.pop(-1)
                i += 1
            print("Path blocked!!")
            Localdefs.towerlist.pop()
            Map.mapvar.towercontainer.remove_widget(newTower)

        else:
            Player.player.towerSelected = None
            for enemy in Map.mapvar.enemycontainer.children:
                if enemy.anim:
                    enemy.anim.cancel_all(enemy)
                enemy.movelist = Map.mapvar.pointmovelists[enemy.movelistNum]
                enemy.getNearestNode()



    elif not Map.mapvar.openPath and not any(toweroverlap) and str(walloverlap) == 'set()':
        #place the tower if it's a closed path map, and no path
        Map.mapvar.towercontainer.add_widget(newTower)
        eval("Towers." + towerselected.type + towerselected.base)(Map.mapvar.background.squarepos)
        Player.player.towerSelected = None


    else:
        print ("tower not placed")
        Localdefs.towerlist.pop()
        Map.mapvar.towercontainer.remove_widget(newTower)
        # MainFunctions.addAlert("Invalid Location".format(pos), 48, "center", (240, 0, 0))



def nextWave(*args):
    '''Send the next enemy wave'''
    Player.player.score += int(Player.player.wavetimeInt * Player.player.wavenum * .25)
    GUI.gui.myDispatcher.Score = str(Player.player.score)
    Player.player.wavenum+=1
    GUI.gui.myDispatcher.WaveNum = str(Player.player.wavenum)
    Map.mapvar.enemypanel.CurrentWave = str(Player.player.wavenum)
    #GUI.gui.myDispatcher.Wave = str(Player.player.wavenum)
    Player.player.wavetime = Map.mapvar.waveseconds
    Player.player.wavetimeInt = int(Map.mapvar.waveseconds)
    GUI.gui.myDispatcher.Timer = str(Player.player.wavetime)
    Player.player.next_wave = False
    SenderClass.Sender(specialSend = False)


