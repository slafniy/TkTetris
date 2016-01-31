import copy
import enum
import random
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


class Game:
    """
    Game logic
    """
    def __init__(self, field):
        self._field = field


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
    Describes cell - internal state and optional related image id
    """
    def __init__(self):
        self.state = CellState.EMPTY
        self.image_id = None
        self.repaint_me = False

    def set_state(self, state: CellState):
        if state != self.state:
            self.state = state
            self.repaint_me = True

    def get_state(self):
        return self.state


class Field:
    """
    Contains information about game field
    """
    def __init__(self, width, height, repaint_event: threading.Event):
        self.width = width
        self.height = height
        # An internal structure to store field state (two-dimensional list)
        self._field = [[Cell() for _ in range(self.height)] for _ in range(self.width)]
        self._lock = threading.Lock()
        self._repaint_event = repaint_event
        # Current falling figure
        self._figure = None
        self.game_over = False
        self.paused = False

    def get_cell_params(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            with self._lock:
                cell = self._field[x][y]
                return cell.get_state(), cell.image_id, cell.repaint_me
        else:
            raise AttributeError("There is no cell {}, {}".format(x, y))

    def set_cell_params(self, x, y, state, image_id, repaint_me):
        if 0 <= x < self.width and 0 <= y < self.height:
            with self._lock:
                self._field[x][y].state = state
                self._field[x][y].image_id = image_id
                self._field[x][y].repaint_me = repaint_me
        else:
            raise AttributeError("There is no cell {}, {}".format(x, y))

    def fix_figure(self):
        with self._lock:
            for x, y in self._figure.current_points:
                self._field[x][y].set_state(CellState.FILLED)
            self._repaint_event.points = self._figure.current_points
            self._repaint_event.set()
            self._figure = None

    def spawn_figure(self):
        if self._figure is None:
            # figure_cls = random.choice((ZFigure, ))
            # self._figure = figure_cls()
            self._figure = ZFigure()  # TODO: make it random
            can_place = self.place()
            if can_place is False:
                self.game_over = True
                print('Cannot place new figure - game over')
            self._repaint_event.set()
            return can_place

    def place(self, point=(4, 0)):
        with self._lock:
            target_points = set()
            for _x, _y in self._figure.current_matrix():
                x = _x + point[0]
                y = _y + point[1]
                if not (0 <= x < self.width and 0 <= y < self.height and
                        self._field[x][y].get_state() != CellState.FILLED):
                    print("Cannot place figure to {}".format(point))
                    return False
                target_points.add((x, y))
            initial_points = copy.deepcopy(self._figure.current_points)
            draw_points = target_points.difference(initial_points)
            repaint_points = target_points.union(initial_points)
            clear_points = initial_points.difference(target_points)
            self._figure.current_points = target_points

            for x, y in clear_points:
                self._field[x][y].set_state(CellState.EMPTY)
            for x, y in draw_points:
                self._field[x][y].set_state(CellState.FALLING)

            self._figure.position = point
            self._repaint_event.set()
            print("Figure placed to {}".format(point))
            return True

    def _print_field(self):
        # TODO: remove
        for y in range(20):
            print("")
            for x in range(10):
                print(self._field[x][y].state._value_, end="")
        print("")

    def _move(self, x_diff=0, y_diff=0):
        print("Trying to move...")
        if self._figure is None or self._figure.position is None:
            print("There is no figure to move")
            return False
        return self.place((self._figure.position[0] + x_diff, self._figure.position[1] + y_diff))

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
        if self.game_over:
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