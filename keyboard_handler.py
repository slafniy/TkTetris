# Default key binds
MOVE_LEFT = 37  # Left arrow
MOVE_RIGHT = 39  # Right arrow
ROTATE = 38  # Up arrow
FORCE_DOWN = 40  # Down arrow
PAUSE = 32  # Space


# TODO: make it work smooth
class KeyboardHandler:
    """
    Possibly this will work fine only on Windows
    """

    def __init__(self):
        self.move_left_func = None
        self.move_right_func = None
        self.force_down_func = None
        self.rotate_func = None
        self.pause_func = None

    def on_key_press(self, event):
        self._process_key(event.keycode)

    def on_key_release(self, event):
        pass

    def _process_key(self, code):
        # Make a decision what should we do with this key (Where is my switch keyword??)

        if code == MOVE_LEFT and callable(self.move_left_func):
            # noinspection PyCallingNonCallable
            self.move_left_func()

        elif code == MOVE_RIGHT and callable(self.move_right_func):
            # noinspection PyCallingNonCallable
            self.move_right_func()

        elif code == ROTATE and callable(self.rotate_func):
            # noinspection PyCallingNonCallable
            self.rotate_func()

        elif code == FORCE_DOWN and callable(self.force_down_func):
            # noinspection PyCallingNonCallable
            self.force_down_func()

        elif code == PAUSE and callable(self.pause_func):
            # noinspection PyCallingNonCallable
            self.pause_func()
