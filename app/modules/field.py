import typing as t

from . logger import logger
from . import figures as f
from . import cell as c


class Field(t.List[t.List[c.Cell]]):
    """
    Game field
    """

    def __init__(self, width: int, height: int):
        super().__init__([[c.Cell() for _ in range(height)] for _ in range(width)])
        self.width = width
        self.height = height

    def set_cell_state(self, point: f.Point, state: c.CellState) -> c.Cell:
        assert isinstance(point, f.Point)
        if 0 <= point.x < self.width and 0 <= point.y < self.height:
            cell = self[point.x][point.y]
            cell.state = state
            return cell

    def get_full_row(self) -> t.Optional[int]:
        for y in range(self.height - 1, -1, -1):
            is_full = True
            for x in range(self.width):
                if self[x][y].state != c.CellState.FILLED:
                    is_full = False
                    break
            if is_full:
                logger.debug(f'Row {y} is full')
                return y
        return None
