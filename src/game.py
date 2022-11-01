import copy
import random
import threading
import time
import typing as t

import cell as c
import custom_threads
import field
import figures as f
import keyboard_handler as kbh
from abstract_ui import AbstractUI

TICK_INTERVAL = 0.5

# Default field parameters
FIELD_HIDDEN_TOP_ROWS_NUMBER = 4
FIELD_HEIGHT = 20  # In cells
FIELD_WIDTH = 10  # In cells


class BusyWarning(Exception):
    def __init__(self):
        super().__init__()


class Game:
    """
    Contains information about game field
    """

    def __init__(self, *, width=FIELD_WIDTH, height=FIELD_HEIGHT + FIELD_HIDDEN_TOP_ROWS_NUMBER,
                 game_over_event: threading.Event, keyboard_handler: kbh.KeyboardHandler, ui_root: AbstractUI):
        """
        Field constructor. Initializes field matrix, should control the game.
        :param width: How many cells one horizontal row contains
        :param height: How many cells one vertical column contains
        :param game_over_event: Event that indicates that game is over
        """

        # Bind keyboard handler to Field methods
        self._keyboard_handler = keyboard_handler
        self._keyboard_handler.move_left_func = self.move_left
        self._keyboard_handler.move_right_func = self.move_right
        self._keyboard_handler.force_down_func = self.force_down
        self._keyboard_handler.force_down_cancel_func = self.force_down_cancel
        self._keyboard_handler.rotate_func = self.rotate
        self._keyboard_handler.pause_func = self.pause

        self._ui_root = ui_root

        self._field = field.Field(height, width)  # An internal structure to store field state (two-dimensional list)
        self.game_over_event = game_over_event
        self._figure: t.Optional[f.Figure] = None  # Current falling figure
        self._next_figure: t.Optional[f.Figure] = random.choice(f.all_figures)()  # Next figure to spawn
        self._ui_root.show_next_figure(self._next_figure.current_matrix())

        self.paused = False

        self.tick_thread = custom_threads.TickThread(self._tick, TICK_INTERVAL, game_over_event)
        self.tick_thread.start()

        self._ui_root.new_game()

        # To not allow simultaneous call of place()
        # TODO: this doesn't look smart, remade
        self._is_busy = True

    def _set_cell_state(self, point: f.Point, state: c.CellState):
        cell = self._field.set_cell_state(point, state)
        # Remove existing image
        if cell.image_id is not None:
            self._ui_root.delete_image(cell.image_id)
        # Paint new image if needed
        if point.y < FIELD_HIDDEN_TOP_ROWS_NUMBER:
            return  # Don't show cells on hidden rows
        if state == c.CellState.FILLED:
            cell.image_id = self._ui_root.paint_filled(point.x, point.y - FIELD_HIDDEN_TOP_ROWS_NUMBER)
        elif state == c.CellState.FALLING:
            cell.image_id = self._ui_root.paint_falling(point.x, point.y - FIELD_HIDDEN_TOP_ROWS_NUMBER)

    def _fix_figure(self):
        print("Fixing figure")
        for point in self._figure.current_points:
            self._set_cell_state(point, c.CellState.FILLED)
        self._ui_root.refresh_ui()
        self._figure = None

    def _spawn_figure(self):
        # First, check full rows and clear them if needed
        self._clear_rows()

        # Spawn new if needed
        if not self.game_over_event.is_set() and self._figure is None:
            self._figure = self._next_figure
            self._next_figure = random.choice(f.all_figures)()
            self._ui_root.show_next_figure(self._next_figure.current_matrix())
            can_place = self._place(f.Point(4, 0))
            if can_place is False:
                self.game_over_event.set()
                self._ui_root.game_over()
                self._ui_root.sounds.game_over.play()
                print('Cannot place new figure - game over')
            return can_place

    def _place(self, point: f.Point):
        self._is_busy = True
        try:
            target_points = set()
            if self._figure is None:  # TODO: fix. _place() should use lock
                return False
            for _x, _y in self._figure.current_matrix():
                x = _x + point[0]
                y = _y + point[1]
                if not (0 <= x < self._field.width and 0 <= y < self._field.height and
                        self._field[x][y].state != c.CellState.FILLED):
                    # print("Cannot place figure to {}".format(point))
                    return False
                target_points.add(f.Point(x, y))
            initial_points = copy.deepcopy(self._figure.current_points)
            draw_points = target_points.difference(initial_points)
            clear_points = initial_points.difference(target_points)
            self._figure.current_points = target_points

            for x, y in clear_points:
                self._set_cell_state(f.Point(x, y), c.CellState.EMPTY)
            for x, y in draw_points:
                self._set_cell_state(f.Point(x, y), c.CellState.FALLING)

            self._figure.position = point
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
            return self._place(f.Point(self._figure.position[0] + x_diff, self._figure.position[1] + y_diff))
        except BusyWarning:
            pass

    def move_left(self):
        self._ui_root.sounds.move.play()
        return self._move(x_diff=-1)

    def move_right(self):
        self._ui_root.sounds.move.play()
        return self._move(x_diff=1)

    def move_down(self):
        self._ui_root.sounds.tick.play()
        return self._move(y_diff=1)

    def force_down(self):
        self.tick_thread.set_tick(TICK_INTERVAL / 10)

    def force_down_cancel(self):
        self.tick_thread.set_tick(TICK_INTERVAL)

    def pause(self):
        self.paused = not self.paused
        self._ui_root.toggle_pause()

    def rotate(self):
        if self.paused:
            return
        if not self.game_over_event.is_set() and self._figure is not None:
            current_rotation = self._figure.rotation
            self._figure.set_next_rotation()
            self._ui_root.sounds.rotate.play()
            if not self._place(self._figure.position):
                if not self._place(f.Point(self._figure.position[0] - 1, self._figure.position[1])):
                    if not self._place(f.Point(self._figure.position[0], self._figure.position[1] - 1)):
                        if not self._place(f.Point(self._figure.position[0] - 1, self._figure.position[1] - 1)):
                            self._figure.rotation = current_rotation

    def _tick(self):
        if self.paused:
            # print("Skip tick because of pause")
            return
        if self.game_over_event.is_set():
            # print("Skip tick because of game over")
            return

        if self._figure is None:
            print("Trying to spawn new figure")
            self._spawn_figure()
        else:
            # print("Trying to move down current figure")
            can_move = self.move_down()
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
                self._set_cell_state(f.Point(x, y), c.CellState.EMPTY)
            self._ui_root.refresh_ui()
            self._ui_root.sounds.row_delete.play()
            time.sleep(TICK_INTERVAL / 2)

            for x, y in cells_to_move_down:
                self._set_cell_state(f.Point(x, y), c.CellState.EMPTY)
            for x, y in cells_to_move_down:
                self._set_cell_state(f.Point(x, y + 1), c.CellState.FILLED)
            time.sleep(TICK_INTERVAL / 2)
            self._ui_root.refresh_ui()
