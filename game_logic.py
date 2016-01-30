import copy
import enum
import threading


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
        self._matrix = {}  # set() of points for each Rotation
        self._rotation = Rotation.NORTH
        self.current_points = []
        self.position = None


class ZFigure(Figure):
    """
    Represents "Z" figure
    """
    def __init__(self):
        super().__init__()
        self._matrix = {Rotation.NORTH: {(0, 0), (1, 0), (1, 1), (2, 1)}}


class Cell:
    """
    Describes cell - internal state and optional related image id
    """
    def __init__(self):
        self.state = CellState.EMPTY
        self.image_id = None
        self.need_img_replace = False


class Field:
    """
    Contains information about game field
    """
    def __init__(self, width, height):
        self.width = width
        self.height = height
        # An internal structure to store field state (two-dimensional list)
        self._field = [[Cell() for _ in range(self.height)] for _ in range(self.width)]
        self._lock = threading.Lock()

    def get_cell_copy(self, x, y):
        """
        :param x: horizontal coordinate
        :param y: vertical coordinate
        :return: Cell copy or None
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            return copy.deepcopy(self._field[x][y])
        else:
            return None

    def set_cell_state(self, x, y, state):
        if 0 <= x < self.width and 0 <= y < self.height:
            with self._lock:
                self._field[x][y].state = state

    def set_cell_image_id(self, x, y, image_id):
        if 0 <= x < self.width and 0 <= y < self.height:
            with self._lock:
                self._field[x][y].image_id = image_id

    def set_cell_need_img_replace(self, x, y, need_img_replace: bool):
        if 0 <= x < self.width and 0 <= y < self.height:
            with self._lock:
                self._field[x][y].need_img_replace = need_img_replace

    def fix_figure(self):
        pass

    def spawn_figure(self):
        pass

    def move_left(self):
        pass

    def move_right(self):
        pass

    def move_down(self):
        pass