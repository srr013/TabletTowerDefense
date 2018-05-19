from kivy.uix.behaviors import DragBehavior
from kivy.uix.image import Image
from kivy.app import App

import Map
import Player
import Utilities


class TowerDragger(DragBehavior, Image):
    """The Dragger is the image you move from the initial point of contact. The current implementation builds towers in
    a straight line."""
    def __init__(self, **kwargs):
        super(TowerDragger, self).__init__(**kwargs)
        self.app = App.get_running_app()
        self.drag_rectangle = (0, 0,
                               self.app.root.scrwid - 4 * self.app.root.squsize, self.app.root.scrhei - 5 * self.app.root.squsize,)
        self.drag_timeout = 120000
        self.drag_distance = 1
        self.color = [1, 1, 1, .6]
        self.source = 'towerimgs/0.png'
        self.allow_stretch = True
        self.size = (self.app.root.squsize * 2 - 1, self.app.root.squsize * 2 - 1)
        self.pos = kwargs['pos']
        Map.mapvar.towerplaceholdercontainer.add_widget(self)
        self.bind(on_touch_up=self.touch_up)
        self.lastpos = None
        self.placeholder = Map.mapvar.background.placeholder
        self.towerposlist = []
        self.framecount = 0

    def touch_up(self, *args):
        if self.towerposlist:
            Map.mapvar.towerdragimagecontainer.clear_widgets()
            self.towerposlist = []
        self.pos = Utilities.roundPoint(self.pos)
        self.pos = Map.mapvar.background.adjustInBounds(self.pos)
        if self.collide_widget(Map.mapvar.background.placeholder):
            self.pos = Map.mapvar.background.placeholder.pos
        if self.pos[0] >= self.placeholder.right:
            Player.player.tbbox.pos = (
                self.placeholder.pos[0] - Player.player.tbbox.size[0]-self.app.root.squsize, Player.player.tbbox.pos[1])
            if Player.player.tbbox.pos[0] <= 0:
                Player.player.tbbox.pos = (5, Player.player.tbbox.pos[1])
        elif self.pos[0] < self.placeholder.pos[0] and Player.player.tbbox.pos[0] < self.placeholder.pos[0]:
            Player.player.tbbox.pos = (self.placeholder.pos[0] + 3 * self.app.root.squsize, Player.player.tbbox.pos[1])
            if Player.player.tbbox.right > self.app.root.scrwid:
                Player.player.tbbox.set_right(self.app.root.scrwid-5)
        delta_x, delta_y = (self.pos[0] - self.placeholder.pos[0], self.pos[1] - self.placeholder.pos[1])
        axis = self.genTowerPos(delta_x, delta_y)
        if axis == 'x':
            self.pos[1] = self.placeholder.pos[1]
        else:
            self.pos[0] = self.placeholder.pos[0]
        totalCost = len(self.towerposlist)*15
        Player.player.myDispatcher.totalCost = str(totalCost)

        x = 1  # x is 1 to ignore the initial tower
        while x < len(self.towerposlist):
            if x == len(self.towerposlist) - 1:
                self.pos = self.towerposlist[x]
                return
            TowerPlaceholder(pos=self.towerposlist[x], initial=False)
            x += 1

        # self.towerposlist.add((self.pos[0], self.pos[1]))

    def addToList(self, pos):
        self.towerposlist.append(pos)

    def genTowerPos(self, delta_x, delta_y):
        towers_x = (delta_x / (self.app.root.squsize * 2.0))
        towers_y = (delta_y / (self.app.root.squsize * 2.0))
        self.towerposlist.append((self.placeholder.pos[0], self.placeholder.pos[1]))

        # only allow straight lines - get x/y depending on the larger of the two.
        if abs(towers_x) >= abs(towers_y):
            x = 1
            y = 0
            while x <= abs(towers_x):
                if towers_x > 0:
                    self.addToList((self.placeholder.pos[0] + 2 * x * self.app.root.squsize,
                                    self.placeholder.pos[1] + 2 * y * self.app.root.squsize))
                elif towers_x < 0:
                    self.addToList((self.placeholder.pos[0] - 2 * x * self.app.root.squsize,
                                    self.placeholder.pos[1] - 2 * y * self.app.root.squsize))
                x += 1
            return 'x'
        else:
            y = 1
            x = 0
            while y <= abs(towers_y):
                if towers_y > 0:
                    self.addToList((self.placeholder.pos[0] + 2 * x * self.app.root.squsize,
                                    self.placeholder.pos[1] + 2 * y * self.app.root.squsize))
                elif towers_y < 0:
                    self.addToList((self.placeholder.pos[0] + 2 * x * self.app.root.squsize,
                                    self.placeholder.pos[1] - 2 * y * self.app.root.squsize))
                y += 1
            return 'y'

    def removeTowerImgs(self):
        self.app.root.towerdragimagecontainer.clear_widgets()


class TowerPlaceholder(Image):
    """The placeholder sits at the initial point of contact."""
    def __init__(self, **kwargs):
        super(TowerPlaceholder, self).__init__(**kwargs)
        app = App.get_running_app()
        self.color = [1, 1, 1, .4]
        self.source = 'towerimgs/0.png'
        self.initial = kwargs['initial']
        self.pos = kwargs['pos']
        self.allow_stretch = True
        self.size = (app.root.squsize * 2 - 1, app.root.squsize * 2 - 1)
        self.isNew = True
        for child in Map.mapvar.towerdragimagecontainer.children:
            if child.pos == self.pos:
                self.isNew = False
        if self.isNew and not self.initial:
            Map.mapvar.towerdragimagecontainer.add_widget(self)
        if self.initial:
            Map.mapvar.towerplaceholdercontainer.add_widget(self)
