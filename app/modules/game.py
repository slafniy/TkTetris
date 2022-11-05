"""Main place for game logic"""
from functools import lru_cache

from .tick_thread import TickThread
from .field import FieldEventType, Field
from .controls_handler import ControlEventType, ControlsHandler, Commands
from .abstract_ui import AbstractGUI
from .logger import logger

TICK_INTERVAL = 0.8
LEVEL_DECREASE = 0.025

# Default field parameters
FIELD_HIDDEN_TOP_ROWS_NUMBER = 4
FIELD_HEIGHT = 20  # In cells
FIELD_WIDTH = 10  # In cells


class Game:  # pylint: disable=too-few-public-methods, too-many-instance-attributes
    """
    Contains information about game logic
    """

    def __init__(self, *, width=FIELD_WIDTH, height=FIELD_HEIGHT + FIELD_HIDDEN_TOP_ROWS_NUMBER,
                 controls_handler: ControlsHandler, gui: AbstractGUI):
        """
        :param width: How many cells one horizontal row contains
        :param height: How many cells one vertical column contains
        """
        self._controls_handler = controls_handler
        self.gui = gui
        self._field = Field(width, height)  # An internal structure to store field state (two-dimensional list)

        self._current_tick = TICK_INTERVAL
        self.paused = False
        self._game_over = False
        self._forcing_speed = False
        self._score = 0

        self._controls_poller_thread = TickThread(self._poll_next_control_event, tick_interval_sec=0.001,
                                                  startup_sleep_sec=0)
        self._controls_poller_thread.start()

        self.tick_thread = TickThread(self._tick, TICK_INTERVAL)
        self.tick_thread.start()

        self._cell_updater_thread = TickThread(self._poll_next_field_event, tick_interval_sec=0.001,
                                               startup_sleep_sec=0)
        self._cell_updater_thread.start()

    def _poll_next_control_event(self):
        event = self._controls_handler.events_q.get()
        logger.debug(f'Control event: {event}')
        if event.event_type == ControlEventType.KEY_PRESS:
            {
                Commands.MOVE_LEFT: self._on_move_left,
                Commands.MOVE_RIGHT: self._on_move_right,
                Commands.ROTATE: self._on_rotate,
                Commands.FORCE_DOWN: self._on_force_down,
                Commands.FORCE_DOWN_CANCEL: self._on_force_down_cancel,
                Commands.PAUSE: self._on_pause,
                Commands.NEW_GAME: self._on_new_game
            }[event.payload]()

    def _poll_next_field_event(self):
        if not self._game_over:
            event = self._field.events_q.get()
            # logger.debug(f'Event received, type={event.event_type}')

            # Apply changes on the game field
            if event.event_type == FieldEventType.CELL_STATE_CHANGE:
                self.gui.apply_field_change(event.payload)

            # We got full row here
            elif event.event_type == FieldEventType.ROW_REMOVED:
                self.gui.sounds.row_delete.play()
                self._current_tick = self._current_tick \
                    if self._current_tick <= LEVEL_DECREASE else self._current_tick - LEVEL_DECREASE
                if not self._forcing_speed:
                    self.tick_thread.set_tick(self._current_tick)
                self._score += 10
                self.gui.show_score(self._score)

            # Figure hit the bottom
            elif event.event_type == FieldEventType.FIGURE_FIXED:
                self.gui.sounds.fix_figure.play()

            # Game over
            elif event.event_type == FieldEventType.GAME_OVER:
                self._game_over = True
                self.tick_thread.stop()
                self.gui.sounds.game_over.play()

            # Next figure known
            elif event.event_type == FieldEventType.NEW_FIGURE:
                self.gui.show_next_figure(event.payload)

    def _on_new_game(self):
        pass

    def _on_move_left(self):
        self._field.move_left()
        self.gui.sounds.move.play()

    def _on_move_right(self):
        self._field.move_right()
        self.gui.sounds.move.play()

    def _on_force_down(self):
        self._forcing_speed = True
        new_tick = _calc_force_down_tick(self._current_tick)
        # logger.debug(f'SPEEDUP: {self._current_tick} => {new_tick}')
        self.tick_thread.set_tick(new_tick)

    def _on_force_down_cancel(self):
        self._forcing_speed = False
        self.tick_thread.set_tick(self._current_tick)

    def _on_pause(self):
        self.paused = not self.paused
        self.gui.toggle_pause()

    def _on_rotate(self):
        if self.paused or self._game_over:
            return
        if self._field.rotate():
            self.gui.sounds.rotate.play()

    def _tick(self):
        if self.paused or self._game_over:
            return

        self._field.tick()
        self.gui.sounds.tick.play()


@lru_cache
def _calc_force_down_tick(basic_tick: float) -> float:
    """doesn't go lower than 0.01 sec ()
     - in this case will be equal to tick."""
    k = 0.15
    # basic_tick_limit = 0.15
    high_speed_tick = basic_tick * k
    # high_speed_tick = basic_tick if high_speed_tick < limit else high_speed_tick
    return high_speed_tick
