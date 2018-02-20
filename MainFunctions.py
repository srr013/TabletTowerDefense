import Localdefs, Map, Towers, Pathfinding
import time
import Player
import GUI
import TowerAbilities

black = (0,0,0)
white = (255,255,255)
red = (255,0,0)

def makeIcons():
    '''Creates an Icon from the class for each tower'''
    for tower in Towers.baseTowerList:
        Towers.Icon(tower)

def makeUpgradeIcons():
    for ability in TowerAbilities.baseAbilityList:
        TowerAbilities.TowerAbility(ability)

def tickAndClear(clock,background):
    '''Updates the game time and blits the background
    Clock: pygame.time.Clock instance
    background: the game's background image'''
    clock.tick(30)
    #Player.player.screen.blit(background,(0,0))

def workSenders(*args):
    '''Determines what enemys to create and where to place them.
    Frametime: the amount of time elapsed per frame'''
    for sender in Localdefs.senderlist:
        sender.tick()

def workTowers():
    '''Towers target enemy(s) and create Shot instances
    Frametime: the amount of time elapsed per frame'''
    for tower in Localdefs.towerlist:
        tower.takeTurn()
    for type in Localdefs.towerGroupDict.values():
        if type:
            for group in type:
                if group.towerSet == set():
                    group.removeTowerGroup()
                else:
                    group.takeTurn()

def updateFlyingList():
    '''Update movelist for flying enemies'''
    # only border walls for flying list. Flying list to be index 1.
    Map.flyPath.walls = Map.path.border_walls
    Map.flyPath.weights = {}
    came_from, cost_so_far = Pathfinding.get_path(Map.flyPath, Map.mapvar.startpoint, Map.mapvar.basepoint)
    Map.mapvar.movelists.append(Pathfinding.reconstruct_path(came_from, Map.mapvar.startpoint, Map.mapvar.basepoint))
    Map.mapvar.genmovelists()

def updatePath():
    '''Update the path using A* algorithm'''
    Map.newPath.walls = Map.path.get_wall_list()
    came_from, cost_so_far = Pathfinding.get_path(Map.newPath, Map.mapvar.startpoint, Map.mapvar.basepoint)
    if len(Map.mapvar.movelists) == 0:
        Map.mapvar.movelists.append(Pathfinding.reconstruct_path(came_from, Map.mapvar.startpoint, Map.mapvar.basepoint))
    else:
        Map.mapvar.movelists[0] = (Pathfinding.reconstruct_path(came_from, Map.mapvar.startpoint, Map.mapvar.basepoint))
    if Map.mapvar.movelists[0] == "Path Blocked":
        addAlert("Path Blocked", 48, "center", (240, 0, 0))
        return False

    if len(Map.mapvar.movelists) < 2:
        updateFlyingList()
    Map.mapvar.genmovelists()
    Map.mapvar.updatePath = False
    Player.player.newMoveList = True
    Map.mapvar.roadGen()
    updateIce()

def updateIce():
    for group in Localdefs.towerGroupDict['Ice']:
        group.getAdjacentRoads()


def workShots():
    '''Update the shot location and hit the enemy'''
    for shot in Localdefs.shotlist:
        shot.takeTurn()

def dispText():
    '''Display any alerts in the queue, then remove them'''
    for alert in Localdefs.alertQueue:
        if alert[2] <= time.time():
            Localdefs.alertQueue.pop(0)
        else:
            pass

def dispExplosions():
    for explosion in Localdefs.explosions:
        explosion[2].dispExplosions(explosion)

def addAlert(message, fontsize, location, color, length = 2):
    pass
#     '''Add an alert to alertQueue
#     Message: the text to display
#     Fontsize: integer size of font
#     Location: string indicating location to display message. [center]
#     length: Default 2. Length of time to display message in seconds.'''
#     if location == "center":
#         location = (Map.scrwid+Map.mapoffset[0]/2, Map.scrhei+Map.mapoffset[1]/2)
#
#     font = pygame.font.Font(None, fontsize)
#     text = font.render(message, 1, color)
#     textpos = text.get_rect(center=location)
#     endtime = time.time() + length
#     localdefs.alertQueue.append([text,textpos, endtime])


def workEnemies():
    '''Move, draw to screen, draw health bars of enemys.
    Frametime: the amount of time elapsed per frame'''
    for enemy in Map.mapvar.enemycontainer.children:
        enemy.distBase = enemy.distToBase()
        if Player.player.newMoveList:
            enemy.movelist = Map.mapvar.pointmovelists[enemy.movelistNum]
        enemy.takeTurn()

    Player.player.newMoveList = False


            #(Player.player.screen, (0,0,0), (enemy.rect_x,enemy.rect_y-2), (enemy.rect_x+enemy.rect_w,enemy.rect_y-2), 3)
        #if enemy.poisontimer:
        #    pygame.draw.line(Player.player.screen, (0,255,0), (enemy.rect_x,enemy.rect_y-2), (enemy.rect_x+(enemy.health*1.0/enemy.starthealth*1.0)*enemy.rect_w,enemy.rect_y-2), 3)
        #else:
        #    pygame.draw.line(Player.player.screen, (255,0,0), (enemy.rect_x,enemy.rect_y-2), (enemy.rect_x+(enemy.health*1.0/enemy.starthealth*1.0)*enemy.rect_w,enemy.rect_y-2), 3)

def updateGUI(wavetime):
    GUI.gui.updateTopBar(wavetime)



def towerButtonPressed(selected):
    '''receives a Button object from GUI_Kivy
    Display the tower and a circle for tower range if a button is pressed'''

    mouseat = Map.mapvar.background.touch_pos
    if eval("Towers."+selected.type+"Tower").basecost*(1-Player.player.modDict[selected.type.lower()+"CostMod"])*(1-Player.player.modDict["towerCostMod"]) > Player.player.money:
        addAlert("Not Enough Money", 48, "center", (240, 0, 0))
        Player.player.towerSelected = None
        selected = None
        return selected

    selected.img.pos = mouseat
    Map.mapvar.background.add_widget(selected.img)

def pauseGame(*args):
    id = args[0].id
    if Player.player.state == 'Playing':
        if id == 'pause':
            Player.player.state = 'Paused'
        if id == 'menu':
            Player.player.state = 'Menu'
    elif Player.player.state == 'Paused':
        Player.player.state = 'Playing'


def resetGame():
    '''Resets game variables so player can restart the game quickly.'''
    AllLists = [Localdefs.towerlist, Localdefs.bulletlist, Localdefs.menulist, Localdefs.explosions, Localdefs.senderlist, Localdefs.timerlist, Localdefs.shotlist, Localdefs.alertQueue]

    i=0
    for list in AllLists:
        while i < len(list):
            list.pop()

    Map.mapvar.towercontainer.clear_widgets()
    Map.mapvar.enemycontainer.clear_widgets()
    Map.mapvar.explosioncontainer.clear_widgets()
    Map.mapvar.roadcontainer.clear_widgets()
    Map.mapvar.shotcontainer.clear_widgets()
    Map.mapvar.cloudcontainer.clear_widgets()
    Map.mapvar.towercontainer.clear_widgets()


    Player.player.wavenum = 0
    GUI.gui.myDispatcher.WaveNum = str(Player.player.wavenum)
    GUI.gui.myDispatcher.Wave = str(Player.player.wavenum)
    Player.player.wavetime = int(Map.waveseconds)
    GUI.gui.myDispatcher.Timer = str(Player.player.wavetime)
    Player.player.money = Player.playermoney
    GUI.gui.myDispatcher.Money = str(Player.player.money)
    Player.player.health = Player.playerhealth
    GUI.gui.myDispatcher.Health = str(Player.player.health)
    Player.player.score = 0
    GUI.gui.myDispatcher.Score = str(Player.player.score)

    updatePath()