from kivy.event import EventDispatcher
from kivy.properties import StringProperty
from kivy.properties import BooleanProperty


class EventDisp(EventDispatcher):
    Timer = StringProperty()
    Score = StringProperty()
    Money = StringProperty()
    Health = StringProperty()
    WaveNum = StringProperty()
    Gems = StringProperty()
    totalCost = StringProperty()


    def __init__(self, **kwargs):
        super(EventDisp, self).__init__(**kwargs)


# It's easiest to bind a standard event directly to the widget and callback instead of creating new events (like in this file). For example
# in GUI the checkbox for sound is bound directly to the callback in Sound.