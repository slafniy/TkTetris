class Cell:
    EMPTY = 0
    FILLED = 1
    FALLING = 2


class Game:
    """
    Game logic and state
    """
    def __init__(self, field_width, field_height):
        self.field = [[Cell.EMPTY for _ in range(field_height)] for _ in range(field_width)]