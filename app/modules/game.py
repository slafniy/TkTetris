"""Main place for game logic"""
from functools import lru_cache

from .tick_thread import TickThread
from .field import FieldEventType, Field
from . import controls_handler as ch
from .abstract_ui import AbstractUI
from .logger import logger

TICK_INTERVAL = 0.68
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

        self._field = Field(width, height)  # An internal structure to store field state (two-dimensional list)

        self._current_tick = TICK_INTERVAL

        self.paused = False
        self._game_over = False
        self._forcing_speed = False

        self.tick_thread = TickThread(self._tick, TICK_INTERVAL)
        self.tick_thread.start()

        self._cell_updater_thread = TickThread(self._poll_next_field_event, tick_interval_sec=0.001, startup_sleep_sec=0)
        self._cell_updater_thread.start()

    def _poll_next_field_event(self):
        if not self._game_over:
            event = self._field.events_q.get()
            # logger.debug(f'Event received, type={event.event_type}')

            # Apply changes on the game field
            if event.event_type == FieldEventType.CELL_STATE_CHANGE:
                self._ui_root.apply_field_change(event.payload)

            # We got full row here
            elif event.event_type == FieldEventType.ROW_REMOVED:
                self._ui_root.sounds.row_delete.play()
                self._current_tick *= LEVEL_MULTIPLIER
                if not self._forcing_speed:
                    self.tick_thread.set_tick(self._current_tick)

            # Figure hit the bottom
            elif event.event_type == FieldEventType.FIGURE_FIXED:
                pass #self._force_down_cancel()  # to avoid smashing the next one

            # Game over
            elif event.event_type == FieldEventType.GAME_OVER:
                self._game_over = True
                self.tick_thread.stop()
                self._ui_root.sounds.game_over.play()

            # Next figure known
            elif event.event_type == FieldEventType.NEW_FIGURE:
                self._ui_root.show_next_figure(event.payload)

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
        self._forcing_speed = True
        new_tick = self._calc_force_down_tick(self._current_tick)
        logger.debug(f'SPEEDUP: {self._current_tick} => {new_tick}')
        self.tick_thread.set_tick(new_tick)

    def _force_down_cancel(self):
        self._forcing_speed = False
        self.tick_thread.set_tick(self._current_tick)

    @staticmethod
    @lru_cache
    def _calc_force_down_tick(basic_tick: float) -> float:
        """doesn't go lower than 0.01 sec ()
         - in this case will be equal to tick."""
        k = 0.15
        # basic_tick_limit = 0.15
        high_speed_tick = basic_tick * k
        # high_speed_tick = basic_tick if high_speed_tick < limit else high_speed_tick
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

        self._field.tick()
        self._ui_root.sounds.tick.play()