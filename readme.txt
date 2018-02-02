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
    These files are new or have been heavily modified from the legacy code. If you are reviewing the entire game this list
    is organized for a top-down review:

    towerdefense - contains the game's main loop and instantiates basic classes and variables
    MainFunctions - contains most of the basic functions required by the main loop
    localclasses - contains the Tower, Enemy, Timer, and Shot classes used in the game
    localdefs - contains the Path, Map, and Player classes. Also contains many "global" variables and lists, and functions used for
    animation, enemy movement, and pausing the game.
    EventFunctions - handles keyboard and mouse input
    pathfinding - implements the a* pathfinding algorithm. Functions return a list of movement for enemies.
    Animation - contains the Animation class for generating a dict of images associated with movement directions
    GUI - handles the creation and updates of top and bottom bars and the rightside panels
    wavegen - not fully implemented. Will generate a dict of enemy waves for the Sender class

    Legacy files:
    TowerAbilities - manages tower upgrades and selling. Upcoming revamp of the Tower class will merge this into a new file with Tower.
    SenderClass - manages creation of enemies

Artwork:
    All artwork is my own unless specified in the ContentSources.txt file


