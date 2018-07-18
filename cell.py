import enum
import typing as t


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
        self.image_id: t.Optional[int] = None
