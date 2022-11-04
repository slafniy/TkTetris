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

TICK_INTERVAL = 0.1

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
    #
        self.tick_thread = TickThread(self._tick, TICK_INTERVAL)
        self.tick_thread.start()
    #
    #     self._ui_root.new_game()
    #
        self._game_over = False

    def _new_game(self):
        self._repaint_all()

    def _repaint_all(self):
        pass
    #
    # def _paint_cell(self, x: int, y: int, cell: c.Cell):
    #     # Remove existing image
    #     if cell.image_id is not None:
    #         self._ui_root.delete_image(cell.image_id)
    #     # Paint new image if needed
    #     if y < FIELD_HIDDEN_TOP_ROWS_NUMBER:
    #         return  # Don't show cells on hidden rows
    #     if cell.state == c.CellState.FILLED:
    #         cell.image_id = self._ui_root.paint_filled(x, y - FIELD_HIDDEN_TOP_ROWS_NUMBER)
    #     elif cell.state == c.CellState.FALLING:
    #         cell.image_id = self._ui_root.paint_falling(x, y - FIELD_HIDDEN_TOP_ROWS_NUMBER)
    #
    # def _fix_figure(self):
    #     print("Fixing figure")
    #     for point in self._figure.current_points:
    #         self._set_cell_state_and_paint(point.x, point.y, c.CellState.FILLED)
    #     self._ui_root.refresh_ui()
    #     self._figure = None
    #
    # def _spawn_figure(self):
    #     # First, check full rows and clear them if needed
    #     self._clear_rows()
    #
    #     # Spawn new if needed
    #     if not self._game_over and self._figure is None:
    #         self._field.spawn_figure()
    #         self._ui_root.show_next_figure(self._next_figure.current_matrix())
    #         can_place = self._place(FIELD_HIDDEN_TOP_ROWS_NUMBER, 0)
    #         if can_place is False:
    #             self._game_over = True
    #             self._ui_root.game_over()
    #             self._ui_root.sounds.game_over.play()
    #             print('Cannot place new figure - game over')
    #         return can_place
    #
    # # def _place(self, x: int, y: int):
    # #
    # #     initial_points = copy.deepcopy(self._figure.current_points)
    # #     target_points = self._field.can_place(x, y, self._figure)
    # #     if target_points is None:
    # #         return False
    # #
    # #     draw_points = target_points.difference(initial_points)
    # #     clear_points = initial_points.difference(target_points)
    # #
    # #     for new_x, new_y in clear_points:
    # #         self._set_cell_state_and_paint(new_x, new_y, c.CellState.EMPTY)
    # #     for new_x, new_y in draw_points:
    # #         self._set_cell_state_and_paint(new_x, new_y, c.CellState.FALLING)
    # #
    # #     self._ui_root.refresh_ui()
    # #     return True

    def _move_left(self):
        move_result = self._field.move_left()
        if len(move_result) > 0:
            self._ui_root.sounds.move.play()
            self._ui_root.apply_field_change(move_result)

    def _move_right(self):
        move_result = self._field.move_right()
        if len(move_result) > 0:
            self._ui_root.sounds.move.play()
            self._ui_root.apply_field_change(move_result)

    def _move_down(self):
        move_result = self._field.move_down()
        if len(move_result) > 0:
            self._ui_root.sounds.tick.play()
            self._ui_root.apply_field_change(move_result)

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
        rotate_result = self._field.rotate()
        if len(rotate_result) > 0:
            self._ui_root.sounds.rotate.play()
            self._ui_root.apply_field_change(rotate_result)

    def _tick(self):
        if self.paused:
            # print("Skip tick because of pause")
            return
        if self._game_over:
            # print("Skip tick because of game over")
            return

        tick_result = self._field.tick()
        if len(tick_result) == 0:
            self._game_over = True
            self.tick_thread.stop()
        self._ui_root.sounds.tick.play()
        self._ui_root.apply_field_change(tick_result)

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
