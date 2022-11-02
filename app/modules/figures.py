import enum
import itertools
import random
import typing as t


class Point(t.NamedTuple):
    x: int
    y: int


class Rotation(enum.IntEnum):
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3


class Figure(t.Dict[Rotation, t.Set[t.Tuple[int, int]]]):
    """
    Saves a set of figure points and rules of rotation
    """

    def __init__(self):
        super().__init__()
        self.position: t.Optional[Point] = None  # Stores position on field
        self._rotation_generator = itertools.cycle(Rotation)
        for _ in range(random.randint(1, 4)):
            self.rotation = next(self._rotation_generator)

    def current_matrix(self) -> t.Set[Point]:
        """Return current rotation matrix"""
        return {Point(x, y) for x, y in self.get(self.rotation, set())}

    def set_next_rotation(self):
        """
        Rotate clockwise
        """
        self.rotation = next(self._rotation_generator)

    def get_points(self, position: t.Optional[Point] = None) -> t.Set[Point]:
        """
        Calculate coordinates of each point of the figure for given position
        :param position: - if None current position will be used for calculations
        If there's no position returns empty set
        """
        position = position or self.position
        if position is not None:
            return {Point(point.x + position.x, point.y + position.y) for point in self.current_matrix()}
        return set()


class ZFigure(Figure):
    """
    Represents "Z" figure
    """

    def __init__(self):
        print("Creating Z-figure...")
        super().__init__()
        self[Rotation.NORTH] = self[Rotation.SOUTH] = {(0, 2), (0, 3), (1, 1), (1, 2)}
        self[Rotation.EAST] = self[Rotation.WEST] = {(0, 2), (1, 2), (1, 3), (2, 3)}


class SFigure(Figure):
    """
    Represents "Z" figure
    """

    def __init__(self):
        print("Creating Z-figure...")
        super().__init__()
        self[Rotation.NORTH] = self[Rotation.SOUTH] = {(0, 1), (0, 2), (1, 2), (1, 3)}
        self[Rotation.EAST] = self[Rotation.WEST] = {(0, 3), (1, 2), (1, 3), (2, 2)}


class TFigure(Figure):
    """
    Represents "T" figure
    """

    def __init__(self):
        print("Creating T-figure...")
        super().__init__()
        self[Rotation.NORTH] = {(0, 3), (1, 2), (1, 3), (2, 3)}
        self[Rotation.EAST] = {(0, 1), (0, 2), (0, 3), (1, 2)}
        self[Rotation.SOUTH] = {(0, 2), (1, 2), (2, 2), (1, 3)}
        self[Rotation.WEST] = {(0, 2), (1, 1), (1, 2), (1, 3)}


class IFigure(Figure):
    """
    Represents "I" figure
    """

    def __init__(self):
        print("Creating I-figure...")
        super().__init__()
        self[Rotation.NORTH] = self[Rotation.SOUTH] = {(1, 0), (1, 1), (1, 2), (1, 3)}
        self[Rotation.EAST] = self[Rotation.WEST] = {(0, 3), (1, 3), (2, 3), (3, 3)}


class OFigure(Figure):
    """
    Represents "O" figure
    """

    def __init__(self):
        print("Creating O-figure...")
        super().__init__()
        self[Rotation.NORTH] = self[Rotation.SOUTH] = self[Rotation.WEST] = self[Rotation.EAST] \
            = {(0, 2), (0, 3), (1, 2), (1, 3)}


class LFigure(Figure):
    """
    Represents "L" figure
    """

    def __init__(self):
        print("Creating L-figure...")
        super().__init__()
        self[Rotation.NORTH] = {(0, 1), (0, 2), (0, 3), (1, 3)}
        self[Rotation.EAST] = {(0, 2), (0, 3), (1, 2), (2, 2)}
        self[Rotation.SOUTH] = {(0, 1), (1, 1), (1, 2), (1, 3)}
        self[Rotation.WEST] = {(0, 3), (1, 3), (2, 2), (2, 3)}


class RLFigure(Figure):
    """
    Represents "Reversed L" figure
    """

    def __init__(self):
        print("Creating Reversed-L-figure...")
        super().__init__()
        self[Rotation.NORTH] = {(0, 3), (1, 1), (1, 2), (1, 3)}
        self[Rotation.EAST] = {(0, 2), (0, 3), (1, 3), (2, 3)}
        self[Rotation.SOUTH] = {(0, 1), (0, 2), (0, 3), (1, 1)}
        self[Rotation.WEST] = {(0, 2), (1, 2), (2, 2), (2, 3)}


all_figures = [ZFigure, TFigure, IFigure, SFigure, OFigure, LFigure, RLFigure]
