import enum
import itertools
import random


class Rotation(enum.Enum):
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
        self.current_points = set()
        self.position = None
        self._rotation_generator = itertools.cycle(Rotation)
        for i in range(random.randint(1, 4)):
            self.rotation = next(self._rotation_generator)

    def current_matrix(self):
        return self.matrix.get(self.rotation, set())

    def set_next_rotation(self):
        self.rotation = next(self._rotation_generator)


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


class SFigure(Figure):
    """
    Represents "Z" figure
    """

    def __init__(self):
        print("Creating Z-figure...")
        super().__init__()
        self.matrix = {Rotation.NORTH: {(0, 1), (1, 0), (2, 0), (1, 1)},
                       Rotation.EAST: {(0, 0), (0, 1), (1, 1), (1, 2)}}
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


class IFigure(Figure):
    """
    Represents "I" figure
    """

    def __init__(self):
        print("Creating I-figure...")
        super().__init__()
        self.matrix = {Rotation.NORTH: {(0, 0), (1, 0), (2, 0), (3, 0)},
                       Rotation.EAST: {(0, 0), (0, 1), (0, 2), (0, 3)}}
        self.matrix[Rotation.SOUTH] = self.matrix[Rotation.NORTH]
        self.matrix[Rotation.WEST] = self.matrix[Rotation.EAST]


class OFigure(Figure):
    """
    Represents "O" figure
    """

    def __init__(self):
        print("Creating O-figure...")
        super().__init__()
        self.matrix = {Rotation.NORTH: {(0, 0), (1, 1), (1, 0), (0, 1)}}
        self.matrix[Rotation.SOUTH] = self.matrix[Rotation.WEST] = \
            self.matrix[Rotation.EAST] = self.matrix[Rotation.NORTH]


class LFigure(Figure):
    """
    Represents "L" figure
    """

    def __init__(self):
        print("Creating L-figure...")
        super().__init__()
        self.matrix = {Rotation.NORTH: {(0, 0), (0, 1), (0, 2), (1, 2)},
                       Rotation.EAST: {(0, 0), (1, 0), (2, 0), (0, 1)},
                       Rotation.SOUTH: {(0, 0), (1, 0), (1, 1), (1, 2)},
                       Rotation.WEST: {(2, 0), (0, 1), (1, 1), (2, 1)}}


class RLFigure(Figure):
    """
    Represents "Reversed L" figure
    """

    def __init__(self):
        print("Creating Reversed-L-figure...")
        super().__init__()
        self.matrix = {Rotation.NORTH: {(0, 0), (0, 1), (0, 2), (1, 0)},
                       Rotation.EAST: {(0, 0), (1, 0), (2, 0), (2, 1)},
                       Rotation.SOUTH: {(0, 2), (1, 0), (1, 1), (1, 2)},
                       Rotation.WEST: {(0, 0), (0, 1), (1, 1), (2, 1)}}


all_figures = [ZFigure, TFigure, IFigure, SFigure, OFigure, LFigure, RLFigure]
