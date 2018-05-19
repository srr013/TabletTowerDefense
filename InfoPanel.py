import os

from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelHeader, TabbedPanelItem
from kivy.lang import Builder
from kivy.uix.label import Label

import Player
import Enemy
import Localdefs
import FireTower
import LifeTower
import IceTower
import GravityTower
import WindTower

Builder.load_string("""
#:import Map Map
<EnemyPanelItem>
    GridLayout
        rows: 1
        cols: 2
        size_hint: 1,1
        pos: 0,0
        padding: 100
        spacing: 10
        canvas:
            Color:
                rgba: .6,.6,.6,1
            RoundedRectangle:
                size: self.size
                pos: self.pos
                radius: 100,100,100,100
        BoxLayout
            orientation: "vertical"
            BoxLayout
                orientation:"vertical"
                Label
                    id:enemyheader
                    color: 1,1,1,1
                    font_size: self.parent.width * .07
                Label
                    id:wavenum
                    color: 1,1,1,1
                    font_size: self.parent.width * .03
                    text_size:self.size
            Label
                id:enemynumber
                color: 1,1,1,1
                font_size: self.parent.width * .05
                text_size:self.size
            Label
                id:enemyhealth
                color: 1,1,1,1
                font_size: self.parent.width * .05
                text_size:self.size
            Label
                id:enemyspeed
                color: 1,1,1,1
                font_size: self.parent.width * .05
                text_size:self.size
            Label
                id:enemyarmor
                color: 1,1,1,1
                font_size: self.parent.width * .05
                text_size:self.size
            Label
                id:enemyreward
                color: 1,1,1,1
                font_size: self.parent.width * .05
                text_size:self.size
        BoxLayout
            orientation: 'vertical'
            spacing: 50
            padding: 50
            Image
                id: enemyimage
            Button
                text: "Go to Main Menu"
                on_release: app.root.change_screens('mainmenu')
            Button
                text: "Go to Game"
                on_release: app.root.change_screens('game')

<TowerPanelItem>
    StackLayout
        orientation:'tb-lr'
        padding:75
        canvas:
            Color:
                rgba: .6,.6,.6,1
            RoundedRectangle:
                size: self.size
                pos: self.pos
                radius: 100,100,100,100
        Label
            color: 1,1,1,1
            id:towerheader
            font_size: self.parent.width * .05
            size_hint: 1,.15
        GridLayout
            cols: 3
            size_hint: 1, .85
            spacing: 10
            padding: 10
            StackLayout
                orientation:"tb-lr"
                Label
                    color: 1,1,1,1
                    text: "Leader Path"
                    font_size: self.parent.width * .08
                    size_hint: 1, .2

                Image
                    source: "towerimgs/crown.png"
                    size_hint: 1, .1
                Label
                    size_hint: 1, .7
                    color: 1,1,1,1
                    text: "Grants all other connected towers a bonus to all stats, but this tower loses the ability to attack. You may only build one leader per Tower Group. A Tower Group is a set of connected towers of the same type."
                    font_size: self.parent.width * .06
                    halign: 'center'
                    valign: 'center'
                    text_size:self.size
            StackLayout
                orientation:"tb-lr"
                spacing: 10
                Label
                    color: 1,1,1,1
                    text: "Damage Path"
                    font_size: self.parent.width * .07
                    size_hint: 1, .2
                Image
                    id: path2image
                    size_hint: 1, .1
                Label
                    id:path2description
                    color: 1,1,1,1
                    font_size: self.parent.width * .05
                    size_hint: 1, .35
                    text_size:self.size
                StackLayout
                    id:path2data
                    orientation:"tb-lr"
                    size_hint: 1,.35
            BoxLayout
                orientation: 'vertical'
                spacing: 20
                Image
                    id: towerimage
                Button
                    text: "Go to Main Menu"
                    on_release: app.root.change_screens('mainmenu')
                Button
                    text: "Go to Game"
                    on_release: app.root.change_screens('game')
<DataLayoutLabel>
    text_size: self.width, None

<GeneralInfoLabel>
    size_hint: 1, None
    text_size: self.width, None
    height: self.texture_size[1]
    markup: True
    halign: 'left'

<InfoPanel>:
    id: infopanel
    background_color: .1,.1,.1,.8
    border: 1,1,1,1
    do_default_tab: False
    tab_width: self.width * .07
    tab_height: self.height * .08
    TabbedPanelItem
        text: "General"
        id: generalinfo
        StackLayout:
            orientation: "tb-lr"
            padding: 75
            spacing: 10
            canvas:
                Color:
                    rgba: .6,.6,.6,1
                RoundedRectangle:
                    size: self.size
                    pos: self.pos
                    radius: 100,100,100,100
            Label
                color: 1,1,1,1
                text: "General Info"
                font_size: self.parent.width * .07
                size_hint: 1,.1
            GridLayout
                cols: 2
                size_hint: 1, .9
                spacing: 10
                padding: 10
                StackLayout
                    size_hint: .5, 1
                    orientation:"tb-lr"
                    spacing: 5
                    id:panel1
                StackLayout
                    size_hint: .5, 1
                    orientation:"tb-lr"
                    id:panel2
                    BoxLayout
                        orientation: 'vertical'
                        spacing: 50
                        padding: 50
                        Image
                            source: "backgroundimgs/Base.png"
                        Button
                            text: "Go to Main Menu"
                            on_release: app.root.change_screens('mainmenu')
                        Button
                            text: "Go to Game"
                            on_release: app.root.change_screens('game')
""")
class EnemyPanelItem(TabbedPanelItem):
    pass
class TowerPanelItem(TabbedPanelItem):
    pass
class DataLayoutLabel(Label):
    pass
class GeneralInfoLabel(Label):
    pass

class InfoPanel(TabbedPanel):
    def createContent(self):
        self.towertypelist = ['Life', 'Fire', 'Gravity', 'Ice', 'Wind']
        self.enemytypelist = ['Standard', 'Airborn', 'Splinter', 'Strong', 'Crowd']
        wavemod = (1 + (Player.player.wavenum / 70.0))

        for i in Localdefs.towerAttributes:
            lbl = GeneralInfoLabel(text=i, color=(1,1,1,1))
            self.ids.panel1.add_widget(lbl)
            lbl.text_size = (self.parent.width, None)
        for i in Localdefs.towerAttackTypes:
            lbl = GeneralInfoLabel(text=i, color=(1,1,1,1))
            self.ids.panel1.add_widget(lbl)

        for enemy in self.enemytypelist:
            th = EnemyPanelItem()
            th.id = enemy
            self.add_widget(th)
            th.color = [0, 0, 0, 1]
            th.text = "Enemy: " +enemy
            th.text_size = th.size
            th.ids.enemyimage.source = "enemyimgs/"+enemy+".png"
            th.ids.wavenum.text = "Information reflects enemy statistics at wave number: " + str(Player.player.wavenum)
            th.ids.enemyheader.text = enemy
            th.ids.enemynumber.text = "Number: " + str(int(eval("Enemy." + enemy + ".defaultNum") * wavemod))
            th.ids.enemyhealth.text = "HP: " + str(int(eval("Enemy." + enemy + ".health") * wavemod))
            th.ids.enemyspeed.text = "Speed: " + str(int(eval("Enemy." + enemy + ".speed") * wavemod))
            th.ids.enemyarmor.text = "Armor: " + str(int(eval("Enemy." + enemy + ".armor") * wavemod))
            th.ids.enemyreward.text = "Reward: " + str(int(eval("Enemy." + enemy + ".reward") * wavemod))

        for tower in self.towertypelist:
            th = TowerPanelItem()
            th.id = tower
            self.add_widget(th)
            th.color = [0, 0, 0, 1]
            th.text = "Tower: " + tower
            th.text_size = th.size
            th.ids.towerimage.source = os.path.join("towerimgs",tower,"1.png")
            th.ids.towerheader.text = tower + "Tower"
            th.ids.path2image.source = eval(tower + "Tower." + tower + "Tower.imagestr")
            th.ids.path2description.text = eval(tower + "Tower." + tower + "Tower.upgradeDescription")
            stats = eval(tower + "Tower." + tower + "Tower.upgradeStats")
            for i in stats:
                lbl = DataLayoutLabel(text=i, size_hint = (1, .5), color= (1,1,1,1))
                lbl.text_size = (lbl.width, lbl.height)
                th.ids.path2data.add_widget(lbl)

    def updateContent(self):
        self.clear_widgets()
        self.createContent()

    def getDefaultTab(self, *args):
        if Player.player.towerSelected:
            tower = Player.player.towerSelected.type
            for tab in self.tab_list:
                if tab.id == tower:
                    return tab
        else:
            return self.tab_list[-1]

class InfoPanelHeader(TabbedPanelHeader):
    def __init__(self, **kwargs):
        super(InfoPanelHeader, self).__init__(**kwargs)
        self.color = [0, 0, 0, 1]
        self.size_hint = (1,1)
        self.pos = (0,0)


    # def createTowerPanelContent(self, tower):
    #     self.towerPanel_header = Label(text=str(tower)+" Tower Upgrades", width=self.width - Map.mapvar.squsize,
    #                                    height=Map.mapvar.squsize * 1.3, size_hint=(None, None), font_size=__main__.Window.size[0]*.016,
    #                                    text_size=(Map.mapvar.squsize * 7, Map.mapvar.squsize * 1.3), halign='center')
    #     self.towerPanel_towerinfo = GridLayout(cols=2)
    #
    #     path1 = StackLayout(orientation='lr-tb', size_hint=(.5,1))
    #     path1title = Label(text = "Leader", size_hint= (1,.1), font_size = __main__.Window.size[0]*.013)
    #     path1image = Image(source = "towerimgs/crown.png", size_hint = (1,.1))
    #     path1desc = Label(text = "Grants all other connected towers a bonus to all stats, but this tower loses the ability to attack."
    #                              "You may only build one leader per Tower Group. A Tower Group is a set of connected towers of the same type.",
    #                       size_hint = (1,.43), valign = 'center', halign = 'left')
    #     path1desc.text_size = (self.width/2.5, self.height)
    #     path1.add_widget(path1title)
    #     path1.add_widget(path1image)
    #     path1.add_widget(path1desc)
    #     self.towerPanel_towerinfo.add_widget(path1)
    #
    #     path2 = StackLayout(orientation='lr-tb', size_hint = (.45,1))
    #     path2title = Label(text=eval(tower+"Tower."+tower+"Tower."+"upgradeName"), size_hint=(1, .1), font_size=__main__.Window.size[0] * .013)
    #     path2image = Image(source=eval(tower+"Tower."+tower+"Tower.imagestr"), size_hint=(1, .1))
    #     path2desc = Label(text=eval(tower+"Tower."+tower+"Tower.upgradeDescription"),
    #                       size_hint = (1,.4), valign = 'center', halign = 'left')
    #     path2desc.text_size = (self.width/2.5, self.height)
    #     path2.add_widget(path2title)
    #     path2.add_widget(path2image)
    #     path2.add_widget(path2desc)
    #     path2data = GridLayout(cols=1, size_hint = (1, .3), spacing = 0)
    #     for i in eval(tower+"Tower."+tower+"Tower.upgradeStats"):
    #         lbl = Label(text=i, size_hint=(1, None), halign='left')
    #         lbl.height = lbl.text_size[1]
    #         lbl.text_size = (self.width / 2.5, lbl.height)
    #         path2data.add_widget(lbl)
    #     path2.add_widget(path2data)
    #     self.towerPanel_towerinfo.add_widget(path2)
    #     self.panelLayout.add_widget(self.towerPanel_header)
    #     self.panelLayout.add_widget(self.towerPanel_towerinfo)
    #     return self.panelLayout

    # def createEnemyPanelContent(self, enemy):
    #     waveNum = Player.player.wavenum
    #     self.enemyPanel_header = Label(text=str(enemy), size_hint=(1, .2), font_size=__main__.Window.size[0]*.022,
    #                                    halign='center')
    #     self.enemyPanel_enemyinfo = GridLayout(cols=1, col_force_default=True, row_force_default=True,
    #                                            row_default_height=Map.mapvar.squsize, col_default_width=self.width,
    #                                            size_hint=(1, .8))
    #     self.enemyPanel_numEnemies = Label(
    #         text="Number: " + str(int(eval("Enemy." + enemy + ".defaultNum") * (1 + (waveNum / 70.0)))), font_size=__main__.Window.size[0]*.015,
    #         text_size=(Map.mapvar.squsize * 7, Map.mapvar.squsize))
    #     self.enemyPanel_enemyHealth = Label(
    #         text="HP: " + str(int(eval("Enemy." + enemy + ".health") * (1 + (waveNum / 70.0)))), font_size=__main__.Window.size[0]*.015,
    #         text_size=(Map.mapvar.squsize * 7, Map.mapvar.squsize))
    #     self.enemyPanel_enemySpeed = Label(
    #         text="Speed: " + str(int(eval("Enemy." + enemy + ".speed") * (1 + (waveNum / 70.0)))), font_size=__main__.Window.size[0]*.015,
    #         text_size=(Map.mapvar.squsize * 7, Map.mapvar.squsize))
    #     self.enemyPanel_enemyArmor = Label(
    #         text="Armor: " + str(int(eval("Enemy." + enemy + ".armor") * (1 + (waveNum / 70.0)))), font_size=__main__.Window.size[0]*.015,
    #         text_size=(Map.mapvar.squsize * 7, Map.mapvar.squsize))
    #     self.enemyPanel_enemyReward = Label(
    #         text="Reward: " + str(int(eval("Enemy." + enemy + ".reward") * (1 + (waveNum / 70.0)))), font_size=__main__.Window.size[0]*.015,
    #         text_size=(Map.mapvar.squsize * 7, Map.mapvar.squsize))
    #     self.enemyPanel_disclaimer = Label(text="Numbers reflect enemy if sent next wave", font_size=__main__.Window.size[0]*.008,
    #                                        text_size=(Map.mapvar.squsize * 9, Map.mapvar.squsize))
    #     self.enemyPanel_enemyinfo.add_widget(self.enemyPanel_numEnemies)
    #     self.enemyPanel_enemyinfo.add_widget(self.enemyPanel_enemyHealth)
    #     self.enemyPanel_enemyinfo.add_widget(self.enemyPanel_enemySpeed)
    #     self.enemyPanel_enemyinfo.add_widget(self.enemyPanel_enemyArmor)
    #     self.enemyPanel_enemyinfo.add_widget(self.enemyPanel_enemyReward)
    #     self.enemyPanel_enemyinfo.add_widget(self.enemyPanel_disclaimer)
    #     self.panelLayout.add_widget(self.enemyPanel_header)
    #     self.panelLayout.add_widget(self.enemyPanel_enemyinfo)
    #     return self.panelLayout

