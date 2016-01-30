import threading
import time

import game_logic

# Default key binds
MOVE_LEFT = 37  # Left arrow
MOVE_RIGHT = 39  # Right arrow
ROTATE = 38  # Up arrow
FORCE_DOWN = 40  # Down arrow
PAUSE = 32  # Space


# TODO: make it work smooth
class KeyboardHandler:
    """
    Possibly this will work fine only on Windows
    """
    def __init__(self, field: game_logic.Field, interval=0.1):
        self._field = field
        self._last_time = time.time()
        self.interval = interval
        self._pressed_keys = dict()
        self._key_processor = threading.Thread(target=self._process_key)
        self._key_processor.start()
        self.processed_once = False

    def on_key_press(self, event):
        print('On key press')
        if event.keycode not in self._pressed_keys:
            self._pressed_keys[event.keycode] = 0

    def on_key_release(self, event):
        print("On key release")
        if event.keycode in self._pressed_keys:
            self._pressed_keys.pop(event.keycode)

    def _process_key(self):
        while True:
            for code in self._pressed_keys:
                # Make a decision what should we do with this key (Where is my switch keyword??)
                if code == MOVE_LEFT:
                    self._process_move_left()
                elif code == MOVE_RIGHT:
                    self._process_move_right()
                elif code == ROTATE:
                    self._process_rotate()
                elif code == FORCE_DOWN:
                    self._process_force_down()
                elif code == PAUSE:
                    self._process_pause()
                self.processed_once = True
            time.sleep(self.interval)

    def _process_move_left(self):
        self._field.move_left()

    def _process_move_right(self):
        self._field.move_right()

    def _process_rotate(self):
        pass

    def _process_force_down(self):
        pass

    def _process_pause(self):
        pass