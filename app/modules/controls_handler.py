"""Interface between UI, user and logic"""
import collections
import dataclasses
import enum
import time
import typing as t
from queue import Queue

from .tick_thread import TickThread


class _Keycodes(enum.IntEnum):
    """Commands and key binds"""
    LEFT_ARROW = 37  # Left arrow
    RIGHT_ARROW = 39  # Right arrow
    UP_ARROW = 38  # Up arrow
    DOWN_ARROW = 40  # Down arrow
    SPACE = 32  # Space
    ENTER = 13  # Enter


TICK_INTERVAL = 0.08
TICK_DELAY = 0.2


@dataclasses.dataclass
class _KeyEventParams:
    """Stores info about pressed key"""
    is_pressed: bool = False
    press_time: float | None = None
    has_been_processed_once: bool = False


class ControlEventType(enum.StrEnum):
    """Possible event types"""
    KEY_PRESS = enum.auto()


class Commands(enum.StrEnum):
    """Commands"""
    MOVE_LEFT = enum.auto()  # Left arrow
    MOVE_RIGHT = enum.auto()  # Right arrow
    ROTATE = enum.auto()  # Up arrow
    FORCE_DOWN = enum.auto()  # Down arrow
    FORCE_DOWN_CANCEL = enum.auto()  # Down arrow
    PAUSE = enum.auto()  # Space
    NEW_GAME = enum.auto()  # Enter


@dataclasses.dataclass
class ControlEvent:
    """Stores control event e.g. move key press, skin change, new game etc."""
    event_type: ControlEventType
    payload: t.Any = None


class ControlsHandler:
    """
    Handles key pressing/release avoiding OS specific timers for key repeat
    """
    # auto-repeat until key release only this commands, other keys processed once per press
    REPEAT_COMMAND = {Commands.MOVE_RIGHT,
                      Commands.MOVE_LEFT}

    def __init__(self):

        self._keycode_to_command_map = {
            _Keycodes.LEFT_ARROW: Commands.MOVE_LEFT,
            _Keycodes.RIGHT_ARROW: Commands.MOVE_RIGHT,
            _Keycodes.DOWN_ARROW: Commands.FORCE_DOWN,
            _Keycodes.UP_ARROW: Commands.ROTATE,
            _Keycodes.SPACE: Commands.PAUSE,
            _Keycodes.ENTER: Commands.NEW_GAME
        }

        self.events_q = Queue()

        self._keys_pressed = collections.defaultdict(_KeyEventParams)

        self.tick_thread = TickThread(self._process_pressed_keys, TICK_INTERVAL)
        self.tick_thread.start()

    def on_key_press(self, event):
        """Callback for pressed key, should be bound to GUI class"""
        command = self._keycode_to_command_map.get(event.keycode, None)
        if command is None:
            return
        pressed_key = self._keys_pressed[command]
        pressed_key.is_pressed = True
        if pressed_key.press_time is None:
            pressed_key.press_time = time.time()
        if not pressed_key.has_been_processed_once:
            self.events_q.put(ControlEvent(ControlEventType.KEY_PRESS, command))
        pressed_key.has_been_processed_once = True

    def on_key_release(self, event):
        """Callback for released key, should be bound to GUI class"""
        command = self._keycode_to_command_map.get(event.keycode, None)
        if command is None:
            return
        released_key = self._keys_pressed[command]
        released_key.is_pressed = False
        released_key.press_time = None
        released_key.has_been_processed_once = False

        if command == Commands.FORCE_DOWN:
            self.events_q.put(ControlEvent(ControlEventType.KEY_PRESS, Commands.FORCE_DOWN_CANCEL))

    def _process_pressed_keys(self):
        # Make a decision what should we do with this key
        for command, pressed_key in self._keys_pressed.items():
            if command not in self.REPEAT_COMMAND or \
                    not pressed_key.is_pressed or \
                    time.time() - pressed_key.press_time < TICK_DELAY or not pressed_key.has_been_processed_once:
                continue
            self.events_q.put(ControlEvent(ControlEventType.KEY_PRESS, command))
