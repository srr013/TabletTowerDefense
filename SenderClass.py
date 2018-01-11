from localdefs import senderlist,mapvar
from localclasses import Enemy

class Sender():
    ##called from EventFunctions, which currently always calls wave#a. Data from the mapdict comes from mapproperties.txt
    def __init__(self,wave,letter):
        self.wavenum = wave
        ##This is setting self.enemycounter to the Time value from mapproperties.txt
        ##example output of a dict list (lvl1/mapproperties.txt): [4.0, 1.0, 10.0, 1.0, 0.0, 1.0, 1.0]
        self.enemycounter = self.enemycounterinit = mapvar.mapdict['wave'+str(self.wavenum)+letter][1]
        #only "a" right now
        self.letter = letter
        self.enemiesgone = 0
        senderlist.append(self)
    def tick(self,frametime):
        self.enemycounter -= frametime
        if self.enemycounter<=0:
            if self.enemiesgone<mapvar.mapdict['wave'+str(self.wavenum)+self.letter][0]:
                Enemy(self.wavenum,self.letter)
                self.enemiesgone+=1
            else:
                senderlist.remove(self)
            self.enemycounter = self.enemycounterinit
