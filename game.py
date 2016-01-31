import copy
import enum
import threading

import custom_threads


class Rotation(enum.Enum):
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3


class CellState(enum.Enum):
    EMPTY = 0
    FILLED = 1
    FALLING = 2


class Figure:
    """
    Saves a set of figure points and rules of rotation
    """
    def __init__(self):
        self.matrix = {}  # set() of points for each Rotation
        self.rotation = Rotation.NORTH
        self.current_points = set()
        self.position = None

    def current_matrix(self):
        return self.matrix.get(self.rotation, set())


class ZFigure(Figure):
    """
    Represents "Z" figure
    """
    def __init__(self):
        print("Creating Z-figure...")
        super().__init__()
        self.matrix = {Rotation.NORTH: {(0, 0), (1, 0), (1, 1), (2, 1)}}


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

        self.tick_thread = custom_threads.TickThread(self.tick, 0.5, game_over_event)
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

    def fix_figure(self):
        print("Fixing figure")
        for x, y in self._figure.current_points:
            self._set_cell_state(x, y, CellState.FILLED)
        self._refresh_ui()
        self._figure = None

    def spawn_figure(self):
        if self._figure is None:
            # figure_cls = random.choice((ZFigure, ))
            # self._figure = figure_cls()
            self._figure = ZFigure()  # TODO: make it random
            can_place = self.place()
            if can_place is False:
                self.game_over_event.set()
                print('Cannot place new figure - game over')
            return can_place

    def place(self, point=(4, 0)):
        self._is_busy = True
        try:
            target_points = set()
            for _x, _y in self._figure.current_matrix():
                x = _x + point[0]
                y = _y + point[1]
                if not (0 <= x < self.width and 0 <= y < self.height and
                        self._field[x][y].state != CellState.FILLED):
                    print("Cannot place figure to {}".format(point))
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
            print("Figure placed to {}".format(point))
            return True
        finally:
            self._is_busy = False

    def _move(self, x_diff=0, y_diff=0):
        print("Trying to move...")
        try:
            if self._is_busy:
                print("place() method is busy, doing nothing!")
                raise BusyWarning()
            if self._figure is None or self._figure.position is None:
                print("There is no figure to move")
                return False
            return self.place((self._figure.position[0] + x_diff, self._figure.position[1] + y_diff))
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

    def tick(self):
        if self.paused:
            print("Skip tick because of pause")
            return
        if self.game_over_event.is_set():
            print("Skip tick because of game over")
            return

        if self._figure is None:
            print("Trying to spawn new figure")
            self.spawn_figure()
        else:
            print("Trying to move down current figure")
            can_move = self.move_down()
            if can_move is False:
                print("Cannot move figure anymore, fixing...")
                self.fix_figure()