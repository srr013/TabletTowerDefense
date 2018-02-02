========================================
Scott's Tower Defence Game ReadMe:
========================================
Version .1
Note: This game is playable without issue or error, but it's not very fun yet and this version cannot be run on a mobile
device or browser. Version 1 will be ported to the Kivy library and ready to play on a tablet. Publication date
on the Google Play store is targeted for May 2018.

----------------
In Order To Run:
----------------
Install Python: Written and tested with version 2.7. Version 3.6 is running in test versions of v1.0
Install PyGame: http://www.pygame.org
Install Thorpy (for buttons and menus): http://www.thorpy.org/index.html
(Thorpy is not in use in v1.0 as it has been replaced by Kivy)

Run towerdefense.py

---------------
Files Included:
---------------
Text files:
    readme.txt - This file
    ContentSources.txt - Includes sources for various content used in this game. All content used is available
    under an open source license

Game files(.py):
    main - contains the game's main loop and instantiates basic classes and variables
    MainFunctions - contains most of the basic functions required by the main loop
    Tower - contains tower classes and functions
    TowerGroup - groups and trackers towers of like types
    Shot - handles shot mechanics after firing
    ShotCloud - handles cloud-like shot appearances
    Enemy - contains enemy classes and functions
    Map - creates the playing field including path bitting. Contains major game variables.
    Playfield - movable element handling touch input
    TowerAbilities - actions taken on a tower like selling and upgrades
    localdefs - contains the Path, Map, and Player classes. Also contains many "global" variables and lists, and functions used for
    animation, enemy movement, and pausing the game.
    EventFunctions - handles keyboard and mouse input
    pathfinding - implements the a* pathfinding algorithm. Functions return a list of movement for enemies.
    GUI - handles the creation and updates of top and bottom bars and the rightside panels
    SenderClass - manages creation of enemies
    Wavegen - generates a random wave dict for the Sender
    Utilities - game-wide functions

Artwork:
    All artwork is my own unless specified in the ContentSources.txt file


