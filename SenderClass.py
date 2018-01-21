import localdefs,Enemy,Map,Player

class Sender():
    '''called from EventFunctions, which currently always calls wave#a. Data from the mapdict comes from mapproperties.txt'''
    def __init__(self,wave,letter):
        self.wavenum = wave
        ##This is setting self.enemycounter to the Time value from mapproperties.txt
        ##example output of a dict list (lvl1/mapproperties.txt): [4.0, 1.0, 10.0, 1.0, 0.0, 1.0, 1.0]
        self.enemycounter = self.enemycounterinit = Map.mapvar.mapdict['wave'+str(self.wavenum)+letter][1]
        #only "a" right now
        self.letter = letter
        self.enemiesgone = 0
        localdefs.senderlist.append(self)
    def tick(self):
        '''Sends an enemy each frame and maintains Senderlist'''
        self.enemycounter -= Player.player.frametime
        if self.enemycounter<=0:
            if self.enemiesgone<Map.mapvar.mapdict['wave'+str(self.wavenum)+self.letter][0]:
                enemy = Enemy.Enemy(self.wavenum,self.letter)
                self.enemiesgone+=1
            else:
                localdefs.senderlist.remove(self)
            self.enemycounter = self.enemycounterinit
