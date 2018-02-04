import localdefs
import Player
import Enemy

import operator
import random

class Sender():
    '''called from EventFunctions. Creates a sender that creates the enemies.'''
    def __init__(self, **kwargs):
        self.specialSend = kwargs['specialSend']
        if self.specialSend:
            self.enemytype = 'Crowd'
            self.pos = kwargs['pos']

            self.curnode = kwargs['curnode']
            self.numThisWave = kwargs['number']
            self.enemycounter = self.enemycounterinit = kwargs['deploySpeed']
            print ("deploying this many:",self.numThisWave)
        else:
            self.enemytype = Player.player.waveList[Player.player.wavenum]['enemytype']
            self.numThisWave = Player.player.waveList[Player.player.wavenum]['enemynum']
            self.enemycounter = self.enemycounterinit = eval("Enemy." +self.enemytype+".deploySpeed")
        self.enemiesDeployed = 0
        self.isBoss = Player.player.waveList[Player.player.wavenum]['isboss']
        localdefs.senderlist.append(self)
        print (self.enemytype)
    def tick(self):
        '''Sends an enemy each frame and maintains Senderlist'''
        self.enemycounter -= Player.player.frametime
        if self.enemycounter<=0 or self.enemiesDeployed == 0:
            if self.enemiesDeployed < self.numThisWave:
                #print ("deploying enemy")
                if self.enemytype == 'Crowd' and self.specialSend == True:
                    self.pos_x = self.pos[0]+(random.randint(0,50))
                    self.pos_y = self.pos[1]+(random.randint(0,50))

                    f = operator.methodcaller(self.enemytype,isBoss=self.isBoss,specialSend=self.specialSend, pos=(self.pos_x,self.pos_y), curnode=self.curnode)
                    f(Enemy)
                else:
                    f = operator.methodcaller(self.enemytype, isBoss=self.isBoss, specialSend=self.specialSend)
                    f(Enemy)
                self.enemiesDeployed+=1
            else:
                localdefs.senderlist.remove(self)

            self.enemycounter = self.enemycounterinit
