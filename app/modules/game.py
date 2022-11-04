"""Main place for game logic"""
import copy
import random
import time
import typing as t
from functools import lru_cache

from . import cell as c
from .tick_thread import TickThread
from . import field
from . import figures as f
from . import controls_handler as ch
from .abstract_ui import AbstractUI
from .logger import logger

TICK_INTERVAL = 0.8
LEVEL_MULTIPLIER = 0.9

# Default field parameters
FIELD_HIDDEN_TOP_ROWS_NUMBER = 4
FIELD_HEIGHT = 20  # In cells
FIELD_WIDTH = 10  # In cells


class Game:
    """
    Contains information about game logic
    """

    def __init__(self, *, width=FIELD_WIDTH, height=FIELD_HEIGHT + FIELD_HIDDEN_TOP_ROWS_NUMBER,
                 controls_handler: ch.ControlsHandler, ui_root: AbstractUI):
        """
        :param width: How many cells one horizontal row contains
        :param height: How many cells one vertical column contains
        """

        # Bind controls handler to Field methods
        self._controls_handler = controls_handler
        self._controls_handler.move_left_func = self._move_left
        self._controls_handler.move_right_func = self._move_right
        self._controls_handler.force_down_func = self._force_down
        self._controls_handler.force_down_cancel_func = self._force_down_cancel
        self._controls_handler.rotate_func = self._rotate
        self._controls_handler.pause_func = self._pause
        self._controls_handler.new_game_func = self._new_game
        self._controls_handler.skin_change_func = self._repaint_all

        self._ui_root = ui_root

        self._field = field.Field(width, height)  # An internal structure to store field state (two-dimensional list)

        self._current_tick = TICK_INTERVAL

        self.paused = False
        self._game_over = False

        self.tick_thread = TickThread(self._tick, TICK_INTERVAL)
        self.tick_thread.start()

        self._cell_updater_thread = TickThread(self._update_cells, tick_interval_sec=0.001, startup_sleep_sec=0)
        self._cell_updater_thread.start()

    def _update_cells(self):
        while not self._game_over:
            patch = self._field.graphic_events_q.get()
            self._ui_root.apply_field_change(patch)

    def _new_game(self):
        self._repaint_all()

    def _repaint_all(self):
        pass

    def _move_left(self):
        if self._field.move_left():
            self._ui_root.sounds.move.play()

    def _move_right(self):
        if self._field.move_right():
            self._ui_root.sounds.move.play()

    def _force_down(self):
        new_tick = self._calc_force_down_tick(self._current_tick)
        logger.debug(f'SPEEDUP: {self._current_tick} => {new_tick}')
        self.tick_thread.set_tick(new_tick)

    def _force_down_cancel(self):
        self.tick_thread.set_tick(TICK_INTERVAL)

    @staticmethod
    @lru_cache
    def _calc_force_down_tick(basic_tick: float) -> float:
        """doesn't go lower than 0.01 sec ()
         - in this case will be equal to tick."""
        k = 0.045
        limit = 0.01
        high_speed_tick = basic_tick * k
        high_speed_tick = basic_tick if high_speed_tick < limit else high_speed_tick
        return high_speed_tick

    def _pause(self):
        self.paused = not self.paused
        self._ui_root.toggle_pause()

    def _rotate(self):
        if self.paused or self._game_over:
            return
        if self._field.rotate():
            self._ui_root.sounds.rotate.play()

    def _tick(self):
        if self.paused or self._game_over:
            return

        if not self._field.tick():
            self._game_over = True
            self.tick_thread.stop()
        self._ui_root.sounds.tick.play()