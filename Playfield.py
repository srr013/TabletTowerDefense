import Map
import GUI
import Utilities
import Player
import main

from kivy.uix.scatterlayout import ScatterLayout
from kivy.graphics import *

class playField(ScatterLayout):
    def __init__(self,**kwargs):
        super(playField,self).__init__(**kwargs)

        ##scatter properties to allow partial scaling and no rotation
        self.scale = 1
        self.scale_max = 1.5
        self.scale_min = 1
        self.do_rotation=False
        self.do_translation = False
        self.size = Map.mapvar.scrwid,Map.mapvar.scrhei
        self.size_hint = (1,1)
        self.pos = Map.mapvar.mapoffset[0]*30,Map.mapvar.mapoffset[1]*30
        self.do_collide_after_children = True
        self.popUpOpen = None

    def bindings(self, *args):
        self.size = main.Window.size
        for child in self.children:
            child.size = self.size

    def on_touch_down(self, touch):
        self.squarepos = Utilities.getPos(touch.pos)

        #print "touch down", Map.mapvar.scrwid, Map.mapvar.scrhei, Map.mapvar.squsize, squarepos, touch
        #don't allow touches outside of play boundary if a menu isn't open
        if self.popUpOpen:
            if not self.popUpOpen.collide_point(*self.squarepos):
                self.removePopUp()
                return
            else:
                pass
        if not self.popUpOpen:
            if touch.pos[0] >= Map.mapvar.scrwid-Map.mapvar.squsize*2:
                self.removePopUp()
                return super(playField, self).on_touch_down(touch)
            if touch.pos[1] >= Map.mapvar.scrhei-Map.mapvar.squsize*2:
                self.removePopUp()
                return super(playField, self).on_touch_down(touch)
            if touch.pos[0] < Map.mapvar.squsize*2:
                self.removePopUp()
                return super(playField, self).on_touch_down(touch)
            if touch.pos[1] < Map.mapvar.squsize*2:
                self.removePopUp()
                return super(playField, self).on_touch_down(touch)
        #do nothing in playfield if paused or menu
        if Player.player.state == 'Paused' or Player.player.state == 'Menu':
            return
        #tower selection
        if Player.player.tbbox and Player.player.tbbox.collide_point(*self.squarepos):
            return super(playField, self).on_touch_down(touch)

        for tower in Map.mapvar.towercontainer.walk(restrict=True):
           if tower.collide_point(*self.squarepos):
               if Player.player.tbbox != None:
                   self.removePopUp()
               Player.player.towerSelected = tower
               GUI.gui.towerMenu(tower.pos)
               return True
        for tower in Map.mapvar.towercontainer.walk(restrict=True):
            if tower.collide_point(self.squarepos[0]+Map.mapvar.squsize, self.squarepos[1]):
                self.squarepos[0]-=Map.mapvar.squsize
            if tower.collide_point(self.squarepos[0], self.squarepos[1]+Map.mapvar.squsize):
                self.squarepos[1]-=Map.mapvar.squsize
            if tower.collide_point(self.squarepos[0]+30, self.squarepos[1]+Map.mapvar.squsize):
                self.squarepos[1]-=Map.mapvar.squsize
                self.squarepos[0]-=Map.mapvar.squsize
        # move the tower inside play boundaries if selection is over an edge
        if self.squarepos[0] + 2*Map.mapvar.squsize > Map.mapvar.scrwid - Map.mapvar.squsize * 2:
            self.squarepos[0] -= Map.mapvar.squsize
        elif self.squarepos[0] < Map.mapvar.squsize * 2:
            self.squarepos[0] += Map.mapvar.squsize
        if self.squarepos[1] + 2*Map.mapvar.squsize > Map.mapvar.scrhei - Map.mapvar.squsize * 2:
            self.squarepos[1] -= Map.mapvar.squsize
        elif self.squarepos[1] < Map.mapvar.squsize * 2:
            self.squarepos[1] += Map.mapvar.squsize
        #create the tower creation menu and display
        if not self.popUpOpen:
            with Map.mapvar.backgroundimg.canvas.after:
                # shaded square where tower will be located
                Color(1, .7, .08, .3)
                Map.mapvar.rect = Rectangle(size=(Map.mapvar.squsize * 2, Map.mapvar.squsize * 2), pos=self.squarepos)
            GUI.gui.builderMenu(self.squarepos)
            self.towerpos=self.squarepos
            return True
        #remove a displayed menu if touch is outside the menu
        # elif self.popUpOpen and not Player.player.tbbox.collide_point(*squarepos):
        #     self.removePopUp()
        #returning this super argument allows the touch to propogate to children.
        return super(playField, self).on_touch_down(touch)

    def removePopUp(self):
        self.towerpos = None
        Map.mapvar.backgroundimg.remove_widget(Player.player.tbbox)
        if Map.mapvar.enemypanel.parent:
            print "here", Map.mapvar.enemypanel.parent
            Map.mapvar.backgroundimg.remove_widget(Map.mapvar.enemypanel)
        if Map.mapvar.rect:
            Map.mapvar.backgroundimg.canvas.after.remove(Map.mapvar.rect)
            Map.mapvar.rect = None
        if Map.mapvar.triangle:
            Map.mapvar.backgroundimg.canvas.remove(Map.mapvar.triangle)
            Map.mapvar.triangle = None
        if Map.mapvar.towerRange:
            Map.mapvar.backgroundimg.canvas.remove(Map.mapvar.towerRange)
            Map.mapvar.towerRange = None
        Player.player.tbbox = None
        Player.player.layout = None
        self.popUpOpen = None

    def on_pressed(self, instance, pos):
        print('pressed at {pos}'.format(pos=pos))



