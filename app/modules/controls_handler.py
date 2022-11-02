import collections
import time
import typing as t

from . import custom_threads

# Default key binds
MOVE_LEFT = 37  # Left arrow
MOVE_RIGHT = 39  # Right arrow
ROTATE = 38  # Up arrow
FORCE_DOWN = 40  # Down arrow
PAUSE = 32  # Space
NEW_GAME = 13  # Enter

TICK_INTERVAL = 0.08
TICK_DELAY = 0.2


class KeyEventParams:
    def __init__(self):
        self.is_pressed: bool = False
        self.press_time: t.Optional[float] = None
        self.has_been_processed_once: bool = False


class ControlsHandler:
    """
    Handles key pressing/release avoiding OS specific timers for key repeat
    """
    REPEAT_KEYS = {MOVE_RIGHT, MOVE_LEFT}  # repeat only this, other keys processed once per press

    def __init__(self):
        self.move_left_func = None
        self.move_right_func = None
        self.force_down_func = None
        self.force_down_cancel_func = None
        self.rotate_func = None
        self.pause_func = None
        self.new_game_func = None
        self.skin_change_func = None

        # int keycode: (bool is_pressed, float pressed time, bool )
        self._keys_pressed = collections.defaultdict(KeyEventParams)

        self.tick_thread = custom_threads.TickThread(self._process_pressed_keys, TICK_INTERVAL)
        self.tick_thread.start()

    def on_key_press(self, event):
        kp = self._keys_pressed[event.keycode]
        kp.is_pressed = True
        if kp.press_time is None:
            kp.press_time = time.time()
        if not kp.has_been_processed_once:
            self._process_keys(event.keycode)
        kp.has_been_processed_once = True

    def on_key_release(self, event):
        kp = self._keys_pressed[event.keycode]
        kp.is_pressed = False
        kp.press_time = None
        kp.has_been_processed_once = False

        if event.keycode == FORCE_DOWN:
            self.force_down_cancel_func()

    def _process_pressed_keys(self):
        # Make a decision what should we do with this key
        for code, kp in self._keys_pressed.items():
            if code not in self.REPEAT_KEYS or \
                    not kp.is_pressed or time.time() - kp.press_time < TICK_DELAY or not kp.has_been_processed_once:
                continue
            self._process_keys(code)

    def _process_keys(self, code):
        if code == MOVE_LEFT and callable(self.move_left_func):
            # noinspection PyCallingNonCallable
            self.move_left_func()
        if code == MOVE_RIGHT and callable(self.move_right_func):
            # noinspection PyCallingNonCallable
            self.move_right_func()
        if code == ROTATE and callable(self.rotate_func):
            # noinspection PyCallingNonCallable
            self.rotate_func()
        if code == FORCE_DOWN and callable(self.force_down_func):
            # noinspection PyCallingNonCallable
            self.force_down_func()
        if code == PAUSE and callable(self.pause_func):
            # noinspection PyCallingNonCallable
            self.pause_func()
        if code == NEW_GAME and callable(self.new_game_func):
            self.new_game_func()
