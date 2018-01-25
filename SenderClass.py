import localdefs
import Player
import Enemy

class Sender():
    '''called from EventFunctions. Creates a sender that creates the enemies.'''
    def __init__(self, **kwargs):
        self.specialSend = kwargs['specialSend']
        if self.specialSend:
            self.enemytype = 'Crowd'
            self.pos = kwargs['pos']
            print (self.pos)
            self.numThisWave = kwargs['number']
        else:
            self.enemytype = Player.player.waveList[Player.player.wavenum]['enemytype']
            self.numThisWave = Player.player.waveList[Player.player.wavenum]['numenemies']
        self.enemycounter = self.enemycounterinit = eval("Enemy." +self.enemytype+".deploySpeed")
        self.enemiesDeployed = 0
        self.isBoss = Player.player.waveList[Player.player.wavenum]['isBoss']
        localdefs.senderlist.append(self)
        print (self.enemytype)
    def tick(self):
        '''Sends an enemy each frame and maintains Senderlist'''
        self.enemycounter -= Player.player.frametime
        if self.enemycounter<=0:
            if self.enemiesDeployed < self.numThisWave:
                #print ("deploying enemy")
                if self.enemytype == 'Crowd' and self.specialSend == True:
                    eval('Enemy.' +str(self.enemytype) +'(isBoss ='+str(self.isBoss)+',self.pos =('+str(self.pos[0])+','+str(self.pos[1])+'))') #notworking
                else:
                    eval('Enemy.' +str(self.enemytype) +'(isBoss ='+str(self.isBoss)+')')
                self.enemiesDeployed+=1
            else:
                localdefs.senderlist.remove(self)

            self.enemycounter = self.enemycounterinit
