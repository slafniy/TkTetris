import typing as t

import cell as c


class Field(t.List[t.List[c.Cell]]):
    """
    Game field
    """

    def __init__(self, height: int, width: int):
        super().__init__([[c.Cell() for _ in range(height)] for _ in range(width)])
        self.width = width
        self.height = height

    def set_cell_state(self, x: int, y: int, state: c.CellState) -> c.Cell:
        if 0 <= x < self.width and 0 <= y < self.height:
            cell = self[x][y]
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
                print("Full row:", y)
                return y
        return None
