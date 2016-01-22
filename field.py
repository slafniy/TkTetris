import enum


class CellState(enum.Enum):
    EMPTY = 0
    FILLED = 1
    FALLING = 2


class Cell:
    """
    Describes cell - internal state and optional related image id
    """
    def __init__(self):
        self.state = CellState.EMPTY
        self.image_id = None

    # def set_filled(self, image_id):
    #     self.image_id = image_id
    #     self.state = CellState.FILLED
    #
    # def set_falling(self, image_id):
    #     self.image_id = image_id
    #     self.state = CellState.FALLING
    #
    # def set_empty(self):
    #     self.image_id = None
    #     self.state = CellState.EMPTY


class Field:
    """
    Contains information about game field
    """
    def __init__(self, width, height):
        self.width = width
        self.height = height
        # An internal structure to store field state (two-dimensional list)
        self._field = [[Cell() for _ in range(self.height)] for _ in range(self.width)]

    def get_cell(self, x, y):
        """
        :param x: horizontal coordinate
        :param y: vertical coordinate
        :return: Cell instance or None
        """
        assert isinstance(x, int)
        assert isinstance(y, int)
        if 0 <= x < self.width and 0 <= y < self.height:
            return self._field[x][y]
        else:
            return None