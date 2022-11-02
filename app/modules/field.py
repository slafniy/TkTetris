import typing as t

from .logger import logger
from . import cell as c
from . import figures as f


class Field(t.List[t.List[c.Cell]]):
    """
    Game field
    """

    def __init__(self, width: int, height: int):
        super().__init__([[c.Cell() for _ in range(height)] for _ in range(width)])
        self.width = width
        self.height = height

    def get_full_row(self) -> t.Optional[int]:
        for y in range(self.height - 1, -1, -1):
            is_full = True
            for x in range(self.width):
                if self[x][y].state != c.CellState.FILLED:
                    is_full = False
                    break
            if is_full:
                logger.debug('Row %i is full', y)
                return y
        return None

    def can_place(self, x: int, y: int, figure: f.Figure) -> t.Optional[t.Set[f.Point]]:
        target_points = set()
        for _x, _y in figure.current_matrix():
            new_x = _x + x
            new_y = _y + y
            if not (0 <= new_x < self.width and 0 <= new_y < self.height and
                    self[new_x][new_y].state != c.CellState.FILLED):
                logger.debug(f'Cannot place figure to [{x}, {y}]')
                return None
            target_points.add(f.Point(new_x, new_y))

        figure.position = f.Point(x, y)
        figure.current_points = target_points
        return target_points

    def __str__(self):
        field_str = '\n'
        for y in range(self.height):
            for x in range(self.width):
                st = self[x][y].state
                # M for moving, X for fiXed
                field_str += '[ ]' if st == c.CellState.EMPTY else '[M]' if st == c.CellState.FALLING else '[X]'
            field_str += '\n'
        return field_str
