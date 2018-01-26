import Map
import GUI_Kivy
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
        #self.do_translation = False
        self.size = Map.scrwid,Map.scrhei
        self.pos = Map.mapoffset[0]*30,Map.mapoffset[1]*30
        #print("playfield:", self.size, self.pos)
        self.do_collide_after_children = True
        #self.inbounds = FloatLayout(pos = (border,border), size_hint=(None,None), size = (scrwid - 4*squsize, scrhei- 4*squsize))
        #print ("self.inbounds", self.inbounds.size, self.inbounds.pos)
        #self.add_widget(self.inbounds)


    def on_touch_down(self, touch):
        squarepos = Utilities.getPos(touch.pos)
        #don't allow touches outside of play boundary if a menu isn't open
        if squarepos[0] >= Map.scrwid-Map.squsize*2 and Player.player.tbbox == None :
            self.removePopUp()
            return super(playField, self).on_touch_down(touch)
        if squarepos[1] >= Map.scrhei-Map.squsize*2 and Player.player.tbbox == None:
            self.removePopUp()
            return super(playField, self).on_touch_down(touch)
        if squarepos[0] < Map.squsize*2 and Player.player.tbbox == None:
            self.removePopUp()
            return
        if squarepos[1] < Map.squsize*2 and Player.player.tbbox == None:
            self.removePopUp()
            return

        #move the tower inside play boundaries if selection is at upper or right edge
        if squarepos[0]+60 > Map.scrwid-Map.squsize*2:
            squarepos[0] -= 30
        if squarepos[1]+60 > Map.scrhei-Map.squsize*2:
            squarepos[1] -= 30

        #do nothing in playfield if paused or menu
        if Player.player.state == 'Paused' or Player.player.state == 'Menu':
            return

        #Handle touches in playfield
        #tower selection
        if Player.player.tbbox and Player.player.tbbox.collide_point(*touch.pos):
            return super(playField, self).on_touch_down(touch)
        #touching a tower on the field
        for tower in Map.mapvar.towercontainer.walk(restrict=True):
           if tower.collide_point(*touch.pos):
               if Player.player.tbbox != None:
                   self.removePopUp()
               Player.player.towerSelected = tower
               GUI_Kivy.gui.towerMenu(tower.pos)
               return True
        #create the tower creation menu and display
        if not Player.player.tbbox:
            GUI_Kivy.gui.builderMenu(squarepos)
            return True
        #remove a displayed menu if touch is outside the menu
        elif Player.player.tbbox and not Player.player.tbbox.collide_point(*touch.pos):
            self.removePopUp()

        #returning this super argument allows the touch to propogate to children.
        return super(playField, self).on_touch_down(touch)



    def removePopUp(self):
        Map.mapvar.backgroundimg.remove_widget(Player.player.tbbox)
        Player.player.tbbox = None
        Player.player.layout = None


    def on_pressed(self, instance, pos):
        print('pressed at {pos}'.format(pos=pos))
