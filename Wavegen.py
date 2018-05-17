import random

import Map
import Enemy

maxSets = 20


def genModList():
    """Generates modifiers to be used in the future. Modifiers are not yet implemented."""
    modifiers = ['speedInc', 'strInc', 'numInc', 'armInc', 'fireRes', 'waterRes', 'rewardInc']
    modList = []

    setNum = 1  # a set is counted every X waves
    sets = maxSets

    while sets > 0:
        x = 0
        numMods = int((setNum) / 2.5)

        if numMods >= 0:
            list = []
            while x < numMods:
                list.append(modifiers[random.randint(0, len(modifiers) - 1)])
                x += 1
            modList.append(list)
        sets -= 1
        setNum += 1
    return modList


def wavegen():
    """Generates the list of enemies for each game"""
    enemyModList = genModList()
    setNum = 1  # a set is counted every X waves
    wavesPerSet = 6
    #enemytypes = ['Airborn','Airborn','Airborn','Airborn','Airborn']
    #enemytypes = ['Splinter','Splinter','Splinter','Splinter','Splinter',]
    enemytypes = ['Standard', 'Crowd', 'Strong', 'Splinter','Airborn']
    waveDict = {}
    waveTypeList = []
    waveNum = 1
    difficultyMod = 1.75
    rewardMod = 5
    if Map.mapvar.difficulty == 'medium':
        difficultyMod = 2
        rewardMod = 4
    elif Map.mapvar.difficulty == 'hard':
        difficultyMod = 2.5
        rewardMod = 3
    counter = 0
    while setNum < maxSets:
        while float(waveNum) / wavesPerSet <= setNum:
            isBoss = False
            if float(waveNum) / wavesPerSet == setNum:
                isBoss = True
            if Map.mapvar.waveOrder == 'standard':
                enemyType = enemytypes[counter]
                counter += 1
                if counter > 4:
                    counter = 0
            else:
                enemyType = enemytypes[random.randint(0, len(enemytypes) - 1)]  # selects a random enemy type
            numEnemies = round(int(eval("Enemy." + enemyType + ".defaultNum") * (1 + (setNum / 10.0)) * (difficultyMod/2)),1)
            healthEnemies = int(eval("Enemy." + enemyType + ".health") * (1 + (setNum / 7.0)) * difficultyMod)
            speedEnemies = eval("Enemy." + enemyType + ".speed") * (1 + (setNum / 10.0))
            armorEnemies = eval("Enemy." + enemyType + ".armor") * (1 + (setNum / 10.0)) * difficultyMod
            rewardEnemies = round(int(eval("Enemy." + enemyType + ".reward") * (1 + (setNum / 10.0))*rewardMod),1)

            if isBoss:
                healthEnemies *= 4
                speedEnemies *= 1.3
                armorEnemies *= 2
                rewardEnemies *= 10

            waveDict[waveNum]={'setnum': setNum, 'enemynum': numEnemies, 'enemyhealth': healthEnemies,
                    'enemyspeed': speedEnemies,
                    'enemytype': enemyType, 'enemyarmor': armorEnemies, 'enemymods': enemyModList[setNum - 1],
                    'enemyreward': rewardEnemies, 'isboss': isBoss}
            #print waveDict[waveNum]
            waveTypeList.append([enemyType, isBoss])
            waveNum += 1
        setNum += 1
    return waveDict, waveTypeList
