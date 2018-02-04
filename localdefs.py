import Player
import Map

enemylist = list()
flyinglist = list()
towerlist = list()
bulletlist = list()
iconlist = list()
menulist = list()
explosions = list()
senderlist = list()
timerlist = list()
shotlist = list()
alertQueue = list()
towerabilitylist = list()
towerGroupDict = {'Life':[], 'Fire':[], 'Ice':[], 'Gravity':[], 'Wind':[]}
topBar_ElementList = [("Wave: ", "Wave", Player.player.wavenum,"iconimgs/smallbox.png"),
                                    ("Score: ", "Score", int(Player.player.score), "iconimgs/100.png"),
                                    ("Money: ", "Money", Player.player.money,"iconimgs/coin20x24.png"),
                                    ("Health: ", "Health", Player.player.health,"iconimgs/heart24x24.png"),
                                    ("Timer: ", "Timer", int(Map.waveseconds), "iconimgs/clock.png")]

'''def pauseGame():
    Pauses the gameloop and counts the time paused.
    timepaused = time.time()
    totaltimepaused = 0

    font = pygame.font.Font(None, 48)
    text = font.render("Game Paused. Press Space to start.", 1, (255,0,0))
    textpos = text.get_rect(center=(Map.scrwid / 2, Map.scrhei / 2))

    while totaltimepaused == 0:
        Player.player.screen.blit(text, textpos)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                keyinput = pygame.key.get_pressed()
                if keyinput[K_SPACE]:
                    totaltimepaused = time.time() - timepaused
                    Player.player.paused = False
    Player.player.pausetime =  totaltimepaused'''





#code not currently in use. Keeping as a source for enemy overhaul
#class PoisonTimer(threading.Thread):
#    def __init__(self,enemy,damage,seconds):
#        threading.Thread.__init__(self)
#        self.runtime = seconds
#        self.dam = damage
#        self.target = enemy
#        enemy.poisontimer=self
#        self.kill = False
#    def run(self):
#        sec = self.runtime*1.0
#        while(sec>0):
#            sec-=0.1
#            time.sleep(0.1)
#            if self.target.poisontimer == self or self.kill == True:
#                if self.target.health>0:
#                    self.target.health-=self.dam
#                    if self.target.health<=0:
#                        self.target.die()
#                        return
#                else:
#                    return
#            else:
#                return
#        if self.target.poisontimer == self:
#            self.target.poisontimer = None

#EnemyImageArray = list()
#def genEnemyImageArray():
#    for type in ["none","enemy","Speedy","Healthy","Armor"]:
#        ia = list()
#        try:enemyimage = imgLoad(os.path.join('enemyimgs',type+'.png'))
#        except:print "enemy image failed to load"
#        ia.append(enemyimage)
#        ia.append(pygame.transform.rotate(enemyimage,90))
#        ia.append(pygame.transform.flip(enemyimage,True,False))
#        ia.append(pygame.transform.rotate(enemyimage,-90))
#        EnemyImageArray.append(ia)
