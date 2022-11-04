"""Cell - describes the smallest part of game field"""
import enum


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
