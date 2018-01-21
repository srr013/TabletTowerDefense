import MainFunctions
import Player

import sys


def _keyboard_closed(self):
    self._keyboard.unbind(on_key_down=self._on_keyboard_up)
    self._keyboard = None


def _on_keyboard_up(key, scancode):
    print (key, scancode)
    if scancode[1] == 'n':
        Player.player.next_wave=True
    elif keycode[1] == 'up':
        if Player.player.game_speed < 10:
            Player.player.game_speed_update(1,True)
    elif keycode[1] == 'down':
        if Player.player.game_speed >1:
            Player.player.game_speed_update(-1, True)
    return True