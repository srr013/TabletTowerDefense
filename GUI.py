import thorpy
import localdefs
import os
import EventFunctions
import pygame
import localclasses
import TowerAbilities
import math

class GUI:
    def __init__(self, player):
        self.player = player
        self.boxes = list()
        self.popUp_group = thorpy.make_group([])
        self.popUp_displayed = None
        self.bottomBar = None
        self.topBar = None
        self.rightPanel = None
        self.last_selected = None

    def mainMenu(self):
        self.player.gameover = True

    def towerSelected(self,**kwargs):
        localdefs.player.towerSelected = kwargs['tower']


    def nextWave(self):
        localdefs.player.next_wave = True

    #currently game cannot be unpaused by a button because the menus are not updated during pause while loop.
    def pauseGame(self):
        self.player.paused = False if self.player.paused==True else True

    def restartGame(self):
        self.player.restart = True



    def createTopBar(self,timer):
        self.home_button = thorpy.make_button("Quit (esc)",func = self.mainMenu)
        self.pause_button = thorpy.make_button("Pause (space)", func = self.pauseGame)
        self.restart_button = thorpy.make_button("Restart", func = self.restartGame)#not yet working. Sets player.restart to True
        self.button_group = thorpy.make_group([self.home_button, self.pause_button, self.restart_button])

        pause_reaction = thorpy.Reaction(reacts_to=thorpy.constants.EVENT_UNPRESS,
                                          reac_func=self.pauseGame,
                                          reac_name="unpause")
        self.pause_button.add_reaction(pause_reaction)

        self.wavenum = thorpy.make_text(text="Wave: %d" %(self.player.wavenum),font_size = thorpy.style.FONT_SIZE+3, font_color=thorpy.style.FONT_COLOR)
        self.timer = thorpy.make_text(text="Next Wave: %d  " % (timer), font_size = thorpy.style.FONT_SIZE+3, font_color=thorpy.style.FONT_COLOR)
        self.total_score = thorpy.make_text(text="Score: %d + %d" % (self.player.kill_score, self.player.bonus_score), font_size = thorpy.style.FONT_SIZE+3, font_color=thorpy.style.FONT_COLOR)

        self.health_image = thorpy.Image.make(os.path.join("backgroundimgs","heart24x24.png"), colorkey=(0,0,0,0))
        self.health = thorpy.make_text(text="Health: %d" % (self.player.health),font_size = thorpy.style.FONT_SIZE+3, font_color=thorpy.style.FONT_COLOR)
        ##standard pygame heart image
        #heartimg = localdefs.imgLoad("backgroundimgs/heart24x24.png")
        #heartrect = heartimg.get_rect(center=(200, 200))
        self.health_group = thorpy.make_group([self.health_image, self.health])
        for element in self.health_group.get_elements():
            element.surface = self.player.screen
        self.coin_image = thorpy.Image.make(os.path.join("backgroundimgs","coin20x24.png"), colorkey=(0,0,0,0))
        self.money = thorpy.make_text(text="Money: %d" % (self.player.money),font_size = thorpy.style.FONT_SIZE+3, font_color=thorpy.style.FONT_COLOR)
        self.money_group = thorpy.make_group([self.coin_image, self.money])
        for element in self.money_group.get_elements():
            element.surface = self.player.screen

        ghost_group = thorpy.make_group([self.button_group,self.wavenum,self.money_group,self.timer,self.health_group,self.total_score])
        for element in ghost_group.get_elements():
            element.surface = self.player.screen

        thorpy.store(ghost_group,mode="h",gap = 110)

        #add all the elements into the topbar
        if self.topBar == None:
            self.topBar = thorpy.Box.make([ghost_group], (localdefs.winwid, 35))
            self.boxes.append(self.topBar)

    def updateGui(self,timer):
        self.wavenum.set_text(text="Wave: %d" %(self.player.wavenum))
        self.money.set_text(text="Money: %d" % self.player.money)
        self.timer.set_text(text="Next Wave: %d  " % timer)
        self.health.set_text(text="Health: %d" % self.player.health)
        self.total_score.set_text(text="Score: %d + %d" % (self.player.kill_score, self.player.bonus_score))

    def createBottomBar(self):
        tower_list = list()
        for tower in localdefs.iconlist:
            button = thorpy.make_button("%s \n$%d" %(tower.type,tower.basecost), func= self.towerSelected, params={'tower':tower})
            button.surface = self.player.screen
            button.set_size((70,60))
            button.set_image(tower.img)
            tower_list.append(button)
        ghost_group = thorpy.make_group(tower_list)
        thorpy.store(ghost_group,mode="h",gap=50, margin=200)

        self.send_wave = thorpy.make_button("Send Wave (n)", func=self.nextWave)
        self.game_speed = thorpy.SliderX.make(length=30, limvals=(1, 10), text="Game Speed", initial_value=localdefs.player.game_speed, type_=int)
        button_group = thorpy.make_group([self.send_wave, self.game_speed])
        thorpy.store(button_group,gap=20,mode='h',margin=-localdefs.winwid/5)

        # add all the elements into the bar
        if self.bottomBar == None:
            self.bottomBar = thorpy.Box.make([ghost_group,button_group], (localdefs.winwid,55))
            thorpy.store(self.bottomBar,mode='h')
            self.bottomBar.set_topleft((0,localdefs.winhei-55))
            self.boxes.append(self.bottomBar)

    def createTowerButtons(self,tower):
        abilitylist = [i for i in TowerAbilities.TowerAbilityList if
                       (i.doesFit(tower) and (i.shortname in localdefs.player.modDict['towerAbilities']))]
        buttonlist = thorpy.make_group([])
        buttonnum = len(TowerAbilities.TowerAbilityList)
        radius =70
        inddeg = (2.0 * math.pi) / buttonnum
        for ind, towerability in enumerate(abilitylist):
            buttonpos = pygame.Rect((0, 0), (localdefs.squsize, localdefs.squsize))
            buttonpos.center = tower.rect.center
            buttonpos.move_ip(radius * math.cos((ind + 1) * inddeg), radius * math.sin((ind + 1) * inddeg))
            button = thorpy.make_button("%s" % abilitylist[0],func=towerability.apply, params={'tower':tower})
            button.surface = self.player.screen
            button.set_size((localdefs.squsize,localdefs.squsize))
            button.set_topleft(buttonpos.topleft)
            try:
                buttonimg = localdefs.imgLoad(os.path.join("upgradeicons", towerability.shortname + ".jpg"))
            except:
                buttonimg = pygame.Surface((20, 20))
                buttonimg.fill((90, 90, 255))
            button.set_image(buttonimg)
            buttonlist.add_elements([button])
        return buttonlist

    def showTowerButtons(self, tower):
        if self.popUp_displayed == None:
            self.popUp_displayed = tower
            self.boxes.append(tower.buttons)
        if self.popUp_displayed != tower and self.popUp_displayed !=None:
            self.boxes.pop()
            self.popUp_displayed = tower
            self.boxes.append(tower.buttons)

    def hidePopUp(self, tower):
        if self.popUp_displayed != tower and self.popUp_displayed != None:
            self.popUp_displayed = None
            self.boxes.pop()


    def createRightPanel(self):

        panelwid = 230
        topbarhei = self.topBar.get_rect()[3]
        bottombarhei = self.bottomBar.get_rect()[3]
        padding = 5
        panelhei = (localdefs.winhei - topbarhei - bottombarhei-padding*3)/2
        FONT_COLOR = (0, 0, 0)
        STANDARD_FONT_SIZE = 18

        #Top right panel displays info about what's selected on the screen (tower or Icon)
        self.topPanel_titleText = thorpy.make_text(text="", font_size=36, font_color = FONT_COLOR)
        self.topPanel_towerImg = thorpy.Image.make(color=(0,0,0,0))
        self.topPanel_towerImg.set_size((60,60))
        self.topPanel_towerDamage = thorpy.make_text(text="", font_size=STANDARD_FONT_SIZE, font_color=FONT_COLOR)
        self.topPanel_towerReload = thorpy.make_text(text="", font_size=STANDARD_FONT_SIZE, font_color=FONT_COLOR)
        self.topPanel_towerAbilityDesc = thorpy.make_text(text="", font_size=STANDARD_FONT_SIZE, font_color=FONT_COLOR)
        self.topPanel_towerAbilityStats = thorpy.make_text(text="", font_size=STANDARD_FONT_SIZE, font_color=FONT_COLOR)
        self.topPanel_separator = thorpy.make_text(text="")#multiple somehow by panel wid instead?
        self.topPanel_towerUpgDamage = thorpy.make_text(text="", font_size=STANDARD_FONT_SIZE, font_color=FONT_COLOR)
        self.topPanel_towerUpgReload = thorpy.make_text(text="", font_size=STANDARD_FONT_SIZE, font_color=FONT_COLOR)
        self.topPanel_towerUpgAbilityStats = thorpy.make_text(text="", font_size=STANDARD_FONT_SIZE, font_color=FONT_COLOR)

        self.topPanel_titleandimage = thorpy.make_group([self.topPanel_titleText, self.topPanel_towerImg],mode='v')
        self.topPanel_towerstats = thorpy.make_group([self.topPanel_towerDamage, self.topPanel_towerReload,
            self.topPanel_towerAbilityDesc, self.topPanel_towerAbilityStats, self.topPanel_separator,
            self.topPanel_towerUpgDamage, self.topPanel_towerUpgReload, self.topPanel_towerUpgAbilityStats],mode='v')

        self.rightTopPanel = thorpy.Box.make([self.topPanel_titleandimage, self.topPanel_towerstats],(panelwid, panelhei))
        thorpy.store(self.rightTopPanel, align='center')
        self.rightTopPanel.set_topleft((localdefs.winwid-panelwid,topbarhei+padding))
        #self.rightPanel.set_main_color((255,255,255,100))
        self.boxes.append(self.rightTopPanel)

        #Bottom right panel displays info about the current enemy and upcoming enemies
        self.botPanel_titleText = thorpy.make_text(text="Enemy", font_size=18, font_color = FONT_COLOR)
        self.botPanel_enemyImg = thorpy.Image.make(color=(0,0,0,0))
        self.botPanel_enemyImg.set_size((60,60))
        self.botPanel_enemyHealth = thorpy.make_text(text="", font_size=STANDARD_FONT_SIZE, font_color=FONT_COLOR)
        self.botPanel_enemySpeed = thorpy.make_text(text="", font_size=STANDARD_FONT_SIZE, font_color=FONT_COLOR)
        self.botPanel_enemyAbilityDesc = thorpy.make_text(text="", font_size=STANDARD_FONT_SIZE, font_color=FONT_COLOR)
        self.botPanel_futureWaves = thorpy.make_text(text="Upcoming Waves: ", font_size=STANDARD_FONT_SIZE, font_color=FONT_COLOR)


        self.botPanel_titleandimage = thorpy.make_group([self.botPanel_titleText, self.botPanel_enemyImg], mode='v')
        self.botPanel_enemystats = thorpy.make_group([self.botPanel_enemyHealth,self.botPanel_enemySpeed,
                                                      self.botPanel_enemyAbilityDesc, self.botPanel_futureWaves], mode='v')
        self.rightBotPanel = thorpy.Box.make([self.botPanel_titleandimage, self.botPanel_enemystats], (panelwid,panelhei))
        thorpy.store(self.rightBotPanel, align='center')
        self.rightBotPanel.set_topleft(((localdefs.winwid-panelwid,topbarhei+panelhei+padding*2)))
        self.boxes.append(self.rightBotPanel)

    def updatePanel(self):

        #update the top panel if what's selected has changed
        if self.player.towerSelected != None and self.last_selected != self.player.towerSelected:
            self.topPanel_titleText.set_text(text="{}".format(self.player.towerSelected.type))
            towerImg = localdefs.imgLoad(os.path.join("towerimgs/",self.player.towerSelected.type,"1.png"))
            self.topPanel_towerImg.set_image(towerImg)
            self.topPanel_towerDamage.set_text(text="Damage: {}".format(self.player.towerSelected.basedamage))#update with appropriate variable that stores current DPS
            self.topPanel_towerReload.set_text(text="Speed: {}".format(self.player.towerSelected.basetime))
            #\n doesnt work with .set_text. Need a different way to display description
            self.topPanel_towerAbilityDesc.set_text(text="placeholder that is very\n long and longer and\n longer")
            self.topPanel_towerAbilityStats.set_text(text="placeholder")
            self.topPanel_separator.set_text(text="________________________")

            thorpy.store(self.topPanel_towerstats, align='center')
            thorpy.store(self.topPanel_titleandimage, align='center')
            self.last_selected = self.player.towerSelected

        #update the bottom panel when a new wave is sent
        if self.player.next_wave == True:
            self.botPanel_titleText.set_text(text="Enemy")
            self.botPanel_enemyImg = thorpy.Image.make(color=(0, 0, 0, 0))
            self.botPanel_enemyImg.set_size((60, 60))
            self.botPanel_enemyHealth.set_text(text="",)
            self.botPanel_enemySpeed.set_text(text="")
            self.botPanel_enemyAbilityDesc.set_text(text="")
            self.botPanel_futureWaves.set_text(text="Upcoming Waves: ")

            thorpy.store(self.botPanel_titleandimage, align='center')
            thorpy.store(self.botPanel_enemystats, align='center')
