import copy
import enum
import random
import threading

import time

import custom_threads
import figures


class CellState(enum.IntEnum):
    EMPTY = 0
    FILLED = 1
    FALLING = 2


class Cell:
    """
    Describes cell - internal state and related image id
    """

    def __init__(self):
        self.state = CellState.EMPTY
        self.image_id = None


class BusyWarning(Exception):
    def __init__(self):
        super().__init__()


class Game:
    """
    Contains information about game field
    """

    def __init__(self, *, width, height, paint_filled, paint_falling, delete_image, refresh_ui,
                 game_over_event: threading.Event):
        """
        Field constructor. Initializes field matrix, should control the game.
        :param width: How many cells one horizontal row contains
        :param height: How many cells one vertical column contains
        :param paint_filled: Function that paints filled cell on UI
        :param paint_falling: Function that paints falling cell on UI
        :param delete_image: Function that deletes image via ID
        :param game_over_event: Event that indicates that game is over
        """
        self.width = width
        self.height = height
        self.tick_interval = 0.2

        # Functions to draw and remove cells
        # TODO: write interface for this
        assert callable(paint_filled)
        assert callable(paint_falling)
        assert callable(delete_image)
        self._paint_ui_filled = paint_filled
        self._paint_ui_falling = paint_falling
        self._delete_ui_image = delete_image
        self._refresh_ui = refresh_ui

        # An internal structure to store field state (two-dimensional list)
        self._field = [[Cell() for _ in range(self.height)] for _ in range(self.width)]
        self.game_over_event = game_over_event
        # Current falling figure
        self._figure = None
        self.paused = False

        self.tick_thread = custom_threads.TickThread(self._tick, self.tick_interval, game_over_event)
        self.tick_thread.start()

        # To not allow simultaneous call of place()
        # TODO: this doesn't look smart, remade
        self._is_busy = True

    def _set_cell_state(self, x, y, state: CellState):
        if 0 <= x < self.width and 0 <= y < self.height:
            cell = self._field[x][y]
            cell.state = state
            # Remove existing image
            if cell.image_id is not None:
                self._delete_ui_image(cell.image_id)
            # Paint new image if needed
            if state == CellState.FILLED:
                cell.image_id = self._paint_ui_filled(x, y)
            elif state == CellState.FALLING:
                cell.image_id = self._paint_ui_falling(x, y)

    def _fix_figure(self):
        print("Fixing figure")
        for x, y in self._figure.current_points:
            self._set_cell_state(x, y, CellState.FILLED)
        self._refresh_ui()
        self._figure = None

    def _spawn_figure(self):
        # First, check full rows and clear them if needed
        self._clear_rows()

        # Spawn new if needed
        if not self.game_over_event.is_set() and self._figure is None:
            figure_cls = random.choice(figures.all_figures)
            self._figure = figure_cls()
            can_place = self._place()
            if can_place is False:
                self.game_over_event.set()
                print('Cannot place new figure - game over')
            return can_place

    def _place(self, point=(4, 0)):
        self._is_busy = True
        try:
            target_points = set()
            for _x, _y in self._figure.current_matrix():
                x = _x + point[0]
                y = _y + point[1]
                if not (0 <= x < self.width and 0 <= y < self.height and
                        self._field[x][y].state != CellState.FILLED):
                    # print("Cannot place figure to {}".format(point))
                    return False
                target_points.add((x, y))
            initial_points = copy.deepcopy(self._figure.current_points)
            draw_points = target_points.difference(initial_points)
            clear_points = initial_points.difference(target_points)
            self._figure.current_points = target_points

            for x, y in clear_points:
                self._set_cell_state(x, y, CellState.EMPTY)
            for x, y in draw_points:
                self._set_cell_state(x, y, CellState.FALLING)

            self._figure.position = point
            self._refresh_ui()
            # print("Figure placed to {}".format(point))
            return True
        finally:
            self._is_busy = False

    def _move(self, x_diff=0, y_diff=0):
        # print("Trying to move...")
        try:
            if self._is_busy:
                # print("place() method is busy, doing nothing!")
                raise BusyWarning()
            if self._figure is None or self._figure.position is None:
                # print("There is no figure to move")
                return False
            return self._place((self._figure.position[0] + x_diff, self._figure.position[1] + y_diff))
        except BusyWarning:
            pass

    def move_left(self):
        return self._move(x_diff=-1)

    def move_right(self):
        return self._move(x_diff=1)

    def move_down(self):
        return self._move(y_diff=1)

    def force_down(self):
        pass

    def rotate(self):
        if not self.game_over_event.is_set() and self._figure is not None:
            current_rotation = self._figure.rotation
            self._figure.set_next_rotation()
            if not self._place(self._figure.position):
                if not self._place((self._figure.position[0] - 1, self._figure.position[1])):
                    if not self._place((self._figure.position[0], self._figure.position[1] - 1)):
                        if not self._place((self._figure.position[0] - 1, self._figure.position[1] - 1)):
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
                print("Cannot move figure anymore, fixing...")
                self._fix_figure()

    def _get_full_row(self):
        for y in range(self.height - 1, -1, -1):
            is_full = True
            for x in range(self.width):
                if self._field[x][y].state != CellState.FILLED:
                    is_full = False
                    break
            if is_full:
                print("Full row:", y)
                return y
        return None

    def _clear_rows(self):
        while True:
            row_index = self._get_full_row()
            if row_index is None:
                break

            cells_to_destroy = [(x, row_index) for x in range(self.width)]
            cells_to_move_down = []
            for x in range(self.width):
                for y in range(0, row_index):
                    if self._field[x][y].state == CellState.FILLED:
                        cells_to_move_down.append((x, y))

            for x, y in cells_to_destroy:
                self._set_cell_state(x, y, CellState.EMPTY)
            self._refresh_ui()
            time.sleep(self.tick_interval / 2)

            for x, y in cells_to_move_down:
                self._set_cell_state(x, y, CellState.EMPTY)
            for x, y in cells_to_move_down:
                self._set_cell_state(x, y + 1, CellState.FILLED)
            time.sleep(self.tick_interval / 2)
            self._refresh_ui()