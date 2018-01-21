from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.image import Image
from kivy.properties import NumericProperty,ReferenceListProperty,ObjectProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.core.window import Window, WindowBase
from kivy.core.image import Image as CoreImage
from kivy.graphics import *
from functools import partial
from random import randint
from kivy.config import Config
from kivy.properties import ListProperty

import localdefs
import Player
import EventFunctions
import MainFunctions
import Map

import math



class MyButton(ButtonBehavior, Image):
    def __init__(self, **kwargs):
        super(MyButton, self).__init__(**kwargs)

    pressed = ListProperty()

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.pressed = touch.pos
            Map.mapvar.backgroundimg.remove_widget(Player.player.tbbox)
            Player.player.tbbox = None
            return True


    def on_pressed(self, instance, pos):
        EventFunctions.placeTower(instance)
        #print('pressed at {pos}'.format(pos=pos))


class MyLabel(Label):
    def __init__(self,**kwargs):
        super(MyLabel,self).__init__(**kwargs)
        self.font_size = Window.width*0.018

class SmartMenu(Widget):
    # the instance created by this class will appear
    # when the game is started for the first time
    buttonList = []

    def __init__(self, **kwargs):
        # create custom events first

        super(SmartMenu, self).__init__(**kwargs)
        self.register_event_type(
            'on_button_release')

        #self.layout = BoxLayout(orientation='vertical')
        #self.add_widget(self.layout)

    def on_button_release(self, *args):
        print ("on_button_release")

    def callback(self, instance):
        self.dispatch('on_button_release')

    def addButtons(self, buttonList):
        for button in buttonList:
            tmpbtn=MyButton(text= button)
            #tmpbtn.bind(on_release = self.callback)
            self.layout.add_widget(tmpbtn)


    def addElements(self,elementList):
        for element in elementList:
            tmplbl = MyLabel(text=element) #add variables here
            self.layout.add_widget(tmplbl)

class Menu(SmartMenu):
    # setup the menu button names

    def __init__(self, **kwargs):
        super(Menu, self).__init__(**kwargs)

        self.layout = BoxLayout(orientation='vertical')
        self.add_widget(self.layout)

        #use pos_hint to set the position relative to its parent by percentage.
        self.msg = Label(text='Testing', color=[0,0,0,1])
        self.layout.add_widget(self.msg)
        self.msg.font_size = Window.width*0.018
        with self.msg.canvas:
            Color(0, 0, 1)

class Bar(SmartMenu):
    def __init__(self,**kwargs):
        super(Bar,self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='horizontal')
        self.layout.pos = self.pos
        self.layout.size = self.size
        self.add_widget(self.layout)
        #with self.layout.canvas.before:
            #Color(.4,.4,.4,.8)
            #self.rect=Rectangle(size=self.size, pos=self.pos)
            #print (self.layout.pos, self.layout.size)



    def addButtons(self, buttonList):
        for button in buttonList:
            tmpbtn = MyButton(text=button)
            # tmpbtn.background_color = [1,1,1,1]
            #tmpbtn.bind(on_release=self.callback)
            self.layout.add_widget(tmpbtn)

    def addElements(self, elementList):
        #likely need to create individual widgets to update later.
        for element,var in elementList:
            self.element = MyLabel(text=element+str(var))  # add variables here. Right now it's just printing the value
            self.layout.add_widget(self.element)
            #with tmplbl.canvas:
            #    Color(.4, .4, .4, .8)
            #    self.rect=Rectangle(size=tmplbl.size, pos=tmplbl.pos)

    def updateElements(self,elementlist):
        pass

def createBottomBar():
    bottomBar=Bar(pos=(0,0), size = (Window.width,80))
    for button in localdefs.iconlist:
        tmpbtn = MyButton()
        tmpbtn.text=button.type
        tmpbtn.type = button.type
        tmpbtn.img = button.img
        # tmpbtn.background_color = [1,1,1,1]
        #tmpbtn.bind(on_release=bottomBar.callback)

        #tmpbtn.bind(on_release=MainFunctions.towerButtonPressed)
        bottomBar.layout.add_widget(tmpbtn)
    return bottomBar

def createTopBar():
    topBar=Bar(pos=(0,Window.height-50), size = (Window.width,50))
    #topBar.addElements([(1,2),(3,4)])
    return topBar

def builderMenu(squarepos):

    Player.player.tbbox = FloatLayout(size = (180, 180), pos = (squarepos[0]-Map.squsize*2, squarepos[1]-Map.squsize*2))

    layout = BoxLayout(size=(Map.squsize*2,Map.squsize*2), pos = squarepos)
    Player.player.tbbox.add_widget(layout)
    with layout.canvas.before:
        Color(0, 0, 0,.3)
        rect2 = Line(circle=(layout.pos[0]+Map.squsize, layout.pos[1]+Map.squsize, 100))
        Color(1,1,.5,.3)
        rect = Rectangle(size=layout.size, pos=layout.pos)


    tbbuttonnum = len(localdefs.iconlist)
    radius = 70
    inddeg = (2.0 * math.pi) / tbbuttonnum
    for ind, button in enumerate(localdefs.iconlist):
        tmpbtn = MyButton()
        tmpbtn.button = button
        tmpbtn.text=button.type
        tmpbtn.size_hint=(.3, .3)
        tmpbtn.size = (20,20)
        tmpbtn.source = button.imgstr
        tmpbtn.type = button.type
        Player.player.tbbox.add_widget(tmpbtn)
        tmpbtn.pos = (layout.x + radius * math.cos((ind) * inddeg),(layout.y - radius * math.sin((ind) * inddeg)))

        #partial(EventFunctions.placeTower,tmpbtn.pos,button.type)
        #print(Player.player.tbbox.center, Player.player.tbbox.size, touchpos, "name:", tmpbtn.size, tmpbtn.text, tmpbtn.center)


    Map.mapvar.backgroundimg.add_widget(Player.player.tbbox)

