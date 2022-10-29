import collections
import time
import typing as t

import custom_threads

# Default key binds
MOVE_LEFT = 37  # Left arrow
MOVE_RIGHT = 39  # Right arrow
ROTATE = 38  # Up arrow
FORCE_DOWN = 40  # Down arrow
PAUSE = 32  # Space

TICK_INTERVAL = 0.1
TICK_DELAY = 0.2


class KeyEventParams:
    def __init__(self):
        self.is_pressed: bool = False
        self.press_time: t.Optional[float] = None
        self.has_been_processed_once: bool = False


class KeyboardHandler:
    """
    Handles key pressing/release avoiding OS specific timers for key repeat
    """

    def __init__(self, game_over_event):
        self.move_left_func = None
        self.move_right_func = None
        self.force_down_func = None
        self.rotate_func = None
        self.pause_func = None

        # int keycode: (bool is_pressed, float pressed time, bool )
        self._keys_pressed = collections.defaultdict(KeyEventParams)

        self.tick_thread = custom_threads.TickThread(self._process_pressed_keys, TICK_INTERVAL, game_over_event)
        self.tick_thread.start()

    def on_key_press(self, event):
        kp = self._keys_pressed[event.keycode]
        kp.is_pressed = True
        if kp.press_time is None:
            kp.press_time = time.time()

    def on_key_release(self, event):
        kp = self._keys_pressed[event.keycode]
        kp.is_pressed = False
        kp.press_time = None
        kp.has_been_processed_once = False

    def _process_pressed_keys(self):
        # Make a decision what should we do with this key
        for code, kp in self._keys_pressed.items():
            if not kp.is_pressed or \
                    (time.time() - kp.press_time < TICK_DELAY and kp.has_been_processed_once):
                continue
            kp.has_been_processed_once = True
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
