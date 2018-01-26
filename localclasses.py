from kivy.event import EventDispatcher
from kivy.properties import StringProperty, NumericProperty

class EventDisp(EventDispatcher):
    Timer = StringProperty()
    Wave = StringProperty()
    Score = StringProperty()
    Money = StringProperty()
    Health = StringProperty()
    WaveNum = NumericProperty()

    def __init__(self,**kwargs):
        super(EventDisp, self).__init__(**kwargs)

    def callback(instance, instance2, *args):
        print('My callback is call from', instance)
        print('and the value changed to', instance2, args[0])