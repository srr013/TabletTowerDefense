========================================
Tablet Tower Defense ReadMe:
========================================
Version .2

----------------
License
----------------
This work is licensed under the NPOSL-3.0 license. No revenue may be generated from sale of the software, support or services.
https://opensource.org/licenses/NPOSL-3.0
Please contact the creator (scott.r.rossignol@gmail.com) with any questions.

----------------
Gameplay:
----------------
You're under attack! Build towers to keep the enemies from getting to your base. Upgrade your towers to counter the
ever-increasing strenght of your enemies.

You can build towers by touching anywhere on the playable area. Click Next Wave to send the enemies at your defenses and
collect gold when they are destroyed.

----------------
In Order To Run:
----------------
You can download the game to an Android tablet from the Google Play store. See www.tablettowerdefense.com for more info.

To run on the computer:
Install Python: Written and tested with version 2.7. Version 3.6 is possible with a few changes to the code.
Install Kivy: https://kivy.org/docs/gettingstarted/intro.html
Run main.py

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
    TowerDragging - allows creation of multiple towers through a touch and drag motion
    Shot - handles shot mechanics after firing
    Enemy - contains enemy classes and functions
    Player - player-specific variables related to the game
    Map - contains map-related game variables and sets up the game for play
    Road - creates road images and handles their positioning
    Wall - manages widgets used as barriers for enemies and tower placement so the playfield is defined
    Playfield - movable element handling touch input. This is the surface the game is played on
    TowerAbilities - actions taken on a tower like selling, rotation, and upgrades
    localdefs - contains some local variables used across classes
    EventFunctions - sends new enemy waves to SenderClass and handles placing towers.
    Keyboard_Kivy - used for keyboard actions when played on a computer. N sends a new wave, esc to quit.
    Pathfinding - implements the a* pathfinding algorithm. Functions return a list of movement for enemies.
    GUI - handles the creation and updates of graphical elements such as buttons and menus
    SenderClass - manages creation of enemies
    Wavegen - generates a wave dict for the Sender.
    Utilities - game-wide functions and helpers.

Artwork:
    All artwork is my own unless specified in the ContentSources.txt file


