from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.scatterlayout import Scatter
from kivy.uix.anchorlayout import AnchorLayout
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
            Map.mapvar.background.removePopUp()
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
        #print('pressed at {pos}'.format(pos=pos))

class ButtonWithImage(Button, Image):
    pressed = ListProperty()
    def __init__(self, **kwargs):
        super(ButtonWithImage, self).__init__(**kwargs)
        self.image = Image(text = " ")
        self.image.pos_hint=(None,None)
        self.add_widget(self.image)
        self.image.size = self.size
        self.image.pos = self.pos
        self.bind(pos=self.on_pos)
        self.label = Label(text=' ', size_hint=(None,None), pos = self.pos,color=[1,1,1,1], halign='center')
        self.add_widget(self.label)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.pressed = touch.pos
            if self.id == 'enemyinfo' or self.id =='rotate':
                pass
            else:
                Map.mapvar.background.removePopUp()
            return True

    def on_pressed(self, button, pos):
        if button.disabled == False:
            if button.id == 'unpause':
                MainFunctions.pauseGame(button)
                return
            elif button.id == 'enemyinfo':
                gui.toggleEnemyPanel()
            #tower abilities like upgrade and sell
            elif button.instance  in Localdefs.towerabilitylist:
                func = "TowerAbilities."+button.instance.type +"."+ button.instance.func + "()"
                eval(func)
                if button.id == 'rotate':
                    gui.removeTriangle()
                    gui.drawTriangle()
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

        self.layout = GridLayout(rows=2, size=(500,400))
        self.layout.center = ((Map.mapvar.scrwid-self.width)/2,(Map.mapvar.scrhei-self.height)/2)
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
            Rectangle(size = (Map.mapvar.scrwid, Map.mapvar.scrhei), pos=(0,0))
        self.configLayout = GridLayout(cols=2)
        self.buttonLayout = GridLayout(cols=2)
        self.gameplayButtons = BoxLayout(orientation = 'vertical',spacing = 10, padding = 20)
        self.startButton = Button(text='Play/Resume', id = 'Play')
        self.restartButton = Button(text='Restart', id='Restart')
        self.gameplayButtons.add_widget(self.startButton)
        self.gameplayButtons.add_widget(self.restartButton)
        self.pathLayout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.pathLabel = Label(text = "# Enemy Paths:")
        self.onePath = ToggleButton(text = 'One', id='onepath', group='path', state='down')
        self.twoPath = ToggleButton(text = 'Two', id='twopath',group='path')
        self.threePath = ToggleButton(text = 'Three', id='threepath',group='path')
        self.pathLayout.add_widget(self.pathLabel)
        self.pathLayout.add_widget(self.onePath)
        self.pathLayout.add_widget(self.twoPath)
        self.pathLayout.add_widget(self.threePath)
        self.difficultyLayout = BoxLayout(orientation='vertical',spacing=10, padding=10)
        self.difficultyLabel = Label(text="Enemy Difficulty:")
        self.easy = ToggleButton(text='Easy', id='easy',group='difficulty', state='down')
        self.medium = ToggleButton(text='Medium', id='medium',group='difficulty')
        self.hard = ToggleButton(text='Hard', id='hard',group='difficulty')
        self.difficultyLayout.add_widget(self.difficultyLabel)
        self.difficultyLayout.add_widget(self.easy)
        self.difficultyLayout.add_widget(self.medium)
        self.difficultyLayout.add_widget(self.hard)


        self.buttonLayout.add_widget(self.gameplayButtons)
        self.configLayout.add_widget(self.pathLayout)
        self.configLayout.add_widget(self.difficultyLayout)
        self.buttonLayout.add_widget(self.configLayout)
        self.layout.add_widget(self.buttonLayout)

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
        self.topBar = None

    def bindings(self, *args):
        if self.topBar:
            self.topBar.pos=(0,Window.height-45)
            self.topBar.layout.pos = self.topBar.pos
            self.topBar.size = (Window.width,45)
            self.topBar.layout.size = self.topBar.size
        self.rightSideButtons_layout.pos = (Window.width-55, 2*Map.mapvar.squsize)

    def rightSideButtons(self):
        self.rightSideButtons_layout=StackLayout(size_hint=(None,None), size=(50,70), pos=(Window.width-55, 2*Map.mapvar.squsize))
        self.enemyInfoButton = ButtonWithImage(text=" ",id='enemyinfo', size_hint=(None,None), width=50, height=50)
        self.enemyInfoButton.image.source = "enemyimgs/Standard.png"
        self.enemyInfoButton.label.text = 'Info'
        self.enemyInfoButton.label.size = (50,20)
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

    def createTBBox(self, squarepos, squwid, squhei):
        Player.player.tbbox = Scatter(size=(Map.mapvar.squsize*squwid,Map.mapvar.squsize*squhei), pos=(squarepos[0]+2*Map.mapvar.squsize,squarepos[1]-Map.mapvar.squsize*2), do_resize=False, do_rotation=False)
        Player.player.layout = GridLayout(size_hint=(None,None), size=Player.player.tbbox.size, pos=(0,0), cols=2)
        with Player.player.tbbox.canvas:
            Color(.1,.1,.1,.9)
            Rectangle(pos=(0,0), size=Player.player.tbbox.size)
        #print Player.player.layout.size, Player.player.layout.pos, Player.player.tbbox.size, Player.player.tbbox.pos
        Player.player.tbbox.add_widget(Player.player.layout)
        Map.mapvar.background.popUpOpen = Player.player.tbbox

    def towerMenu(self, squarepos):
        self.createTBBox(squarepos,6,6)
        range = Player.player.towerSelected.range
        #Player.player.tbbox.pos = (Player.player.tbbox.pos[0]+range, Player.player.tbbox.pos[1])
        with Map.mapvar.backgroundimg.canvas:
            Color(0,0,0,1)
            Map.mapvar.towerRange = Line(points=[squarepos[0] - range+Map.mapvar.squsize, squarepos[1] - range+Map.mapvar.squsize, squarepos[0] - range+Map.mapvar.squsize, squarepos[1] + range+Map.mapvar.squsize,
                                   squarepos[0] + range+Map.mapvar.squsize, squarepos[1] + range+Map.mapvar.squsize, squarepos[0] + range+Map.mapvar.squsize, squarepos[1] - range+Map.mapvar.squsize,
                                   squarepos[0] - range+Map.mapvar.squsize, squarepos[1] - range+Map.mapvar.squsize], width=.2)
        Player.player.layout.cols=1
        #sell button
        self.sellbtn = ButtonWithImage(text=' ', size_hint=(1, None), pos_hint = (1,1),height=40)
        self.sellbtn.instance = Localdefs.towerabilitylist[0]
        self.sellbtn.image.source = self.sellbtn.instance.imgstr
        self.sellbtn.image.size_hint = (None, None)
        self.sellbtn.image.size = (30, 30)
        self.sellbtn.image.pos = self.sellbtn.pos
        self.sellbtn.text = '              '+self.sellbtn.instance.type + ':  $' + str(int(Player.player.towerSelected.refund))
        Player.player.layout.add_widget(self.sellbtn)

        self.sellbtn.x = Player.player.tbbox.x
        #upgrade data grid
        dataLayout = GridLayout(size=(Map.mapvar.squsize*4,Map.mapvar.squsize*4), pos=(0,0), cols=3)
        headers = [' ', 'Current', 'Next']
        for h in headers:
            lbl = Label(text=str(h))
            dataLayout.add_widget(lbl)
        for item in Player.player.towerSelected.upgradeData:
            lbl = Label(text=str(item))
            dataLayout.add_widget(lbl)
        Player.player.layout.add_widget(dataLayout)
        #upgrade button
        self.upgbtn = ButtonWithImage(text=' ', size_hint=(1, None), height=40)
        self.upgbtn.instance = Localdefs.towerabilitylist[1]
        self.upgbtn.text = '              '+self.upgbtn.instance.type + ':  $'+ str(Player.player.towerSelected.upgradeDict['Cost'][Player.player.towerSelected.level-1])
        self.upgbtn.image.source = self.upgbtn.instance.imgstr
        Player.player.layout.add_widget(self.upgbtn)
        self.toggleUpgBtn()
        if Player.player.towerSelected.percentComplete > 0:
            self.disableBtn(self.upgbtn)
            self.disableBtn(self.sellbtn)

        if Player.player.towerSelected.type == 'Wind':
            self.rotatebtn = ButtonWithImage(text=' ', size_hint=(1, None), height=40)
            self.rotatebtn.id = 'rotate'
            self.rotatebtn.instance = Localdefs.towerabilitylist[2]
            self.rotatebtn.text = '              '+self.rotatebtn.instance.type+" Group"
            self.rotatebtn.image.source = self.rotatebtn.instance.imgstr
            Player.player.tbbox.size =  (Map.mapvar.squsize * 6, Map.mapvar.squsize * 7)
            Player.player.layout.height = Player.player.tbbox.height
            Player.player.layout.add_widget(self.rotatebtn)
            with Player.player.tbbox.canvas.before:
                Color(.1, .1, .1, .9)
                Rectangle(pos=(0, 0), size=Player.player.tbbox.size)
            self.drawTriangle()

        Map.mapvar.backgroundimg.add_widget(Player.player.tbbox)

    def drawTriangle(self):
        with Map.mapvar.backgroundimg.canvas:
            Color(0, 0, 0, 1)
            if Player.player.towerSelected.towerGroup.facing == 'l':
                Map.mapvar.triangle = self.getTriangle('l')
            elif Player.player.towerSelected.towerGroup.facing == 'r':
                Map.mapvar.triangle = self.getTriangle('r')
            elif Player.player.towerSelected.towerGroup.facing == 'u':
                Map.mapvar.triangle = self.getTriangle('u')
            elif Player.player.towerSelected.towerGroup.facing == 'd':
                Map.mapvar.triangle = self.getTriangle('d')

    def removeTriangle(self):
        if Map.mapvar.triangle:
            Map.mapvar.backgroundimg.canvas.remove(Map.mapvar.triangle)
            Map.mapvar.triangle = None

    def getTriangle(self, dir):
        # triangles for display around a tower indicating its direction
        if dir == 'l':
            return Triangle(points=(Player.player.towerSelected.pos[0] - Map.mapvar.squsize / 6,
                                            Player.player.towerSelected.pos[1] + Map.mapvar.squsize / 6,
                                            Player.player.towerSelected.pos[0] - Map.mapvar.squsize,
                                            Player.player.towerSelected.pos[1] + Map.mapvar.squsize,
                                            Player.player.towerSelected.pos[0] - Map.mapvar.squsize / 6,
                                            Player.player.towerSelected.top - Map.mapvar.squsize / 6))
        if dir == 'r':
            return Triangle(points=(Player.player.towerSelected.right + Map.mapvar.squsize / 6,
                                         Player.player.towerSelected.pos[1] + Map.mapvar.squsize / 6,
                                         Player.player.towerSelected.right + Map.mapvar.squsize,
                                         Player.player.towerSelected.pos[1] + Map.mapvar.squsize,
                                         Player.player.towerSelected.right + Map.mapvar.squsize / 6,
                                         Player.player.towerSelected.top - Map.mapvar.squsize / 6))
        if dir == 'u':
            return Triangle(points=(Player.player.towerSelected.pos[0] + Map.mapvar.squsize / 6,
                                      Player.player.towerSelected.top + Map.mapvar.squsize / 6,
                                      Player.player.towerSelected.pos[0] + Map.mapvar.squsize,
                                      Player.player.towerSelected.top + Map.mapvar.squsize,
                                      Player.player.towerSelected.right - Map.mapvar.squsize / 6,
                                      Player.player.towerSelected.top + Map.mapvar.squsize / 6))
        if dir == 'd':
            return Triangle(points=(Player.player.towerSelected.pos[0] + Map.mapvar.squsize / 6,
                                        Player.player.towerSelected.pos[1] - Map.mapvar.squsize / 6,
                                        Player.player.towerSelected.pos[0] + Map.mapvar.squsize,
                                        Player.player.towerSelected.pos[1] - Map.mapvar.squsize,
                                        Player.player.towerSelected.right - Map.mapvar.squsize / 6,
                                        Player.player.towerSelected.pos[1] - Map.mapvar.squsize / 6))

    def toggleUpgBtn(self):
        if Player.player.towerSelected and Player.player.money < Player.player.towerSelected.upgradeDict['Cost'][Player.player.towerSelected.level - 1]:
            self.disableBtn(self.upgbtn)
        else:
            self.enableBtn(self.upgbtn)
    def disableBtn(self, btn):
        btn.disabled = True
    def enableBtn(self,btn):
        btn.disabled = False

    def builderMenu(self,squarepos):
        self.createTBBox(squarepos,4,6)

        for button in Localdefs.iconlist:
            tmpbtn = ButtonWithImage(text=' ',size_hint=(None, None), size=(60,60))
            tmpbtn.instance = button
            tmpbtn.image.source = button.imgstr
            tmpbtn.label.text = " $"+str(button.cost)
            tmpbtn.label.size = (30,18)
            if button.cost > Player.player.money:
                tmpbtn.disabled = True
            Player.player.layout.add_widget(tmpbtn)
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
