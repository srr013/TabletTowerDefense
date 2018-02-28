import Map
import GUI
import Utilities
import Player

from kivy.uix.scatterlayout import ScatterLayout

class playField(ScatterLayout):
    def __init__(self,**kwargs):
        super(playField,self).__init__(**kwargs)

        ##scatter properties to allow partial scaling and no rotation
        self.scale = 1
        self.scale_max = 1.5
        self.scale_min = 1
        self.do_rotation=False
        self.do_translation = False
        self.size = Map.scrwid,Map.scrhei
        self.pos = Map.mapoffset[0]*30,Map.mapoffset[1]*30
        self.do_collide_after_children = True
        self.popUpOpen = None


    def on_touch_down(self, touch):
        squarepos = Utilities.getPos(touch.pos)
        #don't allow touches outside of play boundary if a menu isn't open
        if self.popUpOpen:
            if not self.popUpOpen.collide_point(*squarepos):
                self.removePopUp()
                return
            else:
                pass
        if not self.popUpOpen:
            if squarepos[0] >= Map.scrwid-Map.squsize*2:
                self.removePopUp()
                return super(playField, self).on_touch_down(touch)
            if squarepos[1] >= Map.scrhei-Map.squsize*2:
                self.removePopUp()
                return super(playField, self).on_touch_down(touch)
            if squarepos[0] < Map.squsize*2:
                self.removePopUp()
                return
            if squarepos[1] < Map.squsize*2:
                self.removePopUp()
                return
        #do nothing in playfield if paused or menu
        if Player.player.state == 'Paused' or Player.player.state == 'Menu':
            return
        #tower selection
        if Player.player.tbbox and Player.player.tbbox.collide_point(*squarepos):
            return super(playField, self).on_touch_down(touch)

        for tower in Map.mapvar.towercontainer.walk(restrict=True):
           if tower.collide_point(*squarepos):
               if Player.player.tbbox != None:
                   self.removePopUp()
               Player.player.towerSelected = tower
               GUI.gui.towerMenu(tower.pos)
               return True
        for tower in Map.mapvar.towercontainer.walk(restrict=True):
            if tower.collide_point(squarepos[0]+30, squarepos[1]):
                squarepos[0]-=30
            if tower.collide_point(squarepos[0], squarepos[1]+30):
                squarepos[1]-=30
            if tower.collide_point(squarepos[0]+30, squarepos[1]+30):
                squarepos[1]-=30
                squarepos[0]-=30
        # move the tower inside play boundaries if selection is over an edge
        if squarepos[0] + 60 > Map.scrwid - Map.squsize * 2:
            squarepos[0] -= 30
        elif squarepos[0] < Map.squsize * 2:
            squarepos[0] += 30
        if squarepos[1] + 60 > Map.scrhei - Map.squsize * 2:
            squarepos[1] -= 30
        elif squarepos[1] < Map.squsize * 2:
            squarepos[1] += 30
        #create the tower creation menu and display
        if not self.popUpOpen:
            GUI.gui.builderMenu(squarepos)
            return True
        #remove a displayed menu if touch is outside the menu
        # elif self.popUpOpen and not Player.player.tbbox.collide_point(*squarepos):
        #     self.removePopUp()
        #returning this super argument allows the touch to propogate to children.
        return super(playField, self).on_touch_down(touch)

    def removePopUp(self):
        Map.mapvar.backgroundimg.remove_widget(Player.player.tbbox)
        if Map.mapvar.enemypanel.parent:
            Map.mapvar.backgroundimg.remove_widget(Map.mapvar.enemypanel)
        Player.player.tbbox = None
        Player.player.layout = None
        self.popUpOpen = None

    def on_pressed(self, instance, pos):
        print('pressed at {pos}'.format(pos=pos))
