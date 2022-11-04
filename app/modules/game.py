"""Main place for game logic"""
import copy
import random
import time
import typing as t

from . import cell as c
from .tick_thread import TickThread
from . import field
from . import figures as f
from . import controls_handler as ch
from .abstract_ui import AbstractUI
from .logger import logger

TICK_INTERVAL = 0.15

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

    #     self._ui_root.show_next_figure(self._next_figure.current_matrix())
    #
        # self._field.spawn_figure()
        self.paused = False
        self._game_over = False
    #
        self.tick_thread = TickThread(self._tick, TICK_INTERVAL)
        self.tick_thread.start()

        self._cell_updater_thread = TickThread(self._update_cells, tick_interval_sec=TICK_INTERVAL / 2,
                                               startup_sleep_sec=0)
        self._cell_updater_thread.start()
    #
    #     self._ui_root.new_game()
    #

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
        pass
        # self.tick_thread.set_tick(TICK_INTERVAL / 10)

    def _force_down_cancel(self):
        pass
        # self.tick_thread.set_tick(TICK_INTERVAL)

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

    #
    # def _clear_rows(self):
    #     while True:
    #         row_index = self._field.get_full_row()
    #         if row_index is None:
    #             break
    #
    #         cells_to_destroy = [(x, row_index) for x in range(self._field.width)]
    #         cells_to_move_down = []
    #         for x in range(self._field.width):
    #             for y in range(0, row_index):
    #                 if self._field.get(x, y).state == c.CellState.FILLED:
    #                     cells_to_move_down.append((x, y))
    #
    #         for x, y in cells_to_destroy:
    #             self._set_cell_state_and_paint(x, y, c.CellState.EMPTY)
    #         self._ui_root.refresh_ui()
    #         self._ui_root.sounds.row_delete.play()
    #         time.sleep(TICK_INTERVAL / 2)
    #
    #         for x, y in cells_to_move_down:
    #             self._set_cell_state_and_paint(x, y, c.CellState.EMPTY)
    #         for x, y in cells_to_move_down:
    #             self._set_cell_state_and_paint(x, y + 1, c.CellState.FILLED)
    #         time.sleep(TICK_INTERVAL / 2)
    #         self._ui_root.refresh_ui()
