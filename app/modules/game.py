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

TICK_INTERVAL = 0.5

# Default field parameters
FIELD_HIDDEN_TOP_ROWS_NUMBER = 4
FIELD_HEIGHT = 20  # In cells
FIELD_WIDTH = 10  # In cells


class BusyWarning(Exception):
    pass


class Game:
    """
    Contains information about game field
    """

    def __init__(self, *, width=FIELD_WIDTH, height=FIELD_HEIGHT + FIELD_HIDDEN_TOP_ROWS_NUMBER,
                 controls_handler: ch.ControlsHandler, ui_root: AbstractUI):
        """
        Field constructor. Initializes field matrix, should control the game.
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
        self._figure: t.Optional[f.Figure] = None  # Current falling figure
        self._next_figure: t.Optional[f.Figure] = random.choice(f.all_figures)()  # Next figure to spawn
        self._ui_root.show_next_figure(self._next_figure.current_matrix())

        self.paused = False

        self.tick_thread = TickThread(self._tick, TICK_INTERVAL)
        self.tick_thread.start()

        self._ui_root.new_game()

        # To not allow simultaneous call of place()
        # TODO: this doesn't look smart, remade
        self._is_busy = True
        self._game_over = False

    def _new_game(self):
        self._repaint_all()

    def _repaint_all(self):
        self._pause()
        logger.debug('Field to repaint: %s', str(self._field))
        self._ui_root.show_next_figure(self._next_figure.current_matrix())
        for x, row in enumerate(self._field):
            for y, cell in enumerate(row):
                self._paint_cell(x, y, cell)
        self._ui_root.refresh_ui()
        self._pause()

    def _set_cell_state_and_paint(self, x: int, y: int, state: c.CellState):
        cell = self._field[x][y]
        cell.state = state
        self._paint_cell(x, y, cell)

    def _paint_cell(self, x: int, y: int, cell: c.Cell):
        # Remove existing image
        if cell.image_id is not None:
            self._ui_root.delete_image(cell.image_id)
        # Paint new image if needed
        if y < FIELD_HIDDEN_TOP_ROWS_NUMBER:
            return  # Don't show cells on hidden rows
        if cell.state == c.CellState.FILLED:
            cell.image_id = self._ui_root.paint_filled(x, y - FIELD_HIDDEN_TOP_ROWS_NUMBER)
        elif cell.state == c.CellState.FALLING:
            cell.image_id = self._ui_root.paint_falling(x, y - FIELD_HIDDEN_TOP_ROWS_NUMBER)

    def _fix_figure(self):
        print("Fixing figure")
        for point in self._figure.current_points:
            self._set_cell_state_and_paint(point.x, point.y, c.CellState.FILLED)
        self._ui_root.refresh_ui()
        self._figure = None

    def _spawn_figure(self):
        # First, check full rows and clear them if needed
        self._clear_rows()

        # Spawn new if needed
        if not self._game_over and self._figure is None:
            self._figure = self._next_figure
            self._next_figure = random.choice(f.all_figures)()
            self._ui_root.show_next_figure(self._next_figure.current_matrix())
            can_place = self._place(FIELD_HIDDEN_TOP_ROWS_NUMBER, 0)
            if can_place is False:
                self._game_over = True
                self._ui_root.game_over()
                self._ui_root.sounds.game_over.play()
                print('Cannot place new figure - game over')
            return can_place

    def _place(self, x: int, y: int):
        self._is_busy = True
        try:
            initial_points = copy.deepcopy(self._figure.current_points)
            target_points = self._field.can_place(x, y, self._figure)
            if target_points is None:
                return False

            draw_points = target_points.difference(initial_points)
            clear_points = initial_points.difference(target_points)

            for new_x, new_y in clear_points:
                self._set_cell_state_and_paint(new_x, new_y, c.CellState.EMPTY)
            for new_x, new_y in draw_points:
                self._set_cell_state_and_paint(new_x, new_y, c.CellState.FALLING)

            self._ui_root.refresh_ui()
            return True
        finally:
            self._is_busy = False

    def _move(self, x_diff=0, y_diff=0):
        if self.paused:
            return
        try:
            if self._is_busy:
                raise BusyWarning()
            if self._figure is None or self._figure.position is None:
                return False
            return self._place(self._figure.position[0] + x_diff, self._figure.position[1] + y_diff)
        except BusyWarning:
            pass

    def _move_left(self):
        self._ui_root.sounds.move.play()
        return self._move(x_diff=-1)

    def _move_right(self):
        self._ui_root.sounds.move.play()
        return self._move(x_diff=1)

    def _move_down(self):
        self._ui_root.sounds.tick.play()
        return self._move(y_diff=1)

    def _force_down(self):
        self.tick_thread.set_tick(TICK_INTERVAL / 10)

    def _force_down_cancel(self):
        self.tick_thread.set_tick(TICK_INTERVAL)

    def _pause(self):
        self.paused = not self.paused
        self._ui_root.toggle_pause()

    def _rotate(self):
        if self.paused:
            return
        if not self._game_over and self._figure is not None:
            current_rotation = self._figure.rotation
            self._figure.set_next_rotation()
            self._ui_root.sounds.rotate.play()
            if not self._place(self._figure.position.x, self._figure.position.y):
                if not self._place(self._figure.position[0] - 1, self._figure.position[1]):
                    if not self._place(self._figure.position[0], self._figure.position[1] - 1):
                        if not self._place(self._figure.position[0] - 1, self._figure.position[1] - 1):
                            self._figure.rotation = current_rotation

    def _tick(self):
        if self.paused:
            # print("Skip tick because of pause")
            return
        if self._game_over:
            # print("Skip tick because of game over")
            return

        if self._figure is None:
            print("Trying to spawn new figure")
            self._spawn_figure()
        else:
            # print("Trying to move down current figure")
            can_move = self._move_down()
            if can_move is False:
                self._fix_figure()
                self._ui_root.sounds.fix_figure.play()

    def _clear_rows(self):
        while True:
            row_index = self._field.get_full_row()
            if row_index is None:
                break

            cells_to_destroy = [(x, row_index) for x in range(self._field.width)]
            cells_to_move_down = []
            for x in range(self._field.width):
                for y in range(0, row_index):
                    if self._field[x][y].state == c.CellState.FILLED:
                        cells_to_move_down.append((x, y))

            for x, y in cells_to_destroy:
                self._set_cell_state_and_paint(x, y, c.CellState.EMPTY)
            self._ui_root.refresh_ui()
            self._ui_root.sounds.row_delete.play()
            time.sleep(TICK_INTERVAL / 2)

            for x, y in cells_to_move_down:
                self._set_cell_state_and_paint(x, y, c.CellState.EMPTY)
            for x, y in cells_to_move_down:
                self._set_cell_state_and_paint(x, y + 1, c.CellState.FILLED)
            time.sleep(TICK_INTERVAL / 2)
            self._ui_root.refresh_ui()
