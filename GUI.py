from kivy.animation import Animation
from kivy.core.window import Window
from kivy.graphics import *
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.scatterlayout import Scatter
from kivy.uix.scrollview import ScrollView
from kivy.uix.stacklayout import StackLayout
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelHeader
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.widget import Widget
from kivy.properties import ListProperty, StringProperty
from kivy.uix.checkbox import CheckBox

import EventDispatcher
import EventFunctions
import Localdefs
import MainFunctions
import Map
import Player
import Utilities
import Enemy
import main
import TowerAbilities
import GUI_Base
import GUI_Templates


class pauseMenu(GUI_Base.SmartMenu):
    # setup the menu button names

    def __init__(self, **kwargs):
        super(pauseMenu, self).__init__(**kwargs)
        self.unpause = Button()
        self.unpause.size_hint = (None, None)
        self.unpause.size = (main.Window.width, main.Window.height)
        self.unpause.pos = (0, 0)
        self.unpause.id = 'unpause'
        # self.unpause.bind(on_release = MainFunctions.pauseGame)
        self.image = Utilities.imgLoad('backgroundimgs/play.png')
        self.image.size = (Map.mapvar.squsize*2, Map.mapvar.squsize*2)
        self.image.pos=(self.unpause.center[0]-.5*self.width, self.unpause.center[1]-.5*self.height)
        self.unpause.add_widget(self.image)
        self.unpause.background_color = [.2, .2, .2, .2]
        self.add_widget(self.unpause)
        # with self.unpause.canvas.before:
        #   Color(.2,.2,.2,.1)
        #   Rectangle(size = self.unpause.size, pos=self.unpause.pos)


class mainMenu(GUI_Base.SmartMenu):
    # setup the menu button names
    def __init__(self, **kwargs):
        super(mainMenu, self).__init__(**kwargs)

        self.layout = GridLayout(rows=4,size=(main.Window.width-3*Map.mapvar.squsize,main.Window.height-3*Map.mapvar.squsize),
                                 padding=[Map.mapvar.squsize/2], spacing=Map.mapvar.squsize)
        self.layout.center = ((main.Window.width / 2), (main.Window.height/ 2))
        self.id = 'mainmenu'
        self.add_widget(self.layout)

        # use pos_hint to set the position relative to its parent by percentage.
        self.menulabel = Label(text='Tablet Tower Defense', size_hint = (1,.3))
        self.layout.add_widget(self.menulabel)
        self.menulabel.font_size = Window.width * 0.04

        with self.layout.canvas.before:
            Color(.3, .3, .3)
            self.menurect = Rectangle(size=self.layout.size, pos=self.layout.pos)
        self.configLayout = GridLayout(cols=3)
        self.buttonLayout = GridLayout(cols=2)
        self.gameplayButtons = BoxLayout(orientation='vertical', spacing=10, padding=20)
        self.startButton = Button(text='Play', id='Play')
        self.gameplayButtons.add_widget(self.startButton)
        self.restartButton = Button(text='Restart', id='Restart')
        self.gameplayButtons.add_widget(self.restartButton)
        self.quitButton = Button(text='Quit', id='Quit')
        self.gameplayButtons.add_widget(self.quitButton)
        self.pathLayout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.pathLabel = Label(text="# Paths:")
        self.onePath = ToggleButton(text='One', id='onepath', group='path', state='down')
        self.twoPath = ToggleButton(text='Two', id='twopath', group='path')
        self.threePath = ToggleButton(text='Three', id='threepath', group='path')
        self.pathLayout.add_widget(self.pathLabel)
        self.pathLayout.add_widget(self.onePath)
        self.pathLayout.add_widget(self.twoPath)
        self.pathLayout.add_widget(self.threePath)
        self.difficultyLayout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.difficultyLabel = Label(text="Difficulty:")
        self.easy = ToggleButton(text='Easy', id='easy', group='difficulty', state='down')
        self.medium = ToggleButton(text='Med', id='medium', group='difficulty')
        self.hard = ToggleButton(text='Hard', id='hard', group='difficulty')
        self.difficultyLayout.add_widget(self.difficultyLabel)
        self.difficultyLayout.add_widget(self.easy)
        self.difficultyLayout.add_widget(self.medium)
        self.difficultyLayout.add_widget(self.hard)
        self.enemyOrderLayout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.enemyOrderLabel = Label(text="Order:", size_hint=(1,.6))
        self.standardOrder = ToggleButton(text='Standard', id='standard', group='order', state='down')
        self.randomOrder = ToggleButton(text='Random', id='random', group='order')
        self.enemyOrderLayout.add_widget(self.enemyOrderLabel)
        self.enemyOrderLayout.add_widget(self.standardOrder)
        self.enemyOrderLayout.add_widget(self.randomOrder)
        self.buttonLayout.add_widget(self.gameplayButtons)
        self.configLayout.add_widget(self.pathLayout)
        self.configLayout.add_widget(self.difficultyLayout)
        self.configLayout.add_widget(self.enemyOrderLayout)
        self.buttonLayout.add_widget(self.configLayout)
        self.layout.add_widget(self.buttonLayout)
        #Audio settings
        self.settingsLayout = StackLayout(orientation = 'lr-tb', size_hint = (1,.05))
        self.soundCheckBox = GUI_Base.MyCheckBox(size_hint = (.15,1))
        self.soundCheckBox.label.text = "Play Sound: "
        self.soundCheckBox.checkbox.id = 'sound'
        self.soundCheckBox.checkbox.active = True if Player.player.soundOn else False
        self.musicCheckBox = GUI_Base.MyCheckBox(size_hint = (.15,1))
        self.musicCheckBox.label.text = "Play Music: "
        self.musicCheckBox.checkbox.id = 'music'
        self.musicCheckBox.checkbox.active = True if Player.player.musicOn else False
        self.settingsLayout.add_widget(self.soundCheckBox)
        self.settingsLayout.add_widget(self.musicCheckBox)
        self.soundCheckBox.checkbox.bind(active= Player.player.sound.on_sound)
        self.musicCheckBox.checkbox.bind(active= Player.player.sound.on_music)
        self.layout.add_widget(self.settingsLayout)


        self.footerlayout = GridLayout(orientation= 'vertical', rows = 2, size_hint = (1,.15))
        self.footerInfo = Label(text='On the web at tablettowerdefense.com and Twitter: @Tablettowerdef.  Property of Scott Rossignol.', font_size = main.Window.size[0]*.01)
        self.footerDisc = Label(
            text='Thanks to EmojiOne for providing free emoji icons: https://www.emojione.com. This game runs on the Kivy framework.', font_size = main.Window.size[0]*.01)
        self.footerlayout.add_widget(self.footerInfo)
        self.footerlayout.add_widget(self.footerDisc)
        self.layout.add_widget(self.footerlayout)

    def bindings(self):
        Map.mapvar.scrwid, Map.mapvar.scrhei = main.Window.size
        self.layout.center = ((Map.mapvar.scrwid / 2), (Map.mapvar.scrhei / 2))
        self.menurect.pos = self.layout.pos

class GUI():
    def on_totalCost(self, instance, value):
        cost = int(self.myDispatcher.totalCost)
        if cost > Player.player.money:
            self.total_cost.color = (1,0,0,1)
        else:
            self.total_cost.color = (0,1,0,1)
        self.total_cost.text = "$" + str(cost)

    def __init__(self):

        self.topBar_Boxlist = []
        self.myDispatcher = EventDispatcher.EventDisp()
        self.topBar = self.createTopBar()
        self.rightSideButtons_layout = None
        self.bgrect = None
        self.messageCounter = None
        self.towerMenuHeaders = [' ', 'Curr', 'Group+', 'Nxt']

    def bindings(self, *args):
        if self.topBar:
            self.topBar.pos = (0, Window.height - Map.mapvar.squsize*2)
            self.topBar.layout.pos = self.topBar.pos
            self.topBar.size = (Window.width, Map.mapvar.squsize*1.5)
            self.topBar.layout.size = self.topBar.size
        if self.rightSideButtons_layout:
            self.rightSideButtons_layout.pos = (Window.width - 55, 2 * Map.mapvar.squsize)

    def rightSideButtons(self):
        self.rightSideButtons_layout = StackLayout(size_hint=(None, None), size=(55, 120),
                                                   pos=(Window.width - 2*Map.mapvar.squsize, 4 * Map.mapvar.squsize), spacing = [0,20])
        self.enemyInfoButton = GUI_Base.ButtonWithImage(text=" ", id='enemyinfo', size_hint=(None, None), width=50, height=50)
        self.enemyInfoButton.image.source = "enemyimgs/Standard_r.png"
        self.enemyInfoButton.label.text = 'Info'
        self.enemyInfoButton.label.size = (50, 20)
        self.rightSideButtons_layout.add_widget(self.enemyInfoButton)
        self.enemyInfoButton.image.pos = self.enemyInfoButton.pos
        self.enemyInfoButton.label.pos = self.enemyInfoButton.pos

        self.towerInfoButton = GUI_Base.ButtonWithImage(text=" ", id='towerinfo', size_hint=(None, None), width=50,
                                                        height=50)
        self.towerInfoButton.image.source = "towerimgs/0.png"
        self.towerInfoButton.label.text = 'Info'
        self.towerInfoButton.label.size = (50, 20)
        self.rightSideButtons_layout.add_widget(self.towerInfoButton)
        self.towerInfoButton.image.pos = self.towerInfoButton.pos
        self.towerInfoButton.label.pos = self.towerInfoButton.pos

        return self.rightSideButtons_layout

    def toggleEnemyPanel(self):
        if not Map.mapvar.enemypanel.parent:
            Map.mapvar.backgroundimg.add_widget(Map.mapvar.enemypanel)
            Map.mapvar.enemypanel.switch_to(Map.mapvar.enemypanel.getDefaultTab())
            Map.mapvar.background.popUpOpen = Map.mapvar.enemypanel
        else:
            Map.mapvar.backgroundimg.remove_widget(Map.mapvar.enemypanel)

    def toggleTowerPanel(self):
        if not Map.mapvar.towerpanel.parent:
            Map.mapvar.backgroundimg.add_widget(Map.mapvar.towerpanel)
            Map.mapvar.towerpanel.switch_to(Map.mapvar.towerpanel.getDefaultTab())
            Map.mapvar.background.popUpOpen = Map.mapvar.towerpanel
        else:
            Map.mapvar.backgroundimg.remove_widget(Map.mapvar.towerpanel)

    def createTopBar(self):
        self.topBar = GUI_Templates.Bar(pos_hint = (None,None), size_hint=(None,None), pos=(0, Window.height - Map.mapvar.squsize*2), size=(Window.width, Map.mapvar.squsize*1.5))
        self.menuButton = Button(text='Menu', id='menu', size_hint=(None, None),
                                 width=Map.mapvar.squsize * 2.5, height=Map.mapvar.squsize * 2,
                                 font_size=main.Window.size[0] * .02)

        self.pauseButton = Button(text='Pause', id='pause', size_hint=(None, None),
                                  width=Map.mapvar.squsize * 2.5, height=Map.mapvar.squsize * 2,
                                  font_size=main.Window.size[0] * .018)
        self.nextwaveButton = Button(text='Start', id='next', size_hint=(None, None), width=Map.mapvar.squsize * 3.5,
                                     height=Map.mapvar.squsize * 2, font_size=main.Window.size[0] * .024)
        self.nextwaveButton.bind(on_release=self.nextWave)
        self.nextwaveButton.valign = 'top'
        self.topBar.layout.add_widget(self.menuButton)
        self.topBar.layout.add_widget(self.pauseButton)
        self.topBar.layout.add_widget(self.nextwaveButton)
        self.topBar.layout.padding = [5]
        return self.topBar

    def initTopBar(self):
        self.menuButton.bind(on_release=MainFunctions.pauseGame)
        self.pauseButton.bind(on_release=MainFunctions.pauseGame)
        for label, var, source, icon in Localdefs.topBar_ElementList:
            GUI_Templates.topBarWidget(label, var, source, icon)
        Map.mapvar.backgroundimg.add_widget(self.topBar)

    def toggleButtons(self, active = True):
        list = [self.menuButton, self.pauseButton, self.nextwaveButton, self.enemyInfoButton]
        if active:
            for button in list:
                button.disabled = False
        else:
            for button in list:
                button.disabled = True

    def nextWave(self, *args):
        self.waveAnimation.stop(self.waveScroller)
        EventFunctions.nextWave()

    def createWaveStreamer(self):
        self.waveStreamerLayout = StackLayout(orientation='lr-tb',
                                              pos=(Window.width - 12*Map.mapvar.squsize, Map.mapvar.playhei+5),
                                              size=(13 * Map.mapvar.squsize, Map.mapvar.squsize))
        self.waveStreamerLabel = Label(text="Next Waves:", size_hint=(None, 1), width = Map.mapvar.squsize*3,
                                    color=[0, 0, 0, 1], font_size = main.Window.size[0]*.0125)
        self.waveStreamerLayout.add_widget(self.waveStreamerLabel)
        self.waveStreamerEnemyLayout = GridLayout(rows=1, size_hint=(None, 1),
                                                  size=(18 * Map.mapvar.squsize, Map.mapvar.squsize))
        x = 0
        for wave in Player.player.waveTypeList:
            lbl = Label(size_hint=(None, None), text=wave[0], id='wave' + str(x), text_size=(None, None),
                        size=(Map.mapvar.squsize * 2.25, Map.mapvar.squsize), color=[0, 0, 0, 1], font_size = main.Window.size[0]*.0125)
            x += 1
            if wave[1]:  # if boss
                lbl.bold = True
                lbl.color = [1, 0, 0, 1]
            self.waveStreamerEnemyLayout.add_widget(lbl)

        self.waveScroller = ScrollView(do_scroll_y=False, scroll_x=0, size_hint=(None, 1), width=Map.mapvar.squsize * 9,
                                       bar_color=[1, 1, 1, 0], bar_inactive_color=[1, 1, 1, 0])
        self.waveScroller.add_widget(self.waveStreamerEnemyLayout)
        self.waveStreamerLayout.add_widget(self.waveScroller)
        self.topBar.add_widget(self.waveStreamerLayout)
        self.waveAnimation = Animation(scroll_x=.25, duration=20.0)
        self.waveAnimation.bind(on_complete=EventFunctions.updateAnim)
        self.catchUpWaveAnimation = None

    def resetWaveStreamer(self):
        self.waveStreamerEnemyLayout.clear_widgets()
        x = 0
        for wave in Player.player.waveTypeList:
            lbl = Label(size_hint=(None, None), text=wave[0], id='wave' + str(x), text_size=(None, None),
                        size=(Map.mapvar.squsize * 2.3, Map.mapvar.squsize), color=[0, 0, 0, 1], font_size = main.Window.size[0]*.0125)
            x += 1
            if wave[1]:  # if boss
                lbl.bold = True
                lbl.color = [1, 0, 0, 1]
            self.waveStreamerEnemyLayout.add_widget(lbl)
        self.waveScroller.scroll_x = 0


    def removeWaveStreamer(self):
        self.waveStreamerEnemyLayout.clear_widgets()

    def createAlertStreamer(self):
        self.alertQueue = []
        self.alertStreamerLayout = BoxLayout(orientation='horizontal', pos=(5, 5),
                                             size=(Map.mapvar.scrwid - 10, Map.mapvar.squsize * 2 - Map.mapvar.squsize/3))
        self.alertScroller = ScrollView(do_scroll_y=False, scroll_x=1, size_hint=(None, 1),
                                        width=Map.mapvar.scrwid - 10, bar_color=[1, 1, 1, 0],
                                        bar_inactive_color=[1, 1, 1, 0])
        self.alertLayout = GridLayout(rows=1, size_hint=(None, 1), width=Map.mapvar.scrwid*2)
        self.alertLabel = Label(text='', color=[0, 0, 0, 1], size_hint=(1, None),
                                font_size=main.Window.size[0] * .05,
                                height=Map.mapvar.squsize * 2 - 10)
        self.alertLayout.add_widget((self.alertLabel))
        self.alertScroller.add_widget(self.alertLayout)
        self.alertStreamerLayout.add_widget(self.alertScroller)
        self.alertAnimation = Animation(scroll_x=0, duration=6.0)
        self.alertAnimation.bind(on_complete=self.removeAlert)
        return self.alertStreamerLayout
    def alertStreamerBinding(self):
        self.alertStreamerLayout.size = (Map.mapvar.scrwid - 10, Map.mapvar.squsize * 2-Map.mapvar.squsize/3)
        self.alertScroller.width = Map.mapvar.scrwid - 10
        self.alertLayout.width = Map.mapvar.scrwid*2
        self.alertLabel.height = Map.mapvar.squsize*2-10
        self.alertLabel.font_size = main.Window.size[0] * .025

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
        if level == 'repeat':
            self.alertLabel.color = [0, 0, 0, 1]
            self.alertAnimation.unbind(on_complete=self.removeAlert)
            self.alertAnimation.bind(on_complete=self.repeatAlert)
        if level == 'warning':
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
            self.messageLayout.pos = (Map.mapvar.scrwid / 2 - (self.messageLayout.size[0] / 2), Map.mapvar.scrhei / 1.5)
            self.messageLabel = Label(text=msg, color=[.7, 0, 0, 1], size_hint=(None, None), font_size=main.Window.size[0]*.03)
            self.messageLayout.add_widget(self.messageLabel)
            Map.mapvar.backgroundimg.add_widget(self.messageLayout)

    def removeMessage(self):
        self.messageLabel.text = ' '
        self.messageLayout.remove_widget(self.messageLabel)
        Map.mapvar.backgroundimg.remove_widget(self.messageLayout)
        self.messageCounter = None

    def createTBBox(self, squarepos, squwid, squhei):
        Player.player.tbbox = Scatter(size=(Map.mapvar.squsize * squwid, Map.mapvar.squsize * squhei), pos=(
        squarepos[0] + 2 * Map.mapvar.squsize, squarepos[1] + Map.mapvar.squsize - Map.mapvar.squsize * squhei/2), do_resize=False,
                                      do_rotation=False)
        if Player.player.tbbox.right > Map.mapvar.scrwid - Map.mapvar.squsize:
            Player.player.tbbox.set_right(squarepos[0])
        if Player.player.tbbox.top > Map.mapvar.playhei:
            Player.player.tbbox.top = Map.mapvar.playhei

        Player.player.layout = GridLayout(size_hint=(None, None), size=Player.player.tbbox.size, pos=(0, 0), cols=2)
        with Player.player.tbbox.canvas.before:
            Color(.1, .1, .1, .9)
            self.tbBoxRect = Rectangle(pos=(0, 0), size=Player.player.tbbox.size)
        # print Player.player.layout.size, Player.player.layout.pos, Player.player.tbbox.size, Player.player.tbbox.pos
        Player.player.tbbox.add_widget(Player.player.layout)
        Map.mapvar.background.popUpOpen = Player.player.tbbox

    def towerMenu(self, squarepos):
        self.createTBBox(squarepos, 7, 7)
        range = Player.player.towerSelected.range
        with Map.mapvar.backgroundimg.canvas:
            Color(0, 0, 0, 1)
            leftx = (squarepos[0] - range + Map.mapvar.squsize if squarepos[0] - range + Map.mapvar.squsize > Map.mapvar.border else Map.mapvar.border)
            rightx = (squarepos[0] + range + Map.mapvar.squsize if squarepos[0] + range + Map.mapvar.squsize < Map.mapvar.playwid else Map.mapvar.playwid)
            bottomy = (squarepos[1] - range + Map.mapvar.squsize if squarepos[1] - range + Map.mapvar.squsize > Map.mapvar.border else Map.mapvar.border)
            topy = (squarepos[1] + range + Map.mapvar.squsize if squarepos[1] + range + Map.mapvar.squsize < Map.mapvar.playhei else Map.mapvar.playhei)
            Map.mapvar.towerRange = Line(
                points=[leftx,bottomy,leftx,topy,rightx,topy,rightx,bottomy,leftx,bottomy], width=.5)
        Player.player.layout.cols = 1
        # sell button
        self.sellbtn = GUI_Base.ButtonWithImage(text=' ', size_hint=(1, None), pos_hint=(1, 1), height=40,id = 'Sell',font_size = main.Window.size[0]*.013)
        self.sellbtn.group = None
        self.sellbtn.instance = Localdefs.towerabilitylist[0]
        self.sellbtn.instance.cost = int(Player.player.towerSelected.refund)
        self.sellbtn.image.source = self.sellbtn.instance.imgstr
        self.sellbtn.image.size_hint = (None, None)
        self.sellbtn.image.size = (Map.mapvar.squsize, Map.mapvar.squsize)
        self.sellbtn.image.pos = self.sellbtn.pos
        self.sellbtn.text = self.sellbtn.instance.type + ':  $' + str(
            self.sellbtn.instance.cost)
        Player.player.layout.add_widget(self.sellbtn)
        self.sellbtn.x = Player.player.tbbox.x

        # upgrade data grid
        dataLayout = GridLayout(size=(Map.mapvar.squsize * 6, Map.mapvar.squsize * 5), pos=(0, 0), cols=4)
        for h in self.towerMenuHeaders:
            lbl = Label(text=str(h), text_size = (None,None), font_size = main.Window.size[0]*.013)
            dataLayout.add_widget(lbl)
        for item in Player.player.towerSelected.upgradeData:
            lbl = Label(text=str(item), text_size = (None,None), font_size = main.Window.size[0]*.013)
            dataLayout.add_widget(lbl)
        Player.player.layout.add_widget(dataLayout)
        # upgrade button
        if Player.player.towerSelected.level != Player.player.upgPathSelectLvl:
            self.upgbtn = GUI_Base.ButtonWithImage(text=' ', size_hint=(1, None), height=40, id='Upgrade', font_size = main.Window.size[0]*.013)
            self.upgbtn.instance = Localdefs.towerabilitylist[1]
            self.upgbtn.instance.cost = Player.player.towerSelected.upgradeDict['Cost'][Player.player.towerSelected.level - 1]
            self.upgbtn.group = 'Enableable'
            self.upgbtn.text = self.upgbtn.instance.type + ':  $' + str(self.upgbtn.instance.cost)
            self.upgbtn.image.source = self.upgbtn.instance.imgstr
            Player.player.layout.add_widget(self.upgbtn)
            self.toggleUpgBtn()
            if Player.player.towerSelected.percentComplete > 0:
                self.disableBtn(self.upgbtn)
                self.disableBtn(self.sellbtn)
        else:
            upgradeLayout = StackLayout(size_hint=(1,None), height = 40)
            self.upgbtn1 = GUI_Base.StackButtonWithImage(text=' ', size_hint=(.5, None), height=40, id='LeaderPath',
                                                   font_size=main.Window.size[0] * .01)
            self.upgbtn1.instance = Localdefs.towerabilitylist[1]
            self.upgbtn1.instance.cost = Player.player.towerSelected.upgradeDict['Cost'][
                Player.player.towerSelected.level - 1]
            self.upgbtn1.group = 'Enableable'
            self.upgbtn1.layoutLbl.text = 'Leader Path  $' + str(self.upgbtn1.instance.cost[0]) \
                               +" + "+ str(self.upgbtn1.instance.cost[1]) + " Gems"
            self.upgbtn1.layoutImg.source = "iconimgs/reddiamond.png"
            upgradeLayout.add_widget(self.upgbtn1)
            self.upgbtn1.layoutImg.size = (30,40)
            self.upgbtn1.layoutLbl.size = (self.upgbtn1.width*.8, self.upgbtn1.height)
            self.upgbtn1.layoutLbl.halign = 'center'

            self.upgbtn2 = GUI_Base.StackButtonWithImage(text=' ', size_hint=(.5, None), height=40, id='DamagePath',
                                                    font_size=main.Window.size[0] * .01)
            self.upgbtn2.instance = Localdefs.towerabilitylist[1]
            self.upgbtn2.instance.cost = Player.player.towerSelected.upgradeDict['Cost'][
                Player.player.towerSelected.level - 1]
            self.upgbtn2.group = 'Enableable'
            self.upgbtn2.layoutLbl.text = 'Damage Path  $' + str(self.upgbtn2.instance.cost[0]) \
                               + " + " +str(int(self.upgbtn2.instance.cost[1])) + " Gems"
            self.upgbtn2.layoutImg.source = "iconimgs/reddiamond.png"
            upgradeLayout.add_widget(self.upgbtn2)
            self.upgbtn2.layoutImg.size = (30, 40)
            self.upgbtn2.layoutLbl.size = (self.upgbtn1.width * .8, self.upgbtn1.height)
            self.upgbtn2.layoutLbl.halign = 'center'
            Player.player.layout.add_widget(upgradeLayout)
            self.toggleUpgBtn()
            if Player.player.towerSelected.percentComplete > 0:
                self.disableBtn(self.upgbtn1)
                self.disableBtn(self.upgbtn2)
                self.disableBtn(self.sellbtn)
            self.upginfobtn = GUI_Base.ButtonWithImage(text='', size_hint=(1, None), height = 40, id='towerinfo',
                                                       font_size=main.Window.size[0] * .013)
            self.upginfobtn.text = "Upgrade Info"
            self.upginfobtn.image.source = "iconimgs/info.png"
            Player.player.layout.add_widget(self.upginfobtn)

        if Player.player.towerSelected.type == 'Wind':
            self.rotatebtn = GUI_Base.ButtonWithImage(text=' ', size_hint=(1, None), height=40, id='Rotate', group = 'None', font_size = main.Window.size[0]*.013)
            self.rotatebtn.instance = Localdefs.towerabilitylist[2]
            self.rotatebtn.text = "Rotate Group"
            self.rotatebtn.image.source = self.rotatebtn.instance.imgstr
            #Player.player.tbbox.size = (Map.mapvar.squsize * 6, Map.mapvar.squsize * 6)
            Player.player.tbbox.height += 60
            Player.player.layout.height = Player.player.tbbox.height
            self.tbBoxRect.size=Player.player.tbbox.size
            Player.player.layout.add_widget(self.rotatebtn)
            self.drawTriangle()

        Map.mapvar.backgroundimg.add_widget(Player.player.tbbox)

    def upgradeScreen(self):
        Map.mapvar.background.removeAll()


    def drawTriangle(self):
        with Map.mapvar.backgroundimg.canvas.after:
            Color(1, 1, 0, 1)
            if Player.player.towerSelected.towerGroup.facing == 'l':
                Map.mapvar.triangle = self.getTriangle('l')
                if Player.player.tbbox.x < Player.player.towerSelected.x:
                    Player.player.tbbox.pos = (Player.player.tbbox.x - Map.mapvar.squsize, Player.player.tbbox.pos[1])
            elif Player.player.towerSelected.towerGroup.facing == 'r':
                Map.mapvar.triangle = self.getTriangle('r')
                if Player.player.tbbox.x > Player.player.towerSelected.x:
                    Player.player.tbbox.pos = (Player.player.tbbox.x + Map.mapvar.squsize, Player.player.tbbox.pos[1])
            elif Player.player.towerSelected.towerGroup.facing == 'u':
                Map.mapvar.triangle = self.getTriangle('u')
            elif Player.player.towerSelected.towerGroup.facing == 'd':
                Map.mapvar.triangle = self.getTriangle('d')

    def removeTriangle(self):
        if Map.mapvar.triangle:
            Map.mapvar.backgroundimg.canvas.after.remove(Map.mapvar.triangle)
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
        if Player.player.towerSelected and Player.player.towerSelected.level != Player.player.upgPathSelectLvl\
                and Player.player.money < Player.player.towerSelected.upgradeDict['Cost'][Player.player.towerSelected.level - 1]:
            self.disableBtn(self.upgbtn)
        elif Player.player.towerSelected and Player.player.towerSelected.level == Player.player.upgPathSelectLvl:
            if (Player.player.money < Player.player.towerSelected.upgradeDict['Cost'][Player.player.towerSelected.level - 1][0] or\
            Player.player.gems < Player.player.towerSelected.upgradeDict['Cost'][Player.player.towerSelected.level - 1][1]):
                self.disableBtn(self.upgbtn1)
                self.disableBtn(self.upgbtn2)
            elif Player.player.towerSelected.towerGroup.leader:
                self.disableBtn(self.upgbtn1)
                self.enableBtn(self.upgbtn2)
            else:
                self.enableBtn(self.upgbtn1)
                self.enableBtn(self.upgbtn2)
        else:
            self.enableBtn(self.upgbtn)

    def disableBtn(self, btn):
        btn.disabled = True

    def enableBtn(self, btn):
        btn.disabled = False

    def builderMenu(self, squarepos):
        self.createTBBox(squarepos, 4, 6)

        for button in Localdefs.iconlist:
            tmpbtn = GUI_Base.ButtonWithImage(text=' ', size_hint=(None, None),
                                     size=(Map.mapvar.squsize * 2, Map.mapvar.squsize * 2))
            tmpbtn.group = "Enableable"
            tmpbtn.instance = button
            tmpbtn.image.source = button.imgstr
            tmpbtn.label.text = " $" + str(button.cost)
            tmpbtn.label.size = (Map.mapvar.squsize, Map.mapvar.squsize * .6)
            tmpbtn.id = button.type
            attackable = button.attacks
            tmpbtn.toplabel.text = attackable
            if button.cost > Player.player.money:
                tmpbtn.disabled = True
            Player.player.layout.add_widget(tmpbtn)
        self.total_cost = Label(text = '$15', size_hint=(None, None), size = (Map.mapvar.squsize*2, Map.mapvar.squsize * 2),
                                font_size=main.Window.size[0]*.019, halign='center', color = [0,1,0,1])
        self.myDispatcher.bind(totalCost=self.on_totalCost)
        Player.player.layout.add_widget(self.total_cost)
        Map.mapvar.backgroundimg.add_widget(Player.player.tbbox)

gui = GUI()