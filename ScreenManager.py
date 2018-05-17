from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import NumericProperty, ObjectProperty
from kivy.core.window import Window
from kivy.uix.label import Label

import __main__
import Player #in use
import Map
import InfoPanel

Builder.load_string("""
#:import Player Player
#:import Map Map
#:import InfoPanel InfoPanel
#:import sys sys

<MenuScreen>:
    GridLayout
        id: mainmenu
        rows: 4
        size: self.parent.size
        pos: 0,0
        spacing: self.width/100
        padding: self.width/100
        canvas:
            Color:
                rgba: 1,1,1,1
            Rectangle:
                size: self.size
                pos: self.pos
        Image
            source: "backgroundimgs/ttdlogo.png"
            size_hint: 1, .4
        
        GridLayout
            id: buttonlayout
            cols:3
            size_hint: 1, .4
            BoxLayout
                id:gameplaybuttons
                orientation: 'vertical'
                spacing: self.parent.height/50
                Button
                    id:startbutton
                    text:"Play"
                    on_release: app.root.change_screens('game')
                Button
                    id:quitbutton
                    text:"Quit"
                    on_release: app.stop();sys.exit()
            StackLayout
                orientation: 'tb-lr'
                padding: 10
                spacing: 10
                GridLayout
                    id: configlayout
                    cols:3
                    size_hint: 1, .8
                    StackLayout
                        id:pathlayout
                        orientation: 'tb-lr'
                        spacing:6
                        padding:3
                        Label
                            text:"Number of Paths:"
                            size_hint: 1, .1
                        ToggleButton
                            id:onepath
                            size_hint: 1, .3
                            text:"One"
                            state:'down' if Map.mapvar.numpaths == 1 else 'normal'
                            group:'path'
                            on_release: Map.mapvar.numpaths = 1
                        ToggleButton
                            id:twopath
                            size_hint: 1, .3
                            text: "Two"
                            state:'down' if Map.mapvar.numpaths == 2 else 'normal'
                            group:'path'
                            on_release: Map.mapvar.numpaths = 2
                            background_down: "GUI/yellow_outline.png"
                        ToggleButton
                            id:threepath
                            size_hint: 1, .3
                            text:"Three"
                            state:'down' if Map.mapvar.numpaths == 3 else 'normal'
                            group:'path'
                            on_release: Map.mapvar.numpaths = 3
                            background_down: "GUI/red_outline.png"
                    StackLayout
                        id:difficultylayout
                        orientation: 'tb-lr'
                        spacing:6
                        padding:3
                        Label:
                            text:"Difficulty:"
                            size_hint: 1, .1
                        ToggleButton
                            id:easy
                            size_hint: 1, .3
                            text:"Easy"
                            state:'down' if Map.mapvar.difficulty == 'easy' else 'normal'
                            group:'difficulty'
                            on_release: Map.mapvar.difficulty = 'easy'
                        ToggleButton
                            id:medium
                            text: "Medium"
                            state:'down' if Map.mapvar.difficulty == 'medium' else 'normal'
                            size_hint: 1, .3
                            group:'difficulty'
                            on_release: Map.mapvar.difficulty = 'medium'
                            background_down: "GUI/yellow_outline.png"
                        ToggleButton
                            id:hard
                            size_hint: 1, .3
                            text:"Hard"
                            state:'down' if Map.mapvar.difficulty == 'hard' else 'normal'
                            group:'difficulty'
                            on_release: Map.mapvar.difficulty = 'hard'
                            background_down: "GUI/red_outline.png"
                    StackLayout
                        id:enemyorderlayout
                        orientation: 'tb-lr'
                        spacing:6
                        padding:3
                        Label
                            text:"Enemy Order:"
                            size_hint: 1, .1
                        ToggleButton
                            id:standardorder
                            size_hint: 1, .45
                            text:"Standard"
                            state:'down' if Map.mapvar.waveOrder == 'standard' else 'normal'
                            group:'enemyorder'
                            on_release: Map.mapvar.waveOrder = 'standard'
                        ToggleButton
                            id:randomorder
                            size_hint: 1, .45
                            text: "Random"
                            state:'down' if Map.mapvar.waveOrder == 'random' else 'normal'
                            group:'enemyorder'
                            on_release: Map.mapvar.waveOrder = 'random'
                            background_down: "GUI/red_outline.png"
                Button
                    id:restartbutton
                    size_hint: 1, .2
                    text:"Restart Game"
                    disabled: True
                    opacity: 0
                    background_normal: 'GUI/red_button_normal.png'
                    background_down: 'GUI/red_button_down.png'
                    on_release: MainFunctions.resetGame(); app.root.change_screens('game')
        BoxLayout
            size_hint: .3,.1
            orientation:"horizontal"
            spacing: root.width/50
            Label
                text: "Sounds"
                size_hint: .125, 1
                font_size: root.width*.015
            Switch
                id: sound
                size_hint: .125, 1
                active: True if Player.player.soundOn else False
                on_active: Player.player.sound.on_sound(self, self.active)
            Label
                text: "Music"
                size_hint: .125, 1
                font_size: root.width*.015
            Switch
                id: music
                size_hint: .125, 1
                active: True if Player.player.musicOn else False
                on_active: Player.player.sound.on_music(self,self.active)
            Button
                text: "Statistics"
                size_hint: .25, 1
                on_release: root.manager.current = 'statistics'
                Image
                    pos: self.parent.x - 20, self.parent.y + 10
                    source: 'iconimgs/stack.png'
                    size: root.width * .08, root.height * .05
            Button
                text: "Game Info"
                size_hint: .25, 1
                on_release: root.manager.current = 'info'
                Image
                    pos: self.parent.x - 20, self.parent.y - 20
                    source: 'iconimgs/info.png'
        Label
            size_hint: 1, .2
            markup: True
            text: 'On the web at tablettowerdefense.com and Twitter: @Tablettowerdef.  Property of Scott Rossignol. Thanks to EmojiOne for providing free emoji icons: https://www.emojione.com. This game runs on the Kivy framework. Music by Adam Cook. The Wave Change sound is by Jobro https://freesound.org/people/jobro/.'
            text_size: root.width*.8, None
            halign: 'center'
            valign: 'center'
            font_size: root.width*.01
            
            
<StatsLabel@Label>
    size_hint: 1, .06
    font_size: self.width * .05
    text_size: self.size
    halign: 'left'

<StatsHeader@Label>
    size_hint: 1,.1
    font_size: self.width * .11
    text_size: self.size

<StatisticsScreen>:
    StackLayout
        size_hint: 1,1
        spacing: self.width/50
        padding: self.width/25
        canvas:
            Color:
                rgba: .7,.7,.7,1
            Rectangle:
                size: self.size
                pos: self.pos
        Label
            size_hint: 1, .1
            text: "Player Statistics"
            font_size: root.width * .025
        GridLayout
            cols: 3
            size_hint: 1, .9
            BoxLayout:
                orientation: "vertical"
                StatsHeader
                    text: "Last Game"
                StatsLabel
                    text: "# Enemies: " + str(Player.player.analytics.numEnemies)
                StatsLabel
                    text: "Damage: " + str(Player.player.analytics.gameDamage)
                StatsLabel
                    text: "Towers Bought: " + str(Player.player.analytics.towersBought)
                StatsLabel
                    text: "Towers Sold: " + str(Player.player.analytics.towersSold)
                StatsLabel
                    text: "Upgrades: " + str(Player.player.analytics.towerUpgrades)
                StatsLabel
                    text: "Max Tower Level: " + str(Player.player.analytics.maxTowerLevel)
                StatsLabel
                    text: "Money Earned: " + str(Player.player.analytics.moneyEarned)
                StatsLabel
                    text: "Money Spent: " + str(Player.player.analytics.moneySpent)
                StatsLabel
                    text: "Game Length: " + str(int(Player.player.analytics.gameLength[0])) + ":" + str(int(Player.player.analytics.gameLength[1]))
                StatsLabel
                    text: "Score: " + str(Player.player.analytics.score)
                                       
            BoxLayout
                orientation: "vertical"
                StatsHeader
                    text: "Totals"
                StatsLabel
                    text: "Total Enemies: " + str(Player.player.analytics.totalEnemies)
                StatsLabel
                    text: "Total Damage: " + str(Player.player.analytics.totalDamage)
                StatsLabel
                    text: "Total Towers Bought: " + str(Player.player.analytics.totalBought)
                StatsLabel
                    text: "Total Towers Sold: " + str(Player.player.analytics.totalSold)
                StatsLabel
                    text: "Total Towers Upgraded: " + str(Player.player.analytics.totalUpgraded)
                StatsLabel
                    text: "Highest Tower Level: " + str(Player.player.analytics.highestTowerLevel)
                StatsLabel
                    text: "Total Money Earned: " + str(Player.player.analytics.totalEarned)
                StatsLabel
                    text: "Total Money Spent: " + str(Player.player.analytics.totalSpent)
                StatsLabel
                    text: "Total Time Played: " + str(Player.player.analytics.timePlayed['hours']) + ":" + str(Player.player.analytics.timePlayed['minutes'])+ ":" + str(Player.player.analytics.timePlayed['seconds'])
                StatsLabel
                    text: "Total Games Played: " + str(Player.player.analytics.totalGames)
                    
            BoxLayout
                orientation: "vertical"
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
                    
            
<InfoScreen>:
    GridLayout
        id: mainmenu
        rows: 1
        size: self.parent.size
        pos: 0,0
        spacing: self.width/100
        padding: self.width/100
        canvas:
            Color:
                rgba: .7,.7,.7,1
            Rectangle:
                size: self.size
                pos: self.pos    
        InfoPanel
            id:infopanel
""")

class MenuScreen(Screen):
    pass

class StatisticsScreen(Screen):
    pass

class InfoScreen(Screen):
    def __init__(self, **kwargs):
        super(InfoScreen, self).__init__(**kwargs)
        self.ids.infopanel.createContent()

class GameScreen(Screen):
    pass

class GameScreenManager(ScreenManager):

    def __init__(self,**kwargs):
        super(GameScreenManager, self).__init__(**kwargs)
        self.size = Window.size
        self.add_widget(MenuScreen(name = 'mainmenu'))
        self.add_widget(StatisticsScreen(name='statistics'))
        self.add_widget(InfoScreen(name='info'))
        self.current = 'mainmenu'




