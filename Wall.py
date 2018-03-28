from kivy.uix.widget import Widget
from kivy.graphics import *

import Map


class Wall(Widget):
    def __init__(self,**kwargs):
        super(Wall,self).__init__(**kwargs)
        self.squpos = kwargs['squpos']
        self.pos = (self.squpos[0]*Map.mapvar.squsize, self.squpos[1]*Map.mapvar.squsize)
        self.size = (Map.mapvar.squsize-1, Map.mapvar.squsize-1)
        self.bind(size = self.bindings)
        Map.mapvar.wallcontainer.add_widget(self)
        #wall visualization
        # with Map.mapvar.backgroundimg.canvas.after:
        #     Color(0,0,0,1)
        #     Rectangle(pos=self.pos, size=self.size)

    def bindings(self):
        self.size = (Map.mapvar.squsize, Map.mapvar.squsize)