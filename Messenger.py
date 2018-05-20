from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.animation import Animation


import __main__
import MainFunctions
import Map

class Messenger():
    def __init__(self):
        self.messageCounter = None
        self.bgrect = None

    def createAlertStreamer(self):
        self.alertQueue = []
        self.alertStreamerLayout = BoxLayout(orientation='horizontal', pos=(__main__.app.root.x, __main__.app.root.y),
                                             size=(__main__.app.root.scrwid - 10, __main__.app.root.squsize * 2 - __main__.app.root.squsize/3))
        self.alertScroller = ScrollView(do_scroll_y=False, scroll_x=1, size_hint=(None, 1),
                                        width=__main__.app.root.scrwid - 10, bar_color=[1, 1, 1, 0],
                                        bar_inactive_color=[1, 1, 1, 0])
        self.alertLayout = GridLayout(rows=1, size_hint=(None, 1), width=__main__.app.root.scrwid*2.5)
        self.alertLabel = Label(text='', color=[0, 0, 0, 1], size_hint=(1, None),
                                font_size=__main__.Window.size[0] * .05,
                                height=__main__.app.root.squsize * 2 - 10)
        self.alertLayout.add_widget((self.alertLabel))
        self.alertScroller.add_widget(self.alertLayout)
        self.alertStreamerLayout.add_widget(self.alertScroller)
        self.alertAnimation = Animation(scroll_x=0, duration=6.0)
        self.alertAnimation.bind(on_complete=self.removeAlert)
        Map.mapvar.alertStreamer = self.alertStreamerLayout
        Map.mapvar.alertStreamer.pos = (__main__.app.root.squsize*-2, __main__.app.root.squsize*-14) ##Horrible, but it works
        Map.mapvar.background.add_widget(self.alertStreamerLayout)

    def alertStreamerBinding(self):
        self.alertStreamerLayout.size = (__main__.app.root.scrwid - 10, __main__.app.root.squsize * 2-__main__.app.root.squsize/3)
        self.alertScroller.width = __main__.app.root.scrwid - 10
        self.alertLayout.width = __main__.app.root.scrwid*2
        self.alertLabel.height = __main__.app.root.squsize*2-10
        self.alertLabel.font_size = __main__.Window.size[0] * .025

    def removeAlert(self, *args):
        if self.alertAnimation.have_properties_to_animate(self.alertScroller):
            self.alertAnimation.cancel(self.alertScroller)
        if self.alertQueue:
            lastVars = self.alertQueue.pop(0)
            if lastVars[1] == 'repeat':
                self.alertAnimation.unbind(on_complete=self.repeatAlert)
                self.alertAnimation.bind(on_complete=self.removeAlert)
        self.alertLabel.text = ''
        self.alertScroller.scroll_x = 1

    def addAlert(self, alert, level):
        if self.alertQueue:
            self.removeAlert()
        self.alertQueue.append([alert, level])
        if level == 'normal':
            self.alertLabel.color = [0, 0, 0, 1]
        elif level == 'repeat':
            self.alertLabel.color = [0, 0, 0, 1]
            self.alertAnimation.unbind(on_complete=self.removeAlert)
            self.alertAnimation.bind(on_complete=self.repeatAlert)
        elif level == 'warning':
            self.alertLabel.color = [1, 0, 0, 1]
        if not self.alertAnimation.have_properties_to_animate(self.alertScroller):
            MainFunctions.dispMessage()

    def repeatAlert(self, *args):
        self.alertScroller.scroll_x = 1
        MainFunctions.dispMessage()

    def createMessage(self, msg):
        if not self.messageCounter:
            self.messageCounter = 1
            self.messageLayout = BoxLayout(orientation='horizontal')
            self.messageLabel = Label(text=msg, color=[.7, 0, 0, 1], size_hint=(None, None), font_size=__main__.app.root.scrwid*.03)
            self.messageLayout.add_widget(self.messageLabel)
            self.messageLayout.center = (__main__.app.root.center_x - self.messageLabel.width/2, __main__.app.root.center_y)
            Map.mapvar.background.add_widget(self.messageLayout)

    def removeMessage(self):
        self.messageLabel.text = ' '
        self.messageLayout.remove_widget(self.messageLabel)
        Map.mapvar.background.remove_widget(self.messageLayout)
        self.messageCounter = None

messenger = Messenger()