
from kivy.core.window import Window
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout

from kivy.properties import ListProperty
from kivy.graphics import *

import EventFunctions
import GUI
import Localdefs
import MainFunctions
import Map
import Player
import __main__
import TowerAbilities


class MyButton(ButtonBehavior, Image):
    def __init__(self, **kwargs):
        super(MyButton, self).__init__(**kwargs)

    pressed = ListProperty()

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.pressed = touch.pos
            Map.mapvar.background.removeAll()
            return True

    def on_pressed(self, button, pos):
        if button.disabled == False:
            if button.id == 'unpause':
                MainFunctions.pauseGame(button)
                return
            # # if button.id == 'enemyinfo':
            # #     gui.toggleEnemyPanel()
            # #tower abilities like upgrade and sell
            # elif button.instance  in Localdefs.towerabilitylist:
            #     func = "TowerAbilities."+button.instance.type +"."+ button.instance.func + "()"
            #     eval(func)
            #     return
            # else:
            #     Map.mapvar.background.popUpOpen = None
            #     EventFunctions.placeTower(button)
        # print('pressed at {pos}'.format(pos=pos))


class ButtonWithImage(Button, Image):
    pressed = ListProperty()

    def __init__(self, **kwargs):
        super(ButtonWithImage, self).__init__(**kwargs)
        self.image = Image()
        self.image.pos_hint = (None, None)
        self.add_widget(self.image)
        self.image.size = self.size
        self.image.pos = self.pos
        self.bind(pos=self.on_pos)
        self.label = Label(text=' ', size_hint=(None, None), pos=self.pos, color=[1, 1, 1, 1], halign='center')
        self.add_widget(self.label)
        self.group = None
        self.toplabel = Label(text='', size_hint=(1, .1), pos_hint=(None,None), text_size = (None, None), font_size = __main__.Window.size[0]*.01)
        self.add_widget(self.toplabel)
        self.toplabel.pos = (self.toplabel.x-(Map.mapvar.squsize*.35),self.toplabel.y + (Map.mapvar.squsize*.35))

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.pressed = touch.pos
            if self.id == 'enemyinfo' or self.id == 'Rotate':
                pass
            else:
                pass
                # Map.mapvar.background.removeAll()
            return True

    def on_pressed(self, button, pos):
        if button.disabled == False:
            # if button.id == 'unpause':
            #     MainFunctions.pauseGame(button)
            #     return
            if button.id == 'enemyinfo':
                GUI.gui.toggleEnemyPanel()
            elif button.id =='towerinfo':
                GUI.gui.toggleTowerPanel()
            # tower abilities like upgrade and sell
            elif button.instance in Localdefs.towerabilitylist:
                func = "TowerAbilities." + button.instance.type + "." + button.instance.func + "()"
                eval(func)
                if button.id == 'Rotate':
                    GUI.gui.removeTriangle()
                    GUI.gui.drawTriangle()
                    return
                Map.mapvar.background.removeAll()
                return
            else:
                if not button.disabled:
                    EventFunctions.placeTowerFromList(button)
                    Map.mapvar.background.popUpOpen = None
                    Map.mapvar.background.removeAll()
                else:
                    return
            # print('pressed at {pos}'.format(pos=pos))

    def on_pos(self, *args):
        self.image.pos = self.pos
        self.image.size = self.size
        self.label.pos = self.pos
        self.toplabel.size = (self.width, self.height*.2)
        self.toplabel.pos = (self.x, self.top - self.toplabel.size[1] - Map.mapvar.squsize/8)

class StackButtonWithImage(Button):
    pressed = ListProperty()
#Used for multi-path upgrade buttons
    def __init__(self, **kwargs):
        super(StackButtonWithImage, self).__init__(**kwargs)
        self.group = None
        self.layout = GridLayout(cols=2, size = self.size)
        self.layoutImg = Image(text='', size_hint=(None,None))
        self.layout.add_widget(self.layoutImg)
        self.layoutLbl = Label(text='')
        self.layout.add_widget(self.layoutLbl)
        self.layoutLbl.text_size = self.layout.size
        self.add_widget(self.layout)
        self.bind(pos=self.on_pos)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.pressed = touch.pos
            if self.id == 'enemyinfo' or self.id == 'Rotate':
                pass
            else:
                pass
                # Map.mapvar.background.removeAll()
            return True

    def on_pressed(self, button, pos):
        print 'Damage' in self.id
        if self.id == 'LeaderPath' or 'Damage' in self.id:
            func = "TowerAbilities." + button.instance.type + "." + button.instance.func + "(id=self.id)"
            eval(func)
            Map.mapvar.background.removeAll()
        return True

    def on_pos(self, *args):
        self.layout.pos = self.pos
        self.layout.size = self.size
        self.layoutLbl.size = (self.width*.75, self.height)
        self.layoutLbl.text_size = self.layoutLbl.size

class MyLabel(Label):
    def __init__(self, **kwargs):
        super(MyLabel, self).__init__(**kwargs)
        self.font_size = Window.width * 0.018
        self.color = [0, 0, 0, 1]


class SmartMenu(Widget):
    buttonList = []

    def __init__(self, **kwargs):
        # create custom events first

        super(SmartMenu, self).__init__(**kwargs)
        self.register_event_type(
            'on_button_release')

        # self.layout = BoxLayout(orientation='vertical')
        # self.add_widget(self.layout)

    def on_button_release(self, *args):
        print ("on_button_release")

    def callback(self, instance):
        self.dispatch('on_button_release')

    def addButtons(self, buttonList):
        for button in buttonList:
            tmpbtn = MyButton()
            tmpbtn.text = button
            # tmpbtn.bind(on_release = self.callback)
            self.layout.add_widget(tmpbtn)

    def addElements(self, elementList):
        for element in elementList:
            tmplbl = MyLabel(text=element)  # add variables here
            self.layout.add_widget(tmplbl)



class MyCheckBox(BoxLayout):
    def __init__(self, **kwargs):
        super(MyCheckBox, self).__init__(**kwargs)
        self.orientation='horizontal'
        self.label = Label(text='')
        self.checkbox = CheckBox()
        self.checkbox.bind(active=self.on_checkbox_active)
        self.add_widget(self.label)
        self.add_widget(self.checkbox)

    def on_checkbox_active(self, checkbox, value):
        if checkbox.id == 'sound':
            GUI.gui.myDispatcher.sound = value
        elif checkbox.id == 'music':
            GUI.gui.myDispatcher.music = value
