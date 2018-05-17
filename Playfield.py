from kivy.uix.scatterlayout import ScatterLayout
from kivy.app import App

import GUI
import Kvgui
import Map
import TowerDragging
import Utilities
import main
import Player
import Messenger

class PlayField(ScatterLayout):
    def __init__(self, **kwargs):
        super(PlayField, self).__init__(**kwargs)
        self.app = App.get_running_app()
        self.do_collide_after_children = True
        self.popUpOpen = None
        self.placeholder = self.dragger = None
        self.totalCost = 0

    def bindings(self, *args):
        self.size = main.Window.size
        for child in self.children:
            child.size = self.size

    def on_touch_up(self, touch):
        if self.dragger:
            totalCost = len(self.dragger.towerposlist) * 15
            if totalCost == 0:
                totalCost = 1
            Player.player.myDispatcher.totalCost = str(totalCost)
            return

    def on_touch_down(self, touch): # Needs redesign after kv setup is done
        if Player.player.state == 'Paused':
            return
        adjtouchpos =  self.to_local(*touch.pos) #adjtouch uses Scatter coordinates
        self.squarepos = Utilities.getPos(adjtouchpos) #touch and squpos use standard coordinates
        self.squarepos = self.adjustInBounds(self.squarepos)
        # don't allow touches outside of play boundary if a menu isn't open
        if self.popUpOpen:
            if not self.popUpOpen.collide_point(*adjtouchpos):
                if self.dragger:
                    if self.dragger.collide_point(*adjtouchpos):
                        touch.pos = adjtouchpos
                        self.dragger.on_touch_down(touch)
                        return
                    else:
                        self.removeAll()
                        return
                else:
                    self.removeAll()
                    return
            else:
                return super(PlayField, self).on_touch_down(touch)
        if not self.popUpOpen:
            if self.outOfBounds(touch.pos):
                self.removeAll()
                return super(PlayField, self).on_touch_down(touch)
        # tower selection buttons
        if self.towerSelected(adjtouchpos):
            return
        # create the tower creation menu and display
        if not self.openTowerBuilder():
            return
        # returning this super argument allows the touch to propogate to children.
        self.adjustForNeighbor(adjtouchpos)
        return super(PlayField, self).on_touch_down(touch)

    def towerSelected(self, touchpos):
        for tower in Map.mapvar.towercontainer.children:
            if tower.collide_point(*touchpos) and tower.id != 'Base':
                if Player.player.tbbox != None:
                    self.removeAll()
                Player.player.towerSelected = tower
                Kvgui.PopUpBox(tower.pos, 9,9)
                Player.player.tbbox.createTowerMenu()
                if tower.type == 'Wind':
                    tower.drawTriangle()
                tower.drawRangeLines()
                return True

    def openTowerBuilder(self):
        if not self.popUpOpen:
            self.placeholder = TowerDragging.TowerPlaceholder(pos=self.squarepos, initial=True)
            self.dragger = TowerDragging.TowerDragger(pos=self.squarepos)
            Kvgui.PopUpBox(self.squarepos, 4, 6)
            Player.player.tbbox.createBuilderMenu()
            self.towerpos = self.squarepos
            return True

    def adjustInBounds(self, pos):
        if pos[0] < self.app.root.playwid - self.app.root.squsize*4 and pos[0] > 0\
                and pos[1] < self.app.root.playhei - self.app.root.squsize*4 and pos[1] > 0:
            return pos
        if pos[0] + 2 * self.app.root.squsize > self.app.root.playwid - self.app.root.squsize*2:
            pos[0] = self.app.root.playwid - self.app.root.squsize * 4
        elif pos[0] < 0:
            pos[0] = 0
        if pos[1] + 2 * self.app.root.squsize > self.app.root.playhei - self.app.root.squsize*2:
            pos[1] = self.app.root.playhei - self.app.root.squsize * 4
        elif pos[1] < 0:
            pos[1] = 0
        return pos


    def adjustForNeighbor(self, touchpos):
        collision = False
        for tower in Map.mapvar.towercontainer.children:
            if self.placeholder.collide_widget(tower):
                collision = True
                if tower.x <= touchpos[0] < tower.right:
                    if touchpos[1] < tower.top:
                        self.placeholder.pos = (self.placeholder.x, self.placeholder.y - self.app.root.squsize)
                    else:
                        self.placeholder.pos = (self.placeholder.x, self.placeholder.y + self.app.root.squsize)
                elif tower.y <= touchpos[1] < tower.top:
                    if touchpos[0] < tower.right:
                        self.placeholder.pos = (self.placeholder.x - self.app.root.squsize, self.placeholder.y)
                    else:
                        self.placeholder.pos = (self.placeholder.x + self.app.root.squsize, self.placeholder.y)
                elif touchpos[0] < tower.x and touchpos[1] < tower.y:
                    self.placeholder.pos = (self.placeholder.x - self.app.root.squsize, self.placeholder.y - self.app.root.squsize)
        if collision == True:
            for tower in Map.mapvar.towercontainer.children:
                if self.placeholder.collide_widget(tower):
                    self.removeAll()
                    Messenger.messenger.createMessage("Not Enough Room")
                    return


    def outOfBounds(self, pos):
        if pos[0] >= self.app.root.playwid or \
                pos[1] >= self.app.root.playhei or \
                pos[0] < self.app.root.squsize * 2 or pos[1] < self.app.root.squsize * 2:
            return True
        else:
            return False

    def removeAll(self):
        if Player.player.tbbox:
            Map.mapvar.popupcontainer.remove_widget(Player.player.tbbox)
            Player.player.tbbox.type = ' '
            Player.player.tbbox = None
            Player.player.layout = None
        if Map.mapvar.triangle:
            Map.mapvar.background.canvas.after.remove(Map.mapvar.triangle)
            Map.mapvar.triangle = None
        if Map.mapvar.towerRange:
            Map.mapvar.background.canvas.before.remove(Map.mapvar.towerRange)
            Map.mapvar.towerRange = None
            if Map.mapvar.towerRangeExclusion:
                Map.mapvar.background.canvas.before.remove(Map.mapvar.towerRangeExclusion)
                Map.mapvar.towerRangeExclusion = None
        if self.placeholder:
            Map.mapvar.towerplaceholdercontainer.remove_widget(self.placeholder)
            self.placeholder = None
        if self.dragger:
            Map.mapvar.towerplaceholdercontainer.remove_widget(self.dragger)
            Map.mapvar.towerdragimagecontainer.clear_widgets()
            self.dragger = None
        self.popUpOpen = None

