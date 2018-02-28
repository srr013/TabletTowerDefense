from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.image import Image
from kivy.core.window import Window, WindowBase
from kivy.properties import ListProperty, StringProperty, NumericProperty
from kivy.graphics import *
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelContent, TabbedPanelHeader
from kivy.lang import Builder

import Localdefs
import EventDispatcher
import Player
import EventFunctions
import MainFunctions
import Map
import Utilities
import Enemy
import TowerAbilities

import math
import os
import operator



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
        if button.id == 'unpause':
            MainFunctions.pauseGame(button)
            return
        if button.id == 'enemyinfo':
            gui.toggleEnemyPanel()
        #tower abilities like upgrade and sell
        elif button.instance  in Localdefs.towerabilitylist:
            func = "TowerAbilities."+button.instance.type +"."+ button.instance.func + "()"
            eval(func)
            return
        else:
            Map.mapvar.background.popUpOpen = None
            EventFunctions.placeTower(button)
        #print('pressed at {pos}'.format(pos=pos))

class ButtonWithImage(Button, Image):
    pressed = ListProperty()
    def __init__(self, **kwargs):
        super(ButtonWithImage, self).__init__(**kwargs)
        self.image = Image(text = " ")
        self.add_widget(self.image)
        self.image.size = self.size
        self.image.pos = self.pos
        self.bind(pos=self.on_pos)
        self.label = Label(text=' ', size_hint=(None,None), pos=(self.x, self.pos[1]), size=(50,20), color=[1,1,1,1], halign='center')
        self.image.add_widget(self.label)


    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.pressed = touch.pos
            Map.mapvar.backgroundimg.remove_widget(Player.player.tbbox)
            Player.player.tbbox = None
            Player.player.layout = None
            return True


    def on_pressed(self, button, pos):
        if button.id == 'unpause':
            MainFunctions.pauseGame(button)
            return
        if button.id == 'enemyinfo':
            gui.toggleEnemyPanel()
        #tower abilities like upgrade and sell
        elif button.instance  in Localdefs.towerabilitylist:
            func = "TowerAbilities."+button.instance.type +"."+ button.instance.func + "()"
            eval(func)
            return
        else:
            EventFunctions.placeTower(button)
            Map.mapvar.background.popUpOpen = None
        #print('pressed at {pos}'.format(pos=pos))
    def on_pos(self, *args):
        self.image.pos = self.pos
        self.image.size = self.size
        self.label.pos = self.pos

class MyLabel(Label):
    def __init__(self,**kwargs):
        super(MyLabel,self).__init__(**kwargs)
        self.font_size = Window.width*0.018
        self.color = [0,0,0,1]

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

        self.layout = BoxLayout(orientation='vertical', size=(300,300))
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

class topBarWidget():
    def __init__(self, label, var,source,icon):
        self.Box = GridLayout(cols=3, col_force_default=True, row_force_default=True, row_default_height=50,
                         col_default_width=45)
        self.Label = MyLabel(text=label)

        self.Variable = MyLabel(text=str(source), halign='right')
        gui.myDispatcher.fbind(var, self.set_value, var)
        self.Icon = Utilities.imgLoad(icon)
        self.Icon.size_hint_x = None
        self.Icon.size = (30, 30)
        self.Label.size_hint_x = None
        self.Label.size = (30, 50)
        self.Variable.size_hint_x = None
        self.Variable.size = (50, 50)
        self.Box.add_widget(self.Icon)
        self.Box.add_widget(self.Label)
        self.Box.add_widget(self.Variable)
        gui.topBar_Boxlist.append(self.Box)
        gui.topBar.layout.add_widget(self.Box)

    def set_value(self, *args):
        self.Variable.text = args[2]

class GUI():
    def __init__(self):

        self.topBar_Boxlist = []
        self.myDispatcher = EventDispatcher.EventDisp()

    def rightSideButtons(self):
        self.rightSideButtons_layout=StackLayout(size_hint=(None,None), size=(50,70), pos=(Map.scrwid-55, 40))
        self.enemyInfoButton = ButtonWithImage(text=" ",id='enemyinfo', size_hint=(None,None), width=50, height=50)
        self.enemyInfoButton.image.source = "enemyimgs/Standard.png"
        self.enemyInfoButton.label.text = 'Info'
        #self.enemyInfoButton.bind(on_release=self.openEnemyPanel)
        self.rightSideButtons_layout.add_widget(self.enemyInfoButton)
        return self.rightSideButtons_layout
    def toggleEnemyPanel(self):
        if not Map.mapvar.enemypanel.parent:
            Map.mapvar.backgroundimg.add_widget(Map.mapvar.enemypanel)
            Map.mapvar.enemypanel.switch_to(Map.mapvar.enemypanel.getDefaultTab())
            Map.mapvar.background.popUpOpen = Map.mapvar.enemypanel
        else:
            Map.mapvar.backgroundimg.remove_widget(Map.mapvar.enemypanel)

    def createTopBar(self):
        self.topBar=Bar(pos=(0,Window.height-45), size = (Window.width,45))
        self.menuButton = Button(text='Menu', id='menu', size_hint=(None,None), width=50, height=30)
        self.menuButton.bind(on_release = MainFunctions.pauseGame)
        self.pauseButton = Button(text='Pause', id ='pause', size_hint=(None,None), width=50, height=30)
        self.pauseButton.bind(on_release=MainFunctions.pauseGame)
        self.nextwaveButton = Button(text = 'Next Wave', id = 'next', size_hint=(None,None), width=80, height=30)
        self.nextwaveButton.bind(on_release=EventFunctions.nextWave)
        self.nextwaveButton.valign = 'top'
        self.topBar.layout.add_widget(self.menuButton)
        self.topBar.layout.add_widget(self.pauseButton)
        self.topBar.layout.add_widget(self.nextwaveButton)
        self.topBar.layout.padding=[5]
        for label,var,source,icon in Localdefs.topBar_ElementList:
            topBarWidget(label,var,source, icon)

        return self.topBar

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

        self.bottomSideBar_header = MyLabel(text='')
        self.bottomSideBar_image = Image(size=(60, 60), pos=self.topSideBar.layout.center, color=(0, 0, 0, 0))
        self.bottomSideBar_nextEnemies = MyLabel(text='Next Enemies:', text_size = [150, 60])
        self.bottomSideBar_enemyinfo = GridLayout(cols=2, col_force_default=True, row_force_default=True,
                                                  row_default_height=30, col_default_width=90)
        self.bottomSideBar_enemyinfo_numEnemies = MyLabel(text='')
        self.bottomSideBar_enemyinfo_enemyHealth = MyLabel(text='')
        self.bottomSideBar_enemyinfo_enemySpeed = MyLabel(text='')
        self.bottomSideBar_enemyinfo_enemyArmor = MyLabel(text='')
        self.bottomSideBar_enemyinfo_enemyMods = MyLabel(text='')
        self.bottomSideBar_enemyinfo_enemyReward = MyLabel(text='')
        self.bottomSideBar_enemyinfo_isBoss = MyLabel(text='')

        self.myDispatcher.bind(WaveNum=self.setBottomBar)
        self.bottomSideBar_enemyinfo.add_widget(self.bottomSideBar_enemyinfo_numEnemies)
        self.bottomSideBar_enemyinfo.add_widget(self.bottomSideBar_enemyinfo_enemyHealth)
        self.bottomSideBar_enemyinfo.add_widget(self.bottomSideBar_enemyinfo_enemySpeed)
        self.bottomSideBar_enemyinfo.add_widget(self.bottomSideBar_enemyinfo_enemyArmor)
        self.bottomSideBar_enemyinfo.add_widget(self.bottomSideBar_enemyinfo_enemyMods)
        self.bottomSideBar_enemyinfo.add_widget(self.bottomSideBar_enemyinfo_enemyReward)
        self.bottomSideBar_enemyinfo.add_widget(self.bottomSideBar_enemyinfo_isBoss)
        self.bottomSideBar.layout.add_widget(self.bottomSideBar_header)
        self.bottomSideBar.layout.add_widget(self.bottomSideBar_image)
        self.bottomSideBar.layout.add_widget(self.bottomSideBar_enemyinfo)
        self.bottomSideBar.layout.add_widget(self.bottomSideBar_nextEnemies)

        return self.bottomSideBar

    def setBottomBar(self, *args):
        #see wavegen for dict creation
        wavedict = Player.player.waveList
        i = int(Player.player.wavenum)
        enemyType = wavedict[i]['enemytype']
        self.bottomSideBar_header.text = str(enemyType)
        imgSrc= eval(("Enemy."+enemyType +".imagesrc"))
        self.bottomSideBar_image.source = imgSrc
        self.bottomSideBar_image.color = (1,1,1,1)
        self.bottomSideBar_enemyinfo_numEnemies.text = "Number: " + str(wavedict[i]['enemynum'])
        self.bottomSideBar_enemyinfo_enemyHealth.text = "HP: "+ str(int(wavedict[i]['enemyhealth']))
        self.bottomSideBar_enemyinfo_enemySpeed.text = "Speed: "+ str(int(wavedict[i]['enemyspeed']))
        self.bottomSideBar_enemyinfo_enemyArmor.text = "Armor: " + str(int(wavedict[i]['enemyarmor']))
        self.bottomSideBar_enemyinfo_enemyMods.text = "Mods: " + str(wavedict[i]['enemymods'])
        self.bottomSideBar_enemyinfo_enemyReward.text = "Reward: " + str(int(wavedict[i]['enemyreward']))
        self.bottomSideBar_enemyinfo_isBoss.text = "Boss: "+ str(wavedict[i]['isboss'])

        self.bottomSideBar_nextEnemies.text = "Next Enemies: " + wavedict[i+1]['enemytype']+", "+ wavedict[i+2]['enemytype']+", "+ wavedict[i+3]['enemytype']

    def createTBBox(self, squarepos):

        Player.player.tbbox = FloatLayout(size=(150, 150),
                                          pos=(squarepos[0] - Map.squsize * 2, squarepos[1] - Map.squsize * 2))
        Player.player.layout = BoxLayout(size=(Map.squsize * 2, Map.squsize * 2), pos=squarepos)
        Player.player.tbbox.add_widget(Player.player.layout)
        Map.mapvar.background.popUpOpen = Player.player.tbbox


    def towerMenu(self, squarepos):
        self.createTBBox(squarepos)
        range = Player.player.towerSelected.range
        with Player.player.layout.canvas.before:
            Color(.5, .5, .5, .3)
            square = Rectangle(pos = (squarepos[0] - range+Map.squsize, squarepos[1] - range+Map.squsize), size= (2*range, 2*range))
            # Color(0,0,0,1)
            # outline = Line(points=[squarepos[0] - range+Map.squsize, squarepos[1] - range+Map.squsize, squarepos[0] - range+Map.squsize, squarepos[1] + range+Map.squsize,
            #                     squarepos[0] + range + Map.squsize, squarepos[1] + range + Map.squsize, squarepos[0] + range+Map.squsize, squarepos[1] - range+Map.squsize,
            #                     squarepos[0] - range+Map.squsize, squarepos[1] - range+Map.squsize], width=.2)


        tbbuttonnum = len(Localdefs.towerabilitylist)
        radius = 55
        inddeg = (2.0 * math.pi) / tbbuttonnum
        for ind,instance in enumerate(Localdefs.towerabilitylist):
            tmpbtn = ButtonWithImage()
            tmpbtn.instance = instance
            #tmpbtn.text = instance.type
            tmpbtn.size_hint = (.3, .3)
            tmpbtn.size = (20, 20)
            tmpbtn.image.source = instance.imgstr
            Player.player.tbbox.add_widget(tmpbtn)
            tmpbtn.pos = (Player.player.layout.x + radius * math.cos((ind) * inddeg), (Player.player.layout.y - radius * math.sin((ind) * inddeg)))
            #print(Player.player.tbbox.center, Player.player.tbbox.size, squarepos, "name:", tmpbtn.size, tmpbtn.text, tmpbtn.center)
        Map.mapvar.backgroundimg.add_widget(Player.player.tbbox)


    def builderMenu(self,squarepos):
        self.createTBBox(squarepos)
        with Player.player.layout.canvas.before:
            Color(0, 0, 0, 1)
            outline = Line(points=[squarepos[0]-Map.squsize*2, squarepos[1]-Map.squsize*2, squarepos[0]-Map.squsize*2, squarepos[1]+Map.squsize*4,
                                squarepos[0]+ Map.squsize*4, squarepos[1]+ Map.squsize*4, squarepos[0]+Map.squsize*4, squarepos[1]-Map.squsize*2,
                                squarepos[0]-Map.squsize*2, squarepos[1]-Map.squsize*2], width=.2)
            Color(.1, .1, .1, .1)
            rect = Rectangle(size=Player.player.layout.size, pos=Player.player.layout.pos)

        for ind, button in enumerate(Localdefs.iconlist):
            tmpbtn = MyButton()
            tmpbtn.instance = button
            tmpbtn.text=button.type
            tmpbtn.size_hint=(.4, .4)
            tmpbtn.size = (60,60)
            tmpbtn.source = button.imgstr
            Player.player.tbbox.add_widget(tmpbtn)
            tmpbtn.pos = Utilities.get_pos(Player.player.tbbox.pos,180,180, ind)

            #print(Player.player.tbbox.center, Player.player.tbbox.size, touchpos, "name:", tmpbtn.size, tmpbtn.text, tmpbtn.center)


        Map.mapvar.backgroundimg.add_widget(Player.player.tbbox)

gui = GUI()

class EnemyPanel(TabbedPanel):
    #currently instantiating in MAp
    CurrentWave = StringProperty()
    def on_CurrentWave(self, instance, value):
        #here we should update the variables whena  new wave starts (show next wave)
        self.switch_to(self.getDefaultTab())
        wavemod = (1 + (int(self.CurrentWave) / 70.0))
        x=0
        for tab in self.tab_list:
            tab.enemyPanel_numEnemies.text="Number: " + str(int(eval("Enemy." + self.enemytypelist[x] + ".defaultNum") * wavemod))
            tab.enemyPanel_enemyHealth.text="HP: " + str(int(eval("Enemy." + self.enemytypelist[x] + ".health") * wavemod))
            tab.enemyPanel_enemySpeed.text="Speed: " + str(int(eval("Enemy." + self.enemytypelist[x] + ".speed") * wavemod))
            tab.enemyPanel_enemyArmor.text="Armor: " + str(int(eval("Enemy." + self.enemytypelist[x] + ".armor") * wavemod))
            tab.enemyPanel_enemyReward.text="Reward: " + str(int(eval("Enemy." + self.enemytypelist[x] + ".reward") * wavemod))
            x+=1

    def __init__(self,**kwargs):
        super(EnemyPanel,self).__init__(**kwargs)
        self.tab_pos = 'right_top'
        self.tab_height= 40
        self.tab_width=40
        self.size_hint = (1,1)
        self.size = (275,220)
        self.pos = (Window.width - 330, 10)
        self.background_color=[.1,.1,.1,.6]
        self.border = [1,1,1,1]
        self.do_default_tab = False
        self.bind(CurrentWave=self.on_CurrentWave)

        with self.canvas:
            Color(1,1,1,1)
        self.enemytypelist = ['Standard', 'Airborn', 'Splinter', 'Strong', 'Crowd']
        for enemy in self.enemytypelist:
            th = panelHeader(pos=self.pos, size=self.size)
            th.id = enemy
            th.background_normal="enemyimgs/"+enemy+".png"
            th.background_down = "enemyimgs/"+enemy+".png"
            self.add_widget(th)
            th.content = th.createEnemyPanelContent(enemy)

    def getDefaultTab(self, *args):
        enemy = Player.player.waveList[Player.player.wavenum]['enemytype']
        for tab in self.tab_list:
            if tab.id == enemy:
                return tab


class panelHeader(TabbedPanelHeader):
    def __init__(self, **kwargs):
        super(panelHeader,self).__init__(**kwargs)
        self.enemyPanelLayout = StackLayout(size_hint=(1, 1))
        self.add_widget(self.enemyPanelLayout)
        self.enemyPanelLayout.pos = self.pos
        self.enemyPanelLayout.size = self.size

    def createEnemyPanelContent(self,enemy):
        waveNum=Player.player.wavenum
        self.enemyPanel_header = Label(text=str(enemy), width=self.width-30, height= 40, size_hint=(None,None), font_size=24, text_size = (200,40), halign='center')
        self.enemyPanel_enemyinfo = GridLayout(cols=1, col_force_default=True, row_force_default=True,
                                                  row_default_height=30, col_default_width=self.width, size_hint=(None,None))
        self.enemyPanel_numEnemies = Label(text="Number: "+str(int(eval("Enemy."+enemy +".defaultNum") * (1+ (waveNum/70.0)))), font_size=20, text_size = (260, 30))
        self.enemyPanel_enemyHealth = Label(text="HP: "+str(int(eval("Enemy."+enemy +".health") * (1+ (waveNum/70.0)))),font_size=20, text_size = (260, 30))
        self.enemyPanel_enemySpeed = Label(text="Speed: "+str(int(eval("Enemy."+enemy +".speed") * (1+ (waveNum/70.0)))),font_size=20, text_size = (260, 30))
        self.enemyPanel_enemyArmor = Label(text="Armor: "+str(int(eval("Enemy."+enemy +".armor") * (1+ (waveNum/70.0)))),font_size=20, text_size = (260, 30))
        self.enemyPanel_enemyReward = Label(text="Reward: "+str(int(eval("Enemy."+enemy +".reward") * (1+ (waveNum/70.0)))),font_size=20, text_size = (260, 30))
        self.enemyPanel_disclaimer = Label(text="Numbers reflect enemy if sent next wave",font_size=10, text_size = (260, 30))
        self.enemyPanel_enemyinfo.add_widget(self.enemyPanel_numEnemies)
        self.enemyPanel_enemyinfo.add_widget(self.enemyPanel_enemyHealth)
        self.enemyPanel_enemyinfo.add_widget(self.enemyPanel_enemySpeed)
        self.enemyPanel_enemyinfo.add_widget(self.enemyPanel_enemyArmor)
        self.enemyPanel_enemyinfo.add_widget(self.enemyPanel_enemyReward)
        self.enemyPanel_enemyinfo.add_widget(self.enemyPanel_disclaimer)
        self.enemyPanelLayout.add_widget(self.enemyPanel_header)
        self.enemyPanelLayout.add_widget(self.enemyPanel_enemyinfo)


        return self.enemyPanelLayout



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
            element = StringProperty()
            variable = MyLabel(text=str(var))
            variable.id = element
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
