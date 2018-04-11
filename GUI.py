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
        self.image = Image(text=" ")
        self.image.pos_hint = (None, None)
        self.add_widget(self.image)
        self.image.size = self.size
        self.image.pos = self.pos
        self.bind(pos=self.on_pos)
        self.label = Label(text=' ', size_hint=(None, None), pos=self.pos, color=[1, 1, 1, 1], halign='center')
        self.add_widget(self.label)
        self.group = None
        self.toplabel = Label(text='', size_hint=(1, .1), pos_hint=(None,None), text_size = (None, None), font_size = main.Window.size[0]*.01)
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
            if button.id == 'unpause':
                MainFunctions.pauseGame(button)
                return
            elif button.id == 'enemyinfo':
                gui.toggleEnemyPanel()
            # tower abilities like upgrade and sell
            elif button.instance in Localdefs.towerabilitylist:
                func = "TowerAbilities." + button.instance.type + "." + button.instance.func + "()"
                eval(func)
                if button.id == 'Rotate':
                    gui.removeTriangle()
                    gui.drawTriangle()
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


class pauseMenu(SmartMenu):
    # setup the menu button names

    def __init__(self, **kwargs):
        super(pauseMenu, self).__init__(**kwargs)
        self.unpause = Button()
        self.unpause.size_hint = (None, None)
        self.unpause.size = (Map.mapvar.scrwid, Map.mapvar.scrhei)
        self.unpause.pos = (0, 0)
        self.unpause.id = 'unpause'
        # self.unpause.bind(on_release = MainFunctions.pauseGame)
        self.image = Utilities.imgLoad('backgroundimgs/play.png', pos=self.unpause.center)
        self.image.size = (20, 20)
        self.unpause.add_widget(self.image)
        self.unpause.background_color = [.2, .2, .2, .2]
        self.add_widget(self.unpause)
        # with self.unpause.canvas.before:
        #   Color(.2,.2,.2,.1)
        #   Rectangle(size = self.unpause.size, pos=self.unpause.pos)


class mainMenu(SmartMenu):
    # setup the menu button names

    def __init__(self, **kwargs):
        super(mainMenu, self).__init__(**kwargs)

        self.layout = GridLayout(rows=3, size=(Map.mapvar.squsize * 23, Map.mapvar.squsize * 13),
                                 padding=[Map.mapvar.squsize], spacing=Map.mapvar.squsize)
        self.layout.center = ((Map.mapvar.scrwid / 2), (Map.mapvar.scrhei / 2))
        self.id = 'mainmenu'
        self.add_widget(self.layout)

        # use pos_hint to set the position relative to its parent by percentage.
        self.menulabel = Label(text='Tablet TD', size_hint = (1,.5))
        self.layout.add_widget(self.menulabel)
        self.menulabel.font_size = Window.width * 0.04

        with self.layout.canvas.before:
            Color(.3, .3, .3)
            self.menurect = Rectangle(size=self.layout.size, pos=self.layout.pos)
        with self.canvas.before:
            Color(.2, .2, .2, .2)
            self.bgrect = Rectangle(size=(Map.mapvar.scrwid, Map.mapvar.scrhei), pos=(0, 0))
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
        self.bgrect.size = main.Window.size
        self.menurect.pos = self.layout.pos


class topBarWidget():
    def __init__(self, label, var, source, icon):
        self.Box = StackLayout(orientation="lr-tb")
        self.Label = MyLabel(text=label)

        self.Variable = MyLabel(text=str(source), halign='right')
        gui.myDispatcher.fbind(var, self.set_value, var)
        self.Icon = Utilities.imgLoad(icon)
        self.Icon.size_hint = (None,1)
        self.Icon.width = 45
        self.Label.size_hint = (None,1)
        self.Label.width = Map.mapvar.squsize * 2
        self.Variable.size_hint = (None,1)
        self.Variable.width = Map.mapvar.squsize * 1.3
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
        self.bgrect = None
        self.messageCounter = None

    def bindings(self, *args):
        if self.topBar:
            self.topBar.pos = (0, Window.height - 45)
            self.topBar.layout.pos = self.topBar.pos
            self.topBar.size = (Window.width, 45)
            self.topBar.layout.size = self.topBar.size
        self.rightSideButtons_layout.pos = (Window.width - 55, 2 * Map.mapvar.squsize)

    def rightSideButtons(self):
        self.rightSideButtons_layout = StackLayout(size_hint=(None, None), size=(55, 70),
                                                   pos=(Window.width - 2*Map.mapvar.squsize, 2 * Map.mapvar.squsize))
        self.enemyInfoButton = ButtonWithImage(text=" ", id='enemyinfo', size_hint=(None, None), width=50, height=50)
        self.enemyInfoButton.image.source = "enemyimgs/Standard_r.png"
        self.enemyInfoButton.label.text = 'Info'
        self.enemyInfoButton.label.size = (50, 20)
        self.enemyInfoButton.pos = self.rightSideButtons_layout.pos
        self.rightSideButtons_layout.add_widget(self.enemyInfoButton)
        self.enemyInfoButton.image.pos = self.enemyInfoButton.pos
        self.enemyInfoButton.label.pos = self.enemyInfoButton.pos
        return self.rightSideButtons_layout

    def toggleEnemyPanel(self):
        if not Map.mapvar.enemypanel.parent:
            Map.mapvar.backgroundimg.add_widget(Map.mapvar.enemypanel)
            Map.mapvar.enemypanel.switch_to(Map.mapvar.enemypanel.getDefaultTab())
            Map.mapvar.background.popUpOpen = Map.mapvar.enemypanel
        else:
            Map.mapvar.backgroundimg.remove_widget(Map.mapvar.enemypanel)

    def createTopBar(self):
        self.topBar = Bar(pos=(0, Window.height - Map.mapvar.squsize*2), size=(Window.width, Map.mapvar.squsize*1.5))
        self.menuButton = Button(text='Menu', id='menu', size_hint=(None, None),
                                 width=Map.mapvar.squsize + Map.mapvar.squsize * .6, height=Map.mapvar.squsize,
                                 font_size=main.Window.size[0] * .015)
        self.menuButton.bind(on_release=MainFunctions.pauseGame)
        self.pauseButton = Button(text='Pause', id='pause', size_hint=(None, None),
                                  width=Map.mapvar.squsize + Map.mapvar.squsize * .6, height=Map.mapvar.squsize,
                                  font_size=main.Window.size[0] * .014)
        self.pauseButton.bind(on_release=MainFunctions.pauseGame)
        self.nextwaveButton = Button(text='Next Wave', id='next', size_hint=(None, None), width=3 * Map.mapvar.squsize,
                                     height=Map.mapvar.squsize, font_size=main.Window.size[0] * .015)
        self.nextwaveButton.bind(on_release=self.nextWave)
        self.nextwaveButton.valign = 'top'
        self.topBar.layout.add_widget(self.menuButton)
        self.topBar.layout.add_widget(self.pauseButton)
        self.topBar.layout.add_widget(self.nextwaveButton)
        self.topBar.layout.padding = [5]
        for label, var, source, icon in Localdefs.topBar_ElementList:
            topBarWidget(label, var, source, icon)

        return self.topBar

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
        squarepos[0] + 2 * Map.mapvar.squsize, squarepos[1] - Map.mapvar.squsize * 2), do_resize=False,
                                      do_rotation=False)
        if Player.player.tbbox.right > Map.mapvar.scrwid - Map.mapvar.squsize:
            Player.player.tbbox.set_right(squarepos[0])
        if Player.player.tbbox.top > Map.mapvar.playhei:
            Player.player.tbbox.top = Map.mapvar.playhei

        Player.player.layout = GridLayout(size_hint=(None, None), size=Player.player.tbbox.size, pos=(0, 0), cols=2)
        with Player.player.tbbox.canvas:
            Color(.1, .1, .1, .9)
            Rectangle(pos=(0, 0), size=Player.player.tbbox.size)
        # print Player.player.layout.size, Player.player.layout.pos, Player.player.tbbox.size, Player.player.tbbox.pos
        Player.player.tbbox.add_widget(Player.player.layout)
        Map.mapvar.background.popUpOpen = Player.player.tbbox

    def towerMenu(self, squarepos):
        self.createTBBox(squarepos, 6, 6)
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
        self.sellbtn = ButtonWithImage(text=' ', size_hint=(1, None), pos_hint=(1, 1), height=40,id = 'Sell',font_size = main.Window.size[0]*.013)
        self.sellbtn.group = None
        self.sellbtn.instance = Localdefs.towerabilitylist[0]
        self.sellbtn.instance.cost = int(Player.player.towerSelected.refund)
        self.sellbtn.image.source = self.sellbtn.instance.imgstr
        self.sellbtn.image.size_hint = (None, None)
        self.sellbtn.image.size = (Map.mapvar.squsize, Map.mapvar.squsize)
        self.sellbtn.image.pos = self.sellbtn.pos
        self.sellbtn.text = '            ' + self.sellbtn.instance.type + ':  $' + str(
            self.sellbtn.instance.cost)
        Player.player.layout.add_widget(self.sellbtn)

        self.sellbtn.x = Player.player.tbbox.x
        # upgrade data grid
        dataLayout = GridLayout(size=(Map.mapvar.squsize * 4, Map.mapvar.squsize * 4), pos=(0, 0), cols=3)
        headers = [' ', 'Current', 'Next']
        for h in headers:
            lbl = Label(text=str(h), text_size = (None,None), font_size = main.Window.size[0]*.013)
            dataLayout.add_widget(lbl)
        for item in Player.player.towerSelected.upgradeData:
            lbl = Label(text=str(item), text_size = (None,None), font_size = main.Window.size[0]*.013)
            dataLayout.add_widget(lbl)
        Player.player.layout.add_widget(dataLayout)
        # upgrade button
        self.upgbtn = ButtonWithImage(text=' ', size_hint=(1, None), height=40, id='Upgrade', font_size = main.Window.size[0]*.013)
        self.upgbtn.instance = Localdefs.towerabilitylist[1]
        self.upgbtn.instance.cost = Player.player.towerSelected.upgradeDict['Cost'][Player.player.towerSelected.level - 1]
        self.upgbtn.group = 'Enableable'
        self.upgbtn.text = '            ' + self.upgbtn.instance.type + ':  $' + str(self.upgbtn.instance.cost)
        self.upgbtn.image.source = self.upgbtn.instance.imgstr
        Player.player.layout.add_widget(self.upgbtn)
        self.toggleUpgBtn()
        if Player.player.towerSelected.percentComplete > 0:
            self.disableBtn(self.upgbtn)
            self.disableBtn(self.sellbtn)

        if Player.player.towerSelected.type == 'Wind':
            self.rotatebtn = ButtonWithImage(text=' ', size_hint=(1, None), height=40, id='Rotate', group = 'None', font_size = main.Window.size[0]*.013)
            self.rotatebtn.instance = Localdefs.towerabilitylist[2]
            self.rotatebtn.text = '            '+"Rotate Group"
            self.rotatebtn.image.source = self.rotatebtn.instance.imgstr
            #Player.player.tbbox.size = (Map.mapvar.squsize * 6, Map.mapvar.squsize * 6)
            Player.player.layout.height = Player.player.tbbox.height
            Player.player.layout.add_widget(self.rotatebtn)
            self.drawTriangle()

        Map.mapvar.backgroundimg.add_widget(Player.player.tbbox)

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
        if Player.player.towerSelected and Player.player.money < Player.player.towerSelected.upgradeDict['Cost'][
            Player.player.towerSelected.level - 1]:
            self.disableBtn(self.upgbtn)
        else:
            self.enableBtn(self.upgbtn)

    def disableBtn(self, btn):
        btn.disabled = True

    def enableBtn(self, btn):
        btn.disabled = False

    def builderMenu(self, squarepos):
        self.createTBBox(squarepos, 4, 6)

        for button in Localdefs.iconlist:
            tmpbtn = ButtonWithImage(text=' ', size_hint=(None, None),
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
        Map.mapvar.backgroundimg.add_widget(Player.player.tbbox)


gui = GUI()


class EnemyPanel(TabbedPanel):
    # currently instantiating in MAp
    CurrentWave = StringProperty()

    def on_CurrentWave(self, instance, value):
        # here we should update the variables whena  new wave starts (show next wave)
        self.switch_to(self.getDefaultTab())
        wavemod = (1 + (int(self.CurrentWave) / 70.0))
        x = 0
        for tab in self.tab_list:
            tab.enemyPanel_numEnemies.text = "Number: " + str(
                int(eval("Enemy." + self.enemytypelist[x] + ".defaultNum") * wavemod))
            tab.enemyPanel_enemyHealth.text = "HP: " + str(
                int(eval("Enemy." + self.enemytypelist[x] + ".health") * wavemod))
            tab.enemyPanel_enemySpeed.text = "Speed: " + str(
                int(eval("Enemy." + self.enemytypelist[x] + ".speed") * wavemod))
            tab.enemyPanel_enemyArmor.text = "Armor: " + str(
                int(eval("Enemy." + self.enemytypelist[x] + ".armor") * wavemod))
            tab.enemyPanel_enemyReward.text = "Reward: " + str(
                int(eval("Enemy." + self.enemytypelist[x] + ".reward") * wavemod))
            x += 1

    def __init__(self, **kwargs):
        super(EnemyPanel, self).__init__(**kwargs)
        self.tab_pos = 'right_top'
        self.tab_height = Map.mapvar.squsize*1.3
        self.tab_width = Map.mapvar.squsize*1.3
        self.size_hint = (1, 1)
        self.size = (Map.mapvar.squsize*10, Map.mapvar.squsize*8)
        self.pos = (Window.width - Map.mapvar.squsize * 15, Map.mapvar.squsize * .3)
        self.background_color = [.1, .1, .1, .6]
        self.border = [1, 1, 1, 1]
        self.do_default_tab = False
        self.bind(CurrentWave=self.on_CurrentWave)

        with self.canvas:
            Color(1, 1, 1, 1)
        self.enemytypelist = ['Standard', 'Airborn', 'Splinter', 'Strong', 'Crowd']
        for enemy in self.enemytypelist:
            th = panelHeader(pos=self.pos, size=self.size)
            th.id = enemy
            th.background_normal = "enemyimgs/" + enemy + "_l.png"
            th.background_down = "enemyimgs/" + enemy + "_r.png"
            self.add_widget(th)
            th.content = th.createEnemyPanelContent(enemy)

    def getDefaultTab(self, *args):
        enemy = Player.player.waveList[Player.player.wavenum]['enemytype']
        for tab in self.tab_list:
            if tab.id == enemy:
                return tab


class panelHeader(TabbedPanelHeader):
    def __init__(self, **kwargs):
        super(panelHeader, self).__init__(**kwargs)
        self.enemyPanelLayout = StackLayout(size_hint=(1, 1))
        self.add_widget(self.enemyPanelLayout)
        self.enemyPanelLayout.pos = self.pos
        self.enemyPanelLayout.size = self.size

    def createEnemyPanelContent(self, enemy):
        waveNum = Player.player.wavenum
        self.enemyPanel_header = Label(text=str(enemy), width=self.width - Map.mapvar.squsize,
                                       height=Map.mapvar.squsize * 1.3, size_hint=(None, None), font_size=main.Window.size[0]*.019,
                                       text_size=(Map.mapvar.squsize * 7, Map.mapvar.squsize * 1.3), halign='center')
        self.enemyPanel_enemyinfo = GridLayout(cols=1, col_force_default=True, row_force_default=True,
                                               row_default_height=Map.mapvar.squsize, col_default_width=self.width,
                                               size_hint=(None, None))
        self.enemyPanel_numEnemies = Label(
            text="Number: " + str(int(eval("Enemy." + enemy + ".defaultNum") * (1 + (waveNum / 70.0)))), font_size=main.Window.size[0]*.015,
            text_size=(Map.mapvar.squsize * 7, Map.mapvar.squsize))
        self.enemyPanel_enemyHealth = Label(
            text="HP: " + str(int(eval("Enemy." + enemy + ".health") * (1 + (waveNum / 70.0)))), font_size=main.Window.size[0]*.015,
            text_size=(Map.mapvar.squsize * 7, Map.mapvar.squsize))
        self.enemyPanel_enemySpeed = Label(
            text="Speed: " + str(int(eval("Enemy." + enemy + ".speed") * (1 + (waveNum / 70.0)))), font_size=main.Window.size[0]*.015,
            text_size=(Map.mapvar.squsize * 7, Map.mapvar.squsize))
        self.enemyPanel_enemyArmor = Label(
            text="Armor: " + str(int(eval("Enemy." + enemy + ".armor") * (1 + (waveNum / 70.0)))), font_size=main.Window.size[0]*.015,
            text_size=(Map.mapvar.squsize * 7, Map.mapvar.squsize))
        self.enemyPanel_enemyReward = Label(
            text="Reward: " + str(int(eval("Enemy." + enemy + ".reward") * (1 + (waveNum / 70.0)))), font_size=main.Window.size[0]*.015,
            text_size=(Map.mapvar.squsize * 7, Map.mapvar.squsize))
        self.enemyPanel_disclaimer = Label(text="Numbers reflect enemy if sent next wave", font_size=main.Window.size[0]*.008,
                                           text_size=(Map.mapvar.squsize * 9, Map.mapvar.squsize))
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
    def __init__(self, **kwargs):
        super(Bar, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='horizontal')
        self.layout.pos = self.pos
        self.layout.size = self.size
        self.add_widget(self.layout)

    def addButtons(self, buttonList):
        for button in buttonList:
            tmpbtn = MyButton(text=button)
            # tmpbtn.background_color = [1,1,1,1]
            # tmpbtn.bind(on_release=self.callback)
            self.layout.add_widget(tmpbtn)

    def addElements(self, elementList):
        # likely need to create individual widgets to update later.
        for element, var, icon in elementList:
            box = GridLayout(cols=3, col_force_default=True, row_force_default=True, row_default_height=50,
                             col_default_width=55)
            label = MyLabel(text=element)
            element = StringProperty()
            variable = MyLabel(text=str(var))
            variable.id = element
            icon = Utilities.imgLoad(icon)
            icon.size_hint_x = None
            icon.size = (Map.mapvar.squsize, Map.mapvar.squsize)
            label.size_hint_x = None
            label.size = (Map.mapvar.squsize + Map.mapvar.squsize * .3, Map.mapvar.squsize + Map.mapvar.squsize * .6)
            # nlabel.valign='center'
            variable.size_hint_x = None
            variable.size = (3 * Map.mapvar.squsize, Map.mapvar.squsize + Map.mapvar.squsize * .6)
            box.add_widget(icon)
            box.add_widget(label)
            box.add_widget(variable)
            gui.topBar_Boxlist.append(box)
            self.layout.add_widget(box)

            # with tmplbl.canvas:
            #    Color(.4, .4, .4, .8)
            #    self.rect=Rectangle(size=tmplbl.size, pos=tmplbl.pos)
