import field


class Game:
    """
    Game logic
    """
    def __init__(self, game_field: field.Field):
        self._field = game_field