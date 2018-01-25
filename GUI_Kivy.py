from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.core.window import Window, WindowBase
from kivy.properties import ListProperty
from kivy.graphics import *

import localdefs
import Player
import EventFunctions
import MainFunctions
import Map
import Utilities

import math
import os



class MyButton(ButtonBehavior, Image):
    def __init__(self, **kwargs):
        super(MyButton, self).__init__(**kwargs)

    pressed = ListProperty()

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.pressed = touch.pos
            Map.mapvar.backgroundimg.remove_widget(Player.player.tbbox)
            Player.player.tbbox = None
            Player.player.layout = None
            return True


    def on_pressed(self, button, pos):
        print ("in on_pressed from GUI")
        if button.id == 'unpause':
            MainFunctions.pauseGame(button)
            return
        elif button.instance  in localdefs.towerabilitylist:
            func = "TowerAbilities."+button.instance.type +"."+ button.instance.func + "()"
            print (func)
            print("eval func: ",eval(func))
            return
        else:
            EventFunctions.placeTower(button)
        #print('pressed at {pos}'.format(pos=pos))


class MyLabel(Label):
    def __init__(self,**kwargs):
        super(MyLabel,self).__init__(**kwargs)
        self.font_size = Window.width*0.018

class SmartMenu(Widget):
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
            tmpbtn=MyButton()
            tmpbtn.text = button
            #tmpbtn.bind(on_release = self.callback)
            self.layout.add_widget(tmpbtn)


    def addElements(self,elementList):
        for element in elementList:
            tmplbl = MyLabel(text=element) #add variables here
            self.layout.add_widget(tmplbl)

class pauseMenu(SmartMenu):
    # setup the menu button names

    def __init__(self, **kwargs):
        super(pauseMenu, self).__init__(**kwargs)
        self.unpause = Button()
        self.unpause.size_hint=(None,None)
        self.unpause.size = (Map.scrwid, Map.scrhei)
        self.unpause.pos = (0,0)
        self.unpause.id = 'unpause'
        #self.unpause.bind(on_release = MainFunctions.pauseGame)
        self.image = Utilities.imgLoad('backgroundimgs/play.png', pos = self.unpause.center)
        self.image.size = (20,20)
        self.unpause.add_widget(self.image)
        self.unpause.background_color = [.2,.2,.2,.2]
        self.add_widget(self.unpause)
        #with self.unpause.canvas.before:
         #   Color(.2,.2,.2,.1)
         #   Rectangle(size = self.unpause.size, pos=self.unpause.pos)



class mainMenu(SmartMenu):
    # setup the menu button names

    def __init__(self, **kwargs):
        super(mainMenu, self).__init__(**kwargs)

        self.layout = BoxLayout(orientation='vertical', size=(300,500))
        self.layout.center = ((Map.scrwid-self.width)/2,(Map.scrhei-self.height)/2)
        self.layout.padding = [20]
        self.layout.spacing = 20
        self.id ='mainmenu'
        self.add_widget(self.layout)

        #use pos_hint to set the position relative to its parent by percentage.
        self.menulabel = Label(text='Main Menu')
        self.layout.add_widget(self.menulabel)
        self.menulabel.font_size = Window.width*0.018

        with self.layout.canvas.before:
            Color(.3, .3, .3)
            Rectangle(size = self.layout.size, pos=self.layout.pos)
        with self.canvas.before:
            Color(.2,.2,.2,.2)
            Rectangle(size = (Map.scrwid, Map.scrhei), pos=(0,0))


        self.startButton = Button()
        self.startButton.text='Play'
        self.startButton.instance = None
        #self.startButton.bind(on_release=MainFunctions.startGame)

        self.restartButton = Button()
        self.restartButton.text='Restart'
        self.restartButton.instance = None

        self.layout.add_widget(self.startButton)
        self.layout.add_widget(self.restartButton)


class GUI():
    def __init__(self):

        self.topBar_Boxlist = []
        self.topBar_ElementList = [("Wave: ", str(Player.player.wavenum), "iconimgs/default.png"),
                       ("Score: ", str(Player.player.kill_score)+" + "+str(Player.player.bonus_score), "iconimgs/100.png"),
                       ("Money: ", str(Player.player.money), "iconimgs/coin20x24.png"),
                       ("Health: ", str(Player.player.health), "iconimgs/heart24x24.png"), ("Timer: ", '999', "iconimgs/clock.png")]


    def createTopBar(self):
        self.topBar=Bar(pos=(0,Window.height-45), size = (Window.width,45))

        #with self.topBar.layout.canvas.before:
            #Color(.4,.4,.4,.8)
            #self.rect=Rectangle(size=self.topBar.size, pos=self.topBar.pos)
        #icon should be .png in the iconimgs folder with name "icon"

        self.menuButton = Button(text='Menu', id='menu', size_hint=(None,None), width=50, height=30)
        self.menuButton.bind(on_release = MainFunctions.pauseGame)
        self.pauseButton = Button(text='Pause', id ='pause', size_hint=(None,None), width=50, height=30)
        self.pauseButton.bind(on_release=MainFunctions.pauseGame)
        self.nextwaveButton = Button(text = 'Next Wave', id = 'next', size_hint=(None,None), width=80, height=30)
        self.nextwaveButton.bind(on_release=EventFunctions.nextWave)
        self.nextwaveButton.background_color = [1,1,1,1]
        self.nextwaveButton.background_normal=''
        self.nextwaveButton.color=[0,0,0,1]
        self.nextwaveButton.valign = 'top'
        self.topBar.layout.add_widget(self.menuButton)
        self.topBar.layout.add_widget(self.pauseButton)
        self.topBar.layout.add_widget(self.nextwaveButton)
        self.topBar.layout.padding=[5]
        self.topBar.addElements(self.topBar_ElementList)
        return self.topBar

    def updateTopBar(self, wavetime):
        self.topBar_Boxlist[0].children[0].text = str(Player.player.wavenum)
        self.topBar_Boxlist[1].children[0].text = str(int(Player.player.kill_score))+" + "+str(int(Player.player.bonus_score))
        self.topBar_Boxlist[2].children[0].text = str(Player.player.money)
        self.topBar_Boxlist[3].children[0].text = str(Player.player.health)
        self.topBar_Boxlist[4].children[0].text = str(int(wavetime))

        if Player.player.towerSelected != None:
            self.topSideBar_header.text=Player.player.towerSelected.type + "Tower"
            self.topSideBar_image.source = os.path.join(Player.player.towerSelected.imagestr)
            self.topSideBar_image.color = [1,1,1,1]
            print (self.topSideBar_image.pos)
            self.topSideBar_towerinfo.text="Range:  "+str(Player.player.towerSelected.range)+\
                                           " Damage:  "+str(Player.player.towerSelected.damage)+\
                                           " DPS: "+str(int(Player.player.towerSelected.damage/Player.player.towerSelected.reload))+\
                                           " Reload:  "+str(Player.player.towerSelected.reload)
        else:
            self.topSideBar_header.text=''
            self.topSideBar_towerinfo.text=''


        ##Potential button/UI changes
        with self.nextwaveButton.canvas:
            Color(.4, .4, .4,.7)
            #Line(rectangle=(self.nextwaveButton.pos[0]+3, self.nextwaveButton.pos[1]+3, self.nextwaveButton.width-6,
             #                       self.nextwaveButton.height-6), width=1.4)
            Line(points=[self.nextwaveButton.x+2, self.nextwaveButton.y+2,self.nextwaveButton.x+self.nextwaveButton.width-2,
                         self.nextwaveButton.y+2,self.nextwaveButton.x+self.nextwaveButton.width-2, self.nextwaveButton.y+self.nextwaveButton.height-2], width=2.2, cap = 'square')
            # Line(rectangle=(self.nextwaveButton.pos[0]+3, self.nextwaveButton.pos[1]+3, self.nextwaveButton.width-6,
            #                       self.nextwaveButton.height-6), width=1.4)
            Line(points=[self.nextwaveButton.x+1, self.nextwaveButton.y+2,self.nextwaveButton.x+1,
                         self.nextwaveButton.y+self.nextwaveButton.height-1,self.nextwaveButton.x+self.nextwaveButton.width-1, self.nextwaveButton.y+self.nextwaveButton.height-1],
                 width=.6, cap='square')
            #Line(points=[self.nextwaveButton.x+self.nextwaveButton.width, self.nextwaveButton.y, self.nextwaveButton.x+self.nextwaveButton.width-2, self.nextwaveButton.y+2], width=.4)

    def createTopSideBar(self):
        self.topSideBar=Bar(size=(270, (Window.height - 65)/2))
        self.topSideBar.pos = (Window.width - self.topSideBar.width-5, (Window.height-55-self.topSideBar.height))
        self.topSideBar.layout.pos = self.topSideBar.pos
        self.topSideBar.layout.orientation = 'vertical'
        with self.topSideBar.layout.canvas.before:
            Color(1,1,1,.6)
            Line(rounded_rectangle = (self.topSideBar.x, self.topSideBar.y, self.topSideBar.width, self.topSideBar.height, 20, 20, 20, 20, 100), width = 2)


        self.topSideBar_header = MyLabel(text='')
        self.topSideBar_image = Image(size = (60,60), pos = self.topSideBar.layout.center, color=(0,0,0,0))
        self.topSideBar_towerinfo = MyLabel(text='', text_size = [150,120])
        self.topSideBar.layout.add_widget(self.topSideBar_header)
        self.topSideBar.layout.add_widget(self.topSideBar_image)
        self.topSideBar.layout.add_widget(self.topSideBar_towerinfo)

        return self.topSideBar

    def createBottomSideBar(self):
        self.bottomSideBar = Bar(size=(270, (Window.height - 65) / 2))
        self.bottomSideBar.pos = (Window.width - self.topSideBar.width - 5, 5)
        self.bottomSideBar.layout.pos = self.bottomSideBar.pos
        self.bottomSideBar.layout.orientation = 'vertical'
        with self.bottomSideBar.layout.canvas.before:
            Color(1,1,1,.6)
            Line(rounded_rectangle = (self.bottomSideBar.x, self.bottomSideBar.y, self.bottomSideBar.width, self.bottomSideBar.height, 20, 20, 20, 20, 100), width = 2)

        self.bottomSideBar_Element = MyLabel(text="hi")
        self.bottomSideBar.layout.add_widget((self.bottomSideBar_Element))

        return self.bottomSideBar

    def createTBBox(self, squarepos):

        Player.player.tbbox = FloatLayout(size=(180, 180),
                                          pos=(squarepos[0] - Map.squsize * 2, squarepos[1] - Map.squsize * 2))
        Player.player.layout = BoxLayout(size=(Map.squsize * 2, Map.squsize * 2), pos=squarepos)
        Player.player.tbbox.add_widget(Player.player.layout)
        with Player.player.layout.canvas.before:
            Color(0, 0, 0, .3)
            circle = Line(circle=(Player.player.layout.pos[0] + Map.squsize, Player.player.layout.pos[1] + Map.squsize, 100))
            Color(.1, .1, .1, .1)
            rect = Rectangle(size=Player.player.layout.size, pos=Player.player.layout.pos)

    def towerMenu(self, squarepos):
        self.createTBBox(squarepos)

        tbbuttonnum = len(localdefs.towerabilitylist)
        radius = 70
        inddeg = (2.0 * math.pi) / tbbuttonnum
        for ind,instance in enumerate(localdefs.towerabilitylist):
            print(ind,instance)
            tmpbtn = MyButton()
            tmpbtn.instance = instance
            tmpbtn.text = instance.type
            tmpbtn.size_hint = (.3, .3)
            tmpbtn.size = (20, 20)
            tmpbtn.source = instance.imgstr
            Player.player.tbbox.add_widget(tmpbtn)
            tmpbtn.pos = (Player.player.layout.x + radius * math.cos((ind) * inddeg), (Player.player.layout.y - radius * math.sin((ind) * inddeg)))
            #print(Player.player.tbbox.center, Player.player.tbbox.size, squarepos, "name:", tmpbtn.size, tmpbtn.text, tmpbtn.center)
        Map.mapvar.backgroundimg.add_widget(Player.player.tbbox)


    def builderMenu(self,squarepos):
        self.createTBBox(squarepos)

        tbbuttonnum = len(localdefs.iconlist)
        radius = 70
        inddeg = (2.0 * math.pi) / tbbuttonnum
        for ind, button in enumerate(localdefs.iconlist):
            tmpbtn = MyButton()
            tmpbtn.instance = button
            tmpbtn.text=button.type
            tmpbtn.size_hint=(.3, .3)
            tmpbtn.size = (20,20)
            tmpbtn.source = button.imgstr
            Player.player.tbbox.add_widget(tmpbtn)
            tmpbtn.pos = (Player.player.layout.x + radius * math.cos((ind) * inddeg),(Player.player.layout.y - radius * math.sin((ind) * inddeg)))

            #print(Player.player.tbbox.center, Player.player.tbbox.size, touchpos, "name:", tmpbtn.size, tmpbtn.text, tmpbtn.center)


        Map.mapvar.backgroundimg.add_widget(Player.player.tbbox)

gui = GUI()

class Bar(SmartMenu):
    def __init__(self,**kwargs):
        super(Bar,self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='horizontal')
        self.layout.pos = self.pos
        self.layout.size = self.size
        self.add_widget(self.layout)

    def addButtons(self, buttonList):
        for button in buttonList:
            tmpbtn = MyButton(text=button)
            # tmpbtn.background_color = [1,1,1,1]
            #tmpbtn.bind(on_release=self.callback)
            self.layout.add_widget(tmpbtn)

    def addElements(self, elementList):
        #likely need to create individual widgets to update later.
        for element,var,icon in elementList:
            box = GridLayout(cols=3, col_force_default = True, row_force_default=True, row_default_height=50, col_default_width=55)
            label = MyLabel(text=element)
            variable = MyLabel(text=str(var))
            icon = Utilities.imgLoad(icon)
            icon.size_hint_x = None
            icon.size = (30,30)
            label.size_hint_x=None
            label.size = (40,50)
            #nlabel.valign='center'
            variable.size_hint_x = None
            variable.size = (90,50)
            box.add_widget(icon)
            box.add_widget(label)
            box.add_widget(variable)
            gui.topBar_Boxlist.append(box)
            self.layout.add_widget(box)

            #with tmplbl.canvas:
            #    Color(.4, .4, .4, .8)
            #    self.rect=Rectangle(size=tmplbl.size, pos=tmplbl.pos)