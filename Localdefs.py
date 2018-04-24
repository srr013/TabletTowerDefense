import Map
import Player

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
roadlist = list()
activeiceroadlist = list()
burnroadlist = list()
towerGroupDict = {'Life': [], 'Fire': [], 'Ice': [], 'Gravity': [], 'Wind': []}

topBar_ElementList = [("Wave: ", "WaveNum", str(Player.player.wavenum), "enemyimgs/Crowd_r.png"),
                      ("Score: ", "Score", int(Player.player.score), "iconimgs/100.png"),
                      ("Money: ", "Money", Player.player.money, "iconimgs/coin20x24.png"),
                      ("Gems: ", "Gems", Player.player.gems, "iconimgs/reddiamond.png"),
                      ("Health: ", "Health", Player.player.health, "iconimgs/heart24x24.png"),
                      ("Timer: ", "Timer", int(Map.mapvar.waveseconds), "iconimgs/clock.png")]

towerAttributes = ["[b]Damage(Dmg)[/b]: 1 damage results in an enemy's loss of 1 armor point or 1 enemy HP if no armor points remain.",
                   "[b]Range(Rng)[/b]: Towers can only shoot enemies inside their range. Range is calculated in pixels. ",
                   "[b]Reload(Rld)[/b]: Time between shots in game seconds.",
                   "[b]Stun Time(StunTm)[/b]: Amount of time in game seconds that an enemy is immobilized after being stunned",
                   "[b]Stun Chance(Stun%)[/b]: The percent chance that the impact of a shot on an enemy will stun it.",
                   "[b]Slow Time(SlowTm)[/b]: Amount of time that an enemy is slowed each time it is hit.",
                   "[b]Push[/b]: Distance in pixels that an enemy is moved after being hit."]
towerAttackTypes = ["[b][u]Tower Targeting:[/u][/b]",
                   "[i]Ground Only[/i]: Tower attacks all enemies except Airborn.",
                   "[i]Air Only[/i]: Tower attacks only Airborn enemies.",
                   "[i]Both[/i]: Tower attacks all enemies."]