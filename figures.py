import enum
import random


class Rotation(enum.IntEnum):
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3


class Figure:
    """
    Saves a set of figure points and rules of rotation
    """
    def __init__(self):
        self.matrix = {}  # set() of points for each Rotation
        self.rotation = random.choice([e for e in Rotation])
        self.current_points = set()
        self.position = None

    def current_matrix(self):
        return self.matrix.get(self.rotation, set())

    def set_next_rotation(self):
        get_next = False
        founded = False
        while not founded:
            for rotation in Rotation:
                if get_next:
                    self.rotation = rotation
                    print("Next rotation: {}".format(rotation.name))
                    founded = True
                    break
                if rotation == self.rotation:
                    get_next = True


class ZFigure(Figure):
    """
    Represents "Z" figure
    """
    def __init__(self):
        print("Creating Z-figure...")
        super().__init__()
        self.matrix = {Rotation.NORTH: {(0, 0), (1, 0), (1, 1), (2, 1)},
                       Rotation.EAST: {(1, 0), (0, 1), (1, 1), (0, 2)}}
        self.matrix[Rotation.SOUTH] = self.matrix[Rotation.NORTH]
        self.matrix[Rotation.WEST] = self.matrix[Rotation.EAST]


class TFigure(Figure):
    """
    Represents "T" figure
    """
    def __init__(self):
        print("Creating T-figure...")
        super().__init__()
        self.matrix = {Rotation.NORTH: {(0, 0), (1, 0), (2, 0), (1, 1)},
                       Rotation.EAST: {(0, 1), (1, 0), (1, 1), (1, 2)},
                       Rotation.SOUTH: {(1, 0), (0, 1), (1, 1), (2, 1)},
                       Rotation.WEST: {(0, 0), (0, 1), (0, 2), (1, 1)}}