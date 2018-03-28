import random
import Enemy
import Localdefs
import Map


maxSets = 6

def genModList():
    modifiers = ['speedInc', 'strInc', 'numInc', 'armInc', 'fireRes', 'waterRes','rewardInc']
    modList = []

    setNum = 1  # a set is counted every X waves
    sets = maxSets

    while sets > 0:
        x = 0
        numMods = int((setNum) / 2.5)
        if numMods == 0:
            modList.append([])
        elif numMods >= 0:
            list = []
            while x < numMods:
                list.append(modifiers[random.randint(0,len(modifiers)-1)])
                x += 1
            modList.append(list)
        sets -= 1
        setNum += 1
    return modList

def wavegen():
    enemyModList = genModList()
    setNum = 1 # a set is counted every X waves
    wavesPerSet = 7
    enemytypes = ['Standard', 'Crowd', 'Strong', 'Splinter', 'Airborn']#['Airborn','Airborn','Airborn','Airborn','Airborn',]
    waveList = []
    waveTypeList = []
    waveNum = 1
    if Map.mapvar.difficulty == 'easy':
        difficultyMod = 1
    elif Map.mapvar.difficulty == 'medium':
        difficultyMod = 1.2
    if Map.mapvar.difficulty == 'hard':
        difficultyMod = 1.6


    while setNum < maxSets:
        counter = 0
        while float(waveNum)/wavesPerSet <= setNum:
            if Map.mapvar.waveOrder == 'standard':
                enemyType = enemytypes[counter]
                counter+=1
                if counter>4:
                    counter=0
            else:
                enemyType  = enemytypes[random.randint(0, len(enemytypes)-1)]   #selects a random enemy type
            numEnemies = int(eval("Enemy."+enemyType +".defaultNum") * (1+ (setNum/10.0))*difficultyMod)
            healthEnemies = int(eval("Enemy."+enemyType +".health") * (1 + (setNum/10.0))*difficultyMod)
            speedEnemies = eval("Enemy."+enemyType +".speed") * (1 + (setNum/10.0))
            armorEnemies = eval("Enemy."+enemyType +".armor") * (1 + (setNum/10.0))*difficultyMod
            rewardEnemies = int(eval("Enemy."+enemyType +".reward") * (1 + (setNum/10.0)))

            if float(waveNum)/wavesPerSet == setNum:
                isBoss = True
            else:
                isBoss = False

            wave = {'wavenum':waveNum, 'setnum':setNum, 'enemynum':numEnemies, 'enemyhealth':healthEnemies, 'enemyspeed':speedEnemies,
             'enemytype':enemyType, 'enemyarmor': armorEnemies, 'enemymods':enemyModList[setNum-1], 'enemyreward':rewardEnemies, 'isboss':isBoss}
            waveList.append(wave)
            waveTypeList.append([enemyType,isBoss])
            waveNum += 1
        setNum += 1
    return waveList,waveTypeList


