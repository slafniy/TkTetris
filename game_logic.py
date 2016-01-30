import copy
import enum
import threading
import time

import field_impl


class Game:
    """
    Game logic
    """
    def __init__(self, field: field_impl.Field):
        self._field = field
        self._figure = None
        self.fix_on_the_next_step = False

    def spawn_z(self):
        self._figure = ZFigure(self._field)
        if self._figure.place(4, 0):
            return True
        else:
            self._figure = None
            return False

    def next_step(self):
        if self._figure is not None:
            if self.fix_on_the_next_step:
                self.fix_figure()
                self.spawn_z()
                self.fix_on_the_next_step = False
                return
            if self._figure.place(self._figure.position[0], self._figure.position[1]):
                self._figure.position[1] += 1
            else:
                print('Cannot step, fixing figure and spawning the next on the next step')
                self.fix_on_the_next_step = True

    def fix_figure(self):
        """
        Adds current figure points as filled points in field and clears current points
        """
        points_to_fill = copy.deepcopy(self._figure.current_points)
        for x, y in points_to_fill:
            cell = self._field.get_cell(x, y)
            cell.state = field_impl.CellState.FILLED
            cell.need_img_replace = True
        self._figure = None

    def move_left(self):
        if self._figure is not None:
            self._figure.place(self._figure.position[0] - 1, self._figure.position[1])

    def move_right(self):
        if self._figure is not None:
            self._figure.place(self._figure.position[0] + 1, self._figure.position[1])


class Rotation(enum.Enum):
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3


class Figure:
    """
    Saves a set of figure points and rules of rotation
    """
    def __init__(self, field: field_impl.Field):
        self._field = field
        # self._matrix1 = set()
        # self._matrix2 = set()
        # self._matrix3 = set()
        # self._matrix4 = set()
        self._matrix = {}  # set() of points for each Rotation
        self._rotation = Rotation.NORTH
        self.current_points = []
        self.position = None

    def place(self, x, y):
        """
        Tries to place figure on field
        :param y:
        :param x:
        :return: returns True if figure placed and False if it's impossible
        """
        # print("Trying to place figure to ({}, {})".format(x, y))
        points = []
        for _x, _y in self._matrix[self._rotation]:
            cell = self._field.get_cell(_x + x, _y + y)
            if cell is None or cell.state == field_impl.CellState.FILLED:
                return False
            else:
                points.append((_x + x, _y + y))
        # Add new position
        for _x, _y in points:
            self._field.get_cell(_x, _y).state = field_impl.CellState.FALLING
        # Remove old position
        for _x, _y in self.current_points:
            if (_x, _y) not in points:
                self._field.get_cell(_x, _y).state = field_impl.CellState.EMPTY
        # print('Figure placed to {}, {}'.format(x, y))
        self.current_points = points
        self.position = [x, y]
        return True

    def rotate_right(self):
        pass

    def rotate_left(self):
        raise NotImplementedError("Left rotation in not implemented yet")


class ZFigure(Figure):
    """
    Represents "Z" figure
    """
    def __init__(self, field):
        super().__init__(field)
        self._matrix = {Rotation.NORTH: {(0, 0), (1, 0), (1, 1), (2, 1)}}
        # self._matrix1 = self._matrix3 = {(0, 0), (1, 0), (1, 1), (2, 1)}
        # self._matrix2 = self._matrix4 = {(1, 0), (1, 1), (0, 1), (0, 2)}


class TickThread(threading.Thread):
    """
    Special thread that endlessly run tick_function and can be stopped correctly
    """
    def __init__(self, tick_function, tick_interval_sec=1):
        # self._control_tick_interval = 0.01
        # assert tick_interval_sec >= self._control_tick_interval, \
        #     "Tick interval shouldn't be less than {} sec".format(self._control_tick_interval)
        self.tick_interval = tick_interval_sec
        super().__init__(target=tick_function)
        self._stop_event = threading.Event()
        self._time_counter = 0

    def stop(self):
        self._stop_event.set()

    def run(self):
        while not self._stop_event.is_set():
            start_time = time.time()
            self._target()
            self._time_counter = 0
            sleep_time = self.tick_interval - time.time() + start_time
            # print(sleep_time)
            time.sleep(sleep_time)