class Action:
    pass


class KeyDown(Action):

    def __init__(self, key_code: int):
        self.key = key_code


class KeyUp(Action):

    def __init__(self, key_code: int):
        self.key = key_code