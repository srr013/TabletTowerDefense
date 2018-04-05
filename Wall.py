from kivy.uix.widget import Widget

import Map


class Wall(Widget):
    """Walls block the enemy from passing and help check if 2 towers are overlapping. Use the wall visualization to
    see where walls exist in game."""
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