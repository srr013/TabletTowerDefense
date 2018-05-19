import os

from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import *
from kivy.graphics.vertex_instructions import RoundedRectangle
from kivy.properties import ObjectProperty
from kivy.animation import Animation
from kivy.lang import Builder

import Player
import __main__
import Map
import Localdefs
import EventFunctions
import TowerAbilities

Builder.load_string("""
<Label>
    color: 0,0,0,1
    
<TowerMenu>
    StackLayout
        id: toplayout
        size_hint: 1, .2
        spacing: 5
        TowerButton
            id: sellbutton
            size_hint: .75, 1
            background_normal: 'GUI/orange_button_normal.png'
            background_down: 'GUI/orange_button_down.png'
        Button
            id: infobutton
            size_hint: .25, .97
            on_release: app.root.change_screens('info')
            Image
                source: "iconimgs/info.png"
                center: self.parent.center
                size: self.parent.width/2, self.parent.height/2
                center: self.parent.center
    GridLayout
        id: towerinfo
        size_hint: 1, .6
        cols: 4
        padding: 10
        

<StandardUpgradeLayout>   
    id: upgradelayout
    size_hint: 1,.2
    TowerButton
        id: upgradebutton
        size_hint: .7, 1
    StackLayout
        orientation: 'tb-lr'
        size_hint: .3, 1
        Label
            size_hint: 1, .4
            text: "Upgrade All?"
            text_size: self.size
            font_size: self.width * .15
            halign: 'center'
            valign: 'top'
        CheckBox
            size_hint: 1, .6
            id: upgradeall
            on_active: upgradelayout.updateUpgradeAll()
            
<PathUpgradeLayout>   
    id: upgradelayout
    size_hint: 1,.2
    spacing: 5
    TowerUpgPathButton
        id: LeaderPath
        size_hint: .5, 1
        disabled: True if Player.player.towerSelected.towerGroup.leader else False
    TowerUpgPathButton
        id: Damage
        size_hint: .5, 1

<WindStandardLayout>
    id: upgradelayout
    size_hint: 1, .3
    spacing: 5
    TowerButton
        id: upgradebutton
        size_hint: .7, .5
    StackLayout
        orientation: 'tb-lr'
        size_hint: .3, .5
        Label
            size_hint: 1, .4
            text: "Upgrade All?"
            text_size: self.size
            font_size: self.width * .145
            halign: 'center'
            valign: 'top'
        CheckBox
            size_hint: 1, .6
            id: upgradeall
            on_active: upgradelayout.updateUpgradeAll()
    TowerButton
        id: rotatebutton
        size_hint: 1, .5
        
<WindPathUpgradeLayout>
    id: upgradelayout
    size_hint: 1, .3
    spacing: 5
    TowerUpgPathButton
        id: LeaderPath
        size_hint: .5, .5
        disabled: True if Player.player.towerSelected.towerGroup.leader else False
    TowerUpgPathButton
        id: Damage
        size_hint: .5, .5
    TowerButton
        id: rotatebutton
        size_hint: 1, .5

<TowerButton>
    image:image
    label:label
    size_hint: 1, 1
    on_release: self.release()
    disabled: False if Player.player.towerSelected.totalUpgradeTime == 0 else True
    Image:
        id: image
        size: app.root.squsize, app.root.squsize
        pos: self.parent.x + self.width/5, self.parent.y + self.height/2.3
    Label:
        id: label
        color: 0,0,0,1
        text: ""
        font_size: app.root.scrwid*.02
        text_size: None,None
        halign: 'center'
        size: self.texture_size
        pos: self.parent.center_x - self.width/3, self.parent.center_y-self.height/2

<TowerUpgPathButton>
    image:image
    label:label
    disabled: False if Player.player.towerSelected.totalUpgradeTime == 0 else True
    size_hint: 1, 1
    group: 'Enableable'
    on_release: self.release()
    Image:
        id: image
        size: app.root.squsize, app.root.squsize
        pos: self.parent.x + app.root.squsize/4, self.parent.y + app.root.squsize/2
    Label:
        id: label
        color: 0,0,0,1
        font_size: app.root.scrwid*.011
        text_size: self.width, self.parent.height * .6
        halign: 'right'
        valign: 'middle'
        pos: self.parent.center_x - self.width/3, self.parent.center_y-self.height/2

<ConfirmSell>
    rows: 1
    padding: 15
    Button:
        size_hint: 1,1
        on_release: TowerAbilities.Sell.apply()
        Label:
            text: 'Confirm Sale'
            font_size: self.parent.width * .15
            text_size: self.parent.size
            center: root.center
            valign: 'center'
            halign: 'center'

""")

class PopUpBox(ScatterLayout):
    def __init__(self, squarepos, squwid, squhei,  **kwargs):
        super(PopUpBox, self).__init__(**kwargs)
        self.size = (Map.mapvar.squsize * squwid, Map.mapvar.squsize * squhei)
        self.pos = (squarepos[0] + 3 * __main__.app.root.squsize,squarepos[1] + __main__.app.root.squsize - __main__.app.root.squsize * squhei / 2)
        self. do_resize = False
        self.do_rotation = False
        Player.player.tbbox = self
        if self.right > __main__.app.root.scrwid - __main__.app.root.squsize*2:
            self.set_right(squarepos[0])
        if self.top > __main__.app.root.playhei:
            self.top = __main__.app.root.playhei
        if self.y < 5:
            self.y = 5
        self.layout = GridLayout(size_hint=(None, None), size=Player.player.tbbox.size, pos=(0, 0), cols=2, spacing = 4, padding = 5)
        with self.canvas.before:
            Color(.4, .4, .4, 1)
            self.rect = RoundedRectangle(pos=(0, 0), size=self.size)
        Player.player.layout = self.layout
        self.add_widget(self.layout)
        self.enableList = []
        self.upgradeAll = False
        # print Player.player.layout.size, Player.player.layout.pos, Player.player.tbbox.size, Player.player.tbbox.pos
        Map.mapvar.background.popUpOpen = self
        Map.mapvar.popupcontainer.add_widget(self)
        self.type = None

    def createBuilderMenu(self):
        self.type = 'Builder'
        for button in Localdefs.iconlist:
            tmpbtn = BuilderButton()
            tmpbtn.create(button)
            tmpbtn.ids.bottomlabel.texture_update()
            if button.cost > Player.player.money:
                tmpbtn.disabled = True
            Player.player.layout.add_widget(tmpbtn)
            self.enableList.append(tmpbtn)
        self.cost_layout = BuilderLabel()
        Player.player.layout.add_widget(self.cost_layout)
        self.cost_layout.get_color()
        Player.player.myDispatcher.bind(totalCost=self.cost_layout.on_totalCost)
        Player.player.myDispatcher.bind(Money = self.cost_layout.on_Money)

    def createTowerMenu(self):
        self.type = "Tower"
        Player.player.layout.cols = 1
        menu = TowerMenu()
        Player.player.layout.add_widget(menu.createTowerMenu())


class TowerMenu(StackLayout):
    def __init__(self, **kwargs):
        super(TowerMenu,self).__init__(**kwargs)
        pass

    def createTowerMenu(self):
        if Player.player.towerSelected.type == 'Wind':
            self.ids.toplayout.size_hint = (1,.17)
        Player.player.tbbox.enableList.append(self.ids.sellbutton)
        self.ids.sellbutton.instance = Localdefs.towerabilitylist[0]
        self.ids.sellbutton.ids.image.source = self.ids.sellbutton.instance.imgstr
        self.ids.sellbutton.ids.label.text = "Sell: $" + str(Player.player.towerSelected.refund)
        self.ids.infobutton.instance = {'type': 'info'}
        towerMenuHeaders = [' ', 'Current', 'Group Bonus', 'Next']
        for h in towerMenuHeaders:
            lbl = Label(text=str(h), text_size=(__main__.app.root.squsize*1.8, None),
                        font_size=__main__.Window.size[0] * .013,  valign = 'center', halign = 'center')
            self.ids.towerinfo.add_widget(lbl)
        t = Player.player.towerSelected.menuStats
        for key in t.keys():
            lbl = Label(text=t[key][3], font_size=__main__.app.root.scrwid * .013)
            self.ids.towerinfo.add_widget(lbl)
            lbl.text_size = (lbl.parent.width,None)
            lbl2 = Label(text=t[key][0], text_size=(None, None), font_size=__main__.app.root.scrwid * .013)
            self.ids.towerinfo.add_widget(lbl2)
            lbl3 = Label(text=t[key][1], text_size=(None, None), font_size=__main__.app.root.scrwid * .013)
            self.ids.towerinfo.add_widget(lbl3)
            lbl4 = Label(text=t[key][2], text_size=(None, None), font_size=__main__.app.root.scrwid * .013)
            self.ids.towerinfo.add_widget(lbl4)
        self.add_widget(self.getUpgradeButtons())
        return self


    def getUpgradeButtons(self):
        if Player.player.towerSelected.level != Player.player.upgPathSelectLvl and Player.player.towerSelected.type != 'Wind':
            layout = StandardUpgradeLayout()
            instance = Localdefs.towerabilitylist[1]
            layout.ids.upgradebutton.instance = instance

            Player.player.tbbox.enableList.append(layout.ids.upgradebutton)
            layout.ids.upgradebutton.ids.label.font_size = __main__.app.root.scrwid * .013
            layout.ids.upgradebutton.ids.label.halign = 'right'
            cost = Player.player.towerSelected.upgradeDict['Cost'][Player.player.towerSelected.level]
            layout.ids.upgradebutton.instance.cost = cost
            if cost > Player.player.money:
                layout.ids.upgradebutton.disabled = True
            layout.ids.upgradebutton.ids.label.text = 'Upgrade:  $' + str(cost)
            layout.ids.upgradebutton.ids.image.source = instance.imgstr
        elif Player.player.towerSelected.type == 'Wind':
            Player.player.tbbox.size = (Player.player.tbbox.width, Player.player.tbbox.height * 1.25)
            Player.player.layout.size = Player.player.tbbox.size
            with Player.player.tbbox.canvas.before:
                Color(.4, .4, .4, 1)
                RoundedRectangle(pos=(0, 0), size=Player.player.tbbox.size)
            self.ids.towerinfo.size_hint = (1, .5)
            if Player.player.towerSelected.level != Player.player.upgPathSelectLvl:
                layout = WindStandardLayout()
                instance = Localdefs.towerabilitylist[1]
                layout.ids.upgradebutton.instance = instance
                Player.player.tbbox.enableList.append(layout.ids.upgradebutton)
                layout.ids.upgradebutton.ids.label.font_size = __main__.app.root.scrwid * .013
                layout.ids.upgradebutton.ids.label.halign = 'right'
                cost = Player.player.towerSelected.upgradeDict['Cost'][Player.player.towerSelected.level]
                layout.ids.upgradebutton.instance.cost = cost
                if cost > Player.player.money:
                    layout.ids.upgradebutton.disabled = True
                layout.ids.upgradebutton.ids.label.text = 'Upgrade:  $' + str(cost)
                layout.ids.upgradebutton.ids.image.source = instance.imgstr
                layout.ids.rotatebutton.instance = Localdefs.towerabilitylist[2]
                layout.ids.rotatebutton.ids.image.source = "iconimgs/Rotate.png"
                layout.ids.rotatebutton.ids.label.text = "Rotate Group"
            else:
                layout = WindPathUpgradeLayout()
                layout.ids.LeaderPath.instance = Localdefs.towerabilitylist[1]
                cost = Player.player.towerSelected.upgradeDict['Cost'][Player.player.towerSelected.level]
                layout.ids.LeaderPath.id = 'LeaderPath'
                layout.ids.LeaderPath.instance.cost = cost
                layout.ids.LeaderPath.ids.label.text = 'Leader Path  $' + str(cost[0]) + " + " + str(cost[1]) + " Gems"
                layout.ids.LeaderPath.ids.image.source = "towerimgs/crown.png"
                Player.player.tbbox.enableList.append(layout.ids.LeaderPath)
                layout.ids.Damage.instance = Localdefs.towerabilitylist[1]
                layout.ids.Damage.instance.cost = cost
                layout.ids.Damage.ids.label.text = 'Damage Path $' + str(cost[0]) + " + " + str(cost[1]) + " Gems"
                layout.ids.Damage.ids.image.source = "towerimgs/Wind/icon.png"
                Player.player.tbbox.enableList.append(layout.ids.Damage)
                layout.ids.rotatebutton.instance = Localdefs.towerabilitylist[2]
                layout.ids.rotatebutton.ids.image.source = "iconimgs/Rotate.png"
                layout.ids.rotatebutton.ids.label.text = "Rotate Group"
                if cost[0] > Player.player.money or cost[1] > Player.player.gems:
                    layout.ids.Damage.disabled = True
                    layout.ids.LeaderPath.disabled = True

        else:
            layout = PathUpgradeLayout()
            layout.ids.LeaderPath.instance = Localdefs.towerabilitylist[1]
            cost = Player.player.towerSelected.upgradeDict['Cost'][Player.player.towerSelected.level]
            layout.ids.LeaderPath.instance.cost = cost
            layout.ids.LeaderPath.id = 'LeaderPath'
            layout.ids.LeaderPath.ids.label.text = 'Leader Path  $' + str(cost[0]) + " + " + str(cost[1]) + " Gems"
            layout.ids.LeaderPath.ids.image.source = "towerimgs/crown.png"
            Player.player.tbbox.enableList.append(layout.ids.LeaderPath)
            layout.ids.Damage.instance = Localdefs.towerabilitylist[1]
            layout.ids.Damage.instance.cost = cost
            layout.ids.Damage.ids.label.text = 'Damage Path $' + str(cost[0]) + " + " + str(cost[1]) + " Gems"
            layout.ids.Damage.ids.image.source = os.path.join("towerimgs", Player.player.towerSelected.type,
                                                                  "icon.png")
            Player.player.tbbox.enableList.append(layout.ids.Damage)
            if cost[0] > Player.player.money or cost[1] > Player.player.gems:
                layout.ids.Damage.disabled = True
                layout.ids.LeaderPath.disabled = True

        return layout

class StandardUpgradeLayout(StackLayout):
    def updateUpgradeAll(self):
        if Player.player.tbbox.upgradeAll == False:
            Player.player.tbbox.upgradeAll = True
            self.ids.upgradebutton.ids.label.text =  'Upgrade All (Lowest Level Only):  $' + str(
                TowerAbilities.UpgradeAll.totalCost(Player.player.towerSelected))
            self.ids.upgradebutton.ids.label.text_size = (self.ids.upgradebutton.width*.7, None)
            self.ids.upgradebutton.ids.label.halign = 'center'
        else:
            Player.player.tbbox.upgradeAll = False
            self.ids.upgradebutton.ids.label.text = 'Upgrade:  $' + str(Player.player.towerSelected.upgradeDict['Cost'][
                Player.player.towerSelected.level])


class PathUpgradeLayout(StackLayout):
    pass
class WindStandardLayout(StackLayout):
    def updateUpgradeAll(self):
        if Player.player.tbbox.upgradeAll == False:
            Player.player.tbbox.upgradeAll = True
            self.ids.upgradebutton.ids.label.text =  'Upgrade All (Lowest Level Only):  $' + str(
                TowerAbilities.UpgradeAll.totalCost(Player.player.towerSelected))
            self.ids.upgradebutton.ids.label.text_size = (self.ids.upgradebutton.width * .7, None)
            self.ids.upgradebutton.ids.label.halign = 'center'
        else:
            Player.player.tbbox.upgradeAll = False
            self.ids.upgradebutton.ids.label.text = 'Upgrade:  $' + str(Player.player.towerSelected.upgradeDict['Cost'][
                Player.player.towerSelected.level])

class WindPathUpgradeLayout(StackLayout):
    pass

class ConfirmSell(GridLayout):
    pass

class TowerButton(Button):
    image = ObjectProperty()
    label = ObjectProperty()

    def release(self):
        if self.instance.type == 'Rotate':
            TowerAbilities.Rotate.apply()
            return
        elif self.instance.type == 'Sell':
            Map.mapvar.background.removeAll()
            self.tbbox = PopUpBox(Player.player.towerSelected.pos, 4, 3)
            Player.player.layout.cols = 1
            self.tbbox.add_widget(ConfirmSell())
            return
        if Player.player.tbbox.upgradeAll:
            TowerAbilities.UpgradeAll.upgradeAll(Player.player.towerSelected)
        else:
            TowerAbilities.Upgrade.apply()

    def checkDisabled(self):
        if self.instance.type != 'Rotate' and self.instance.type != 'Sell':
            if self.instance.cost > Player.player.money:
                return True
        return False

class TowerUpgPathButton(Button):
    image = ObjectProperty()
    label = ObjectProperty()

    def release(self):
        if self.id == 'LeaderPath':
            string = 'LeaderPath'
        else:
            string = str(Player.player.towerSelected.type) + "Damage"

        TowerAbilities.Upgrade.apply(id=string)

class BuilderButton(Button):
    image = ObjectProperty()
    toplabel = ObjectProperty()
    bottomlabel = ObjectProperty()

    def create(self, button):
        self.instance = button
        self.image.source = button.imgstr
        self.bottomlabel.text = " $" + str(button.cost)
        self.toplabel.text = button.attacks

class BuilderLabel(GridLayout):
    def get_color(self):
        if 15 > Player.player.money:
            self.ids.cost.color = (1, 0, 0, 1)
        else:
            self.ids.cost.color = (0, 1, 0, 1)

    def on_totalCost(self, instance, value):
        cost = int(Player.player.myDispatcher.totalCost)
        if cost == 1:
            cost = 15
        if cost > Player.player.money:
            self.ids.cost.color = (1,0,0,1)
        self.ids.cost.text = "$" + str(cost)

    def on_Money(self, instance, value):
        cost = int(Player.player.myDispatcher.totalCost)
        if cost <= Player.player.money:
            self.ids.cost.color = (0, 1, 0, 1)
        else:
            self.ids.cost.color = (1, 0, 0, 1)
        self.ids.money.text = str(Player.player.money)
    money = ObjectProperty()
    cost = ObjectProperty()


class WaveStreamer(StackLayout):
    def __init__(self, **kwargs):
        super(WaveStreamer, self).__init__(**kwargs)
        self.scroll_length = .3

    def nextWave(self, *args):
        if Player.player.wavenum != 0:
            self.waveAnimation.stop(__main__.ids.wavescroller)
        if self.waveAnimation.duration != 20:
            self.waveAnimation = Animation(scroll_x=self.scroll_length, duration=20.0)
            self.waveAnimation.bind(on_complete=EventFunctions.updateAnim)
        EventFunctions.nextWave()


    def createWaveStreamer(self):
        self.buildWaves()
        self.waveAnimation = Animation(scroll_x=self.scroll_length, duration=20.0)
        self.waveAnimation.bind(on_complete=EventFunctions.updateAnim)

    def resetWaveStreamer(self):
        self.removeWaveStreamer()
        self.buildWaves()
        __main__.ids.wavescroller.scroll_x = 0

    def buildWaves(self):
        x = 1
        for wave in Player.player.waveTypeList:
            lbl = Label(size_hint=(None, None), font_size = __main__.app.root.scrwid*.012,
                        text=str(x) + '. '+ wave[0], id='wave' + str(x), text_size=(None, None),
                        size=(Map.mapvar.squsize * 4, Map.mapvar.squsize), color=[0, 0, 0, 1], texture_size = self.size, halign = 'left')
            x += 1
            if wave[1]:  # if boss
                lbl.bold = True
                lbl.color = [1, 0, 0, 1]
            __main__.app.root.ids.wavelist.add_widget(lbl)


    def removeWaveStreamer(self):
        __main__.ids.wavelist.clear_widgets()


def disableTowerButtons():
    if Player.player.tbbox:
        if Player.player.tbbox.type == 'Tower':
            for button in Player.player.tbbox.enableList:
                button.disabled = True