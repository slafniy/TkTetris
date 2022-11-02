"""Cell - describes the smallest part of game field"""
import dataclasses
import enum
import typing as t


class CellState(enum.IntEnum):
    """
    Possible cell states:
        FALLING - part of moving figure controlled by user
        FILLED - block that fixed on game field
        EMPTY - the cell is free
    """
    EMPTY = 0
    FILLED = 1
    FALLING = 2


@dataclasses.dataclass
class Cell:
    """Describes cell - internal state and related image id"""
    state = CellState.EMPTY
    image_id: t.Optional[int] = None
