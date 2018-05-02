import os
from kivy.core.window import Window
from kivy.graphics import *
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.stacklayout import StackLayout
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelHeader
from kivy.uix.image import Image
from kivy.properties import StringProperty

import GUI
import GUI_Base
import Map
import Player
import Utilities
import __main__
import Enemy #in use
import Towers #in use
import Localdefs
import FireTower
import LifeTower
import IceTower
import GravityTower
import WindTower


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
        self.tab_height = Map.mapvar.squsize*1.8
        self.tab_width = Map.mapvar.squsize*1.8
        self.size_hint = (1, 1)
        self.size = (Map.mapvar.squsize * 12, Map.mapvar.squsize * 10)
        self.pos = (Window.width - self.width - 3 * Map.mapvar.squsize, Map.mapvar.squsize * .3)
        self.background_color = [.1, .1, .1, .8]
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
            if enemy == 'Crowd':
                th.background_normal = "enemyimgs/Crowd_icon.png"
            th.background_down = "enemyimgs/" + enemy + "_icon_down.png"
            self.add_widget(th)
            th.content = th.createEnemyPanelContent(enemy)

    def getDefaultTab(self, *args):
        enemy = Player.player.waveList[Player.player.wavenum+1]['enemytype']
        for tab in self.tab_list:
            if tab.id == enemy:
                return tab

class TowerPanel(TabbedPanel):
    # currently instantiating in MAp

    def __init__(self, **kwargs):
        super(TowerPanel, self).__init__(**kwargs)
        self.tab_pos = 'right_top'
        self.tab_height = Map.mapvar.squsize*1.5
        self.tab_width = Map.mapvar.squsize*1.5
        #self.size_hint = (1, 1)
        self.size = (Map.mapvar.squsize*16, Map.mapvar.squsize*16)
        self.pos = (Window.width - self.width - 3*Map.mapvar.squsize, Map.mapvar.squsize * .3)
        self.background_color = [.1, .1, .1, .8]
        self.border = [1, 1, 1, 1]
        self.do_default_tab = False

        with self.canvas:
            Color(1, 1, 1, 1)

        towerAttributes = panelHeader(pos=self.pos, size=self.size)
        towerAttributes.id = 'towerAttributes'
        towerAttributes.color = [0,0,0,1]
        towerAttributes.text = 'General'
        towerAttributes.background_normal = "towerimgs/questionmark.png"
        towerAttributes.background_down = "towerimgs/questionmark_down.png"
        self.add_widget(towerAttributes)
        towerAttributes.content = towerAttributes.createBasicPanel()

        self.towertypelist = ['Life', 'Fire', 'Gravity', 'Ice', 'Wind']
        for tower in self.towertypelist:
            th = panelHeader(pos=self.pos, size=self.size)
            th.id = tower
            th.color = [0,0,0,1]
            th.text = tower
            th.background_normal = "towerimgs/"+tower+"/icon.png"
            th.background_down = "towerimgs/"+tower+"/icon_down.png"
            self.add_widget(th)
            th.content = th.createTowerPanelContent(tower)

    def getDefaultTab(self, *args):
        if Player.player.towerSelected:
            tower = Player.player.towerSelected.type
            for tab in self.tab_list:
                if tab.id == tower:
                    return tab
        else:
            return self.tab_list[-1]


class panelHeader(TabbedPanelHeader):
    def __init__(self, **kwargs):
        super(panelHeader, self).__init__(**kwargs)
        self.panelLayout = StackLayout(size_hint=(1, 1))
        self.add_widget(self.panelLayout)
        self.panelLayout.pos = (self.x+10, self.y+10)
        self.panelLayout.size = self.size

    def createBasicPanel(self):
        self.basicPanel_header = Label(text="Tower Attributes", size_hint=(1, .1), text_size = (None,None),
                                       font_size=__main__.Window.size[0] * .016, halign='center')
        self.basicPanel_towerinfo = StackLayout(orientation = 'tb-lr', size = self.panelLayout.size, padding = [7], spacing = [0,3])
        self.panelLayout.add_widget(self.basicPanel_header)
        self.panelLayout.add_widget(self.basicPanel_towerinfo)
        for i in Localdefs.towerAttributes:
            lbl = Label(text=i, markup = True, size_hint=(None,None),width = self.width/1.2, height = Map.mapvar.squsize*1.5, halign='left',
                        valign='center',font_size = __main__.Window.size[0]*.008)
            lbl.text_size = lbl.size
            self.basicPanel_towerinfo.add_widget(lbl)
        for i in Localdefs.towerAttackTypes:
            lbl = Label(text=i, markup = True, size_hint=(None, None), width=self.width / 1.1, height=Map.mapvar.squsize*.7, halign='left',
                        valign='center', font_size=__main__.Window.size[0] * .008)
            lbl.text_size = lbl.size
            self.basicPanel_towerinfo.add_widget(lbl)
        return self.panelLayout

    def createTowerPanelContent(self, tower):
        self.towerPanel_header = Label(text=str(tower)+" Tower Upgrades", width=self.width - Map.mapvar.squsize,
                                       height=Map.mapvar.squsize * 1.3, size_hint=(None, None), font_size=__main__.Window.size[0]*.016,
                                       text_size=(Map.mapvar.squsize * 7, Map.mapvar.squsize * 1.3), halign='center')
        self.towerPanel_towerinfo = GridLayout(cols=2)

        path1 = StackLayout(orientation='lr-tb', size_hint=(.5,1))
        path1title = Label(text = "Leader", size_hint= (1,.1), font_size = __main__.Window.size[0]*.013)
        path1image = Image(source = "towerimgs/crown.png", size_hint = (1,.1))
        path1desc = Label(text = "Grants all other connected towers a bonus to all stats, but this tower loses the ability to attack."
                                 "You may only build one leader per Tower Group. A Tower Group is a set of connected towers of the same type.",
                          size_hint = (1,.43), valign = 'center', halign = 'left')
        path1desc.text_size = (self.width/2.5, self.height)
        path1.add_widget(path1title)
        path1.add_widget(path1image)
        path1.add_widget(path1desc)
        self.towerPanel_towerinfo.add_widget(path1)

        path2 = StackLayout(orientation='lr-tb', size_hint = (.45,1))
        path2title = Label(text=eval(tower+"Tower."+tower+"Tower."+"upgradeName"), size_hint=(1, .1), font_size=__main__.Window.size[0] * .013)
        path2image = Image(source=eval(tower+"Tower."+tower+"Tower.imagestr"), size_hint=(1, .1))
        path2desc = Label(text=eval(tower+"Tower."+tower+"Tower.upgradeDescription"),
                          size_hint = (1,.4), valign = 'center', halign = 'left')
        path2desc.text_size = (self.width/2.5, self.height)
        path2.add_widget(path2title)
        path2.add_widget(path2image)
        path2.add_widget(path2desc)
        path2data = GridLayout(cols=1, size_hint = (1, .3), spacing = 0)
        for i in eval(tower+"Tower."+tower+"Tower.upgradeStats"):
            lbl = Label(text=i, size_hint=(1, None), halign='left', )
            lbl.text_size = (self.width / 2.5, lbl.height)
            path2data.add_widget(lbl)
        path2.add_widget(path2data)
        self.towerPanel_towerinfo.add_widget(path2)
        self.panelLayout.add_widget(self.towerPanel_header)
        self.panelLayout.add_widget(self.towerPanel_towerinfo)
        return self.panelLayout

    def createEnemyPanelContent(self, enemy):
        waveNum = Player.player.wavenum
        self.enemyPanel_header = Label(text=str(enemy), size_hint=(1, .2), font_size=__main__.Window.size[0]*.022,
                                       halign='center')
        self.enemyPanel_enemyinfo = GridLayout(cols=1, col_force_default=True, row_force_default=True,
                                               row_default_height=Map.mapvar.squsize, col_default_width=self.width,
                                               size_hint=(1, .8))
        self.enemyPanel_numEnemies = Label(
            text="Number: " + str(int(eval("Enemy." + enemy + ".defaultNum") * (1 + (waveNum / 70.0)))), font_size=__main__.Window.size[0]*.015,
            text_size=(Map.mapvar.squsize * 7, Map.mapvar.squsize))
        self.enemyPanel_enemyHealth = Label(
            text="HP: " + str(int(eval("Enemy." + enemy + ".health") * (1 + (waveNum / 70.0)))), font_size=__main__.Window.size[0]*.015,
            text_size=(Map.mapvar.squsize * 7, Map.mapvar.squsize))
        self.enemyPanel_enemySpeed = Label(
            text="Speed: " + str(int(eval("Enemy." + enemy + ".speed") * (1 + (waveNum / 70.0)))), font_size=__main__.Window.size[0]*.015,
            text_size=(Map.mapvar.squsize * 7, Map.mapvar.squsize))
        self.enemyPanel_enemyArmor = Label(
            text="Armor: " + str(int(eval("Enemy." + enemy + ".armor") * (1 + (waveNum / 70.0)))), font_size=__main__.Window.size[0]*.015,
            text_size=(Map.mapvar.squsize * 7, Map.mapvar.squsize))
        self.enemyPanel_enemyReward = Label(
            text="Reward: " + str(int(eval("Enemy." + enemy + ".reward") * (1 + (waveNum / 70.0)))), font_size=__main__.Window.size[0]*.015,
            text_size=(Map.mapvar.squsize * 7, Map.mapvar.squsize))
        self.enemyPanel_disclaimer = Label(text="Numbers reflect enemy if sent next wave", font_size=__main__.Window.size[0]*.008,
                                           text_size=(Map.mapvar.squsize * 9, Map.mapvar.squsize))
        self.enemyPanel_enemyinfo.add_widget(self.enemyPanel_numEnemies)
        self.enemyPanel_enemyinfo.add_widget(self.enemyPanel_enemyHealth)
        self.enemyPanel_enemyinfo.add_widget(self.enemyPanel_enemySpeed)
        self.enemyPanel_enemyinfo.add_widget(self.enemyPanel_enemyArmor)
        self.enemyPanel_enemyinfo.add_widget(self.enemyPanel_enemyReward)
        self.enemyPanel_enemyinfo.add_widget(self.enemyPanel_disclaimer)
        self.panelLayout.add_widget(self.enemyPanel_header)
        self.panelLayout.add_widget(self.enemyPanel_enemyinfo)
        return self.panelLayout


class Bar(GUI_Base.SmartMenu):
    def __init__(self, **kwargs):
        super(Bar, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='horizontal')
        self.layout.pos = self.pos
        self.layout.size = self.size
        self.add_widget(self.layout)
    # def addButtons(self, buttonList):
    #     for button in buttonList:
    #         tmpbtn = MyButton(text=button)
    #         # tmpbtn.background_color = [1,1,1,1]
    #         # tmpbtn.bind(on_release=self.callback)
    #         self.layout.add_widget(tmpbtn)
    #
    # def addElements(self, elementList):
    #     # likely need to create individual widgets to update later.
    #     for element, var, icon in elementList:
    #         box = GridLayout(cols=3, col_force_default=True, row_force_default=True, row_default_height=50,
    #                          col_default_width=55)
    #         label = MyLabel(text=element)
    #         element = StringProperty()
    #         variable = MyLabel(text=str(var))
    #         variable.id = element
    #         icon = Utilities.imgLoad(icon)
    #         icon.size_hint_x = None
    #         icon.size = (Map.mapvar.squsize, Map.mapvar.squsize)
    #         label.size_hint_x = None
    #         label.size = (Map.mapvar.squsize + Map.mapvar.squsize * .3, Map.mapvar.squsize + Map.mapvar.squsize * .6)
    #         # nlabel.valign='center'
    #         variable.size_hint_x = None
    #         variable.size = (3 * Map.mapvar.squsize, Map.mapvar.squsize + Map.mapvar.squsize * .6)
    #         box.add_widget(icon)
    #         box.add_widget(label)
    #         box.add_widget(variable)
    #         gui.topBar_Boxlist.append(box)
    #         self.layout.add_widget(box)

            # with tmplbl.canvas:
            #    Color(.4, .4, .4, .8)
            #    self.rect=Rectangle(size=tmplbl.size, pos=tmplbl.pos)

class topBarWidget():
    def __init__(self, label, var, source, icon):
        self.Box = StackLayout(orientation="lr-tb")
        self.Label = GUI_Base.MyLabel(text=label)

        self.Variable = GUI_Base.MyLabel(text=str(source), halign='right')
        GUI.gui.myDispatcher.fbind(var, self.set_value, var)
        self.Icon = Utilities.imgLoad(icon)
        self.Icon.size_hint = (None,1)
        self.Icon.width = Map.mapvar.squsize*1.5
        self.Box.add_widget(self.Icon)
        if label != ' ':
            self.Label.size_hint = (None,1)
            self.Label.width = Map.mapvar.squsize * 2
            self.Box.add_widget(self.Label)
        self.Variable.size_hint = (None,1)
        self.Variable.width = Map.mapvar.squsize * 1.3
        self.Box.add_widget(self.Variable)
        GUI.gui.topBar_Boxlist.append(self.Box)
        GUI.gui.topBar.layout.add_widget(self.Box)

    def set_value(self, *args):
        self.Variable.text = args[2]

