import os
import threading
import tkinter as tk
import typing as t

import figures
import keyboard_handler
import game

VERSION = '1.0d'

# Default field parameters
CELL_SIZE = 24  # In pixels, this is base size for all
CELL_INTERNAL_BORDER = 4
FIELD_HEIGHT = 20  # In cells
FIELD_HIDDEN_TOP_ROWS_NUMBER = 4
FIELD_WIDTH = 10  # In cells
COLOR_BACKGROUND = "#FF00FF"


class TkTetrisUI(tk.Tk):
    """
    Main window class
    """

    def __init__(self):
        super(TkTetrisUI, self).__init__()
        self.title(f'TkTetris {VERSION}')

        # Load resources
        self._resources_path = os.path.join(os.path.realpath(__file__), '../../res/ClassicMonochrome')
        self._filled_cell_image = tk.PhotoImage(file=os.path.join(self._resources_path, "cell_filled.png"))
        self._falling_cell_image = tk.PhotoImage(file=os.path.join(self._resources_path, "cell_falling.png"))
        self._background_image = tk.PhotoImage(file=os.path.join(self._resources_path, "background.png"))
        self._game_over_image = tk.PhotoImage(file=os.path.join(self._resources_path, "game_over.png"))
        self._pause_image = tk.PhotoImage(file=os.path.join(self._resources_path, "pause.png"))

        self.ui_field: t.Optional[tk.Canvas] = None
        self._next_figure_field: t.Optional[tk.Canvas] = None
        self._pause_image_id: t.Optional[int] = None
        self._game_score: t.Optional[tk.Label] = None

        self.create_ui()  # Initialize or re-initialize UI from resources

    def create_ui(self):
        # Draw background, draw labels etc.
        self.ui_field = tk.Canvas(master=self, background=COLOR_BACKGROUND,
                                  height=FIELD_HEIGHT * CELL_SIZE,
                                  width=FIELD_WIDTH * CELL_SIZE)

        self.ui_field.grid()
        # TODO: get rid of this magic number!
        self.ui_field.create_image(2, 2, anchor=tk.NW, image=self._background_image)

        # Create area to show the next figure
        self._next_figure_field = tk.Canvas(master=self, background=COLOR_BACKGROUND,
                                            height=4 * CELL_SIZE,
                                            width=4 * CELL_SIZE)
        self._next_figure_field.create_image(0, 0, anchor=tk.NW, image=self._background_image)
        self._next_figure_field.grid(column=1, row=0, sticky=tk.N)
        # Add game score
        self._game_score = tk.Label(master=self, text="Score: 0")
        self._game_score.grid(column=1, row=1, sticky=tk.N)

    def paint_filled(self, x, y):
        _x = x * CELL_SIZE + 2  # TODO: get rid of this magic
        _y = (y - FIELD_HIDDEN_TOP_ROWS_NUMBER) * CELL_SIZE + 2  # TODO: get rid of this magic
        return self.ui_field.create_image(_x, _y, anchor=tk.NW, image=self._filled_cell_image)

    def paint_falling(self, x, y):
        _x = x * CELL_SIZE + 2  # TODO: get rid of this magic
        _y = (y - FIELD_HIDDEN_TOP_ROWS_NUMBER) * CELL_SIZE + 2  # TODO: get rid of this magic
        return self.ui_field.create_image(_x, _y, anchor=tk.NW, image=self._falling_cell_image)

    def paint_next(self, points: t.List[figures.Point]):
        self._next_figure_field.create_image(0, 0, anchor=tk.NW, image=self._background_image)  # clear all previous
        for x, y in points:
            _x = x * CELL_SIZE + 2
            _y = y * CELL_SIZE + 2
            self._next_figure_field.create_image(_x, _y, anchor=tk.NW, image=self._falling_cell_image)

    def game_over(self):
        self.ui_field.create_image(FIELD_WIDTH / 2 * CELL_SIZE,
                                   FIELD_HEIGHT / 2 * CELL_SIZE,
                                   anchor=tk.CENTER, image=self._game_over_image)

    def toggle_pause(self):
        if self.ui_field.pause_image_id is not None:
            self.ui_field.delete(self.ui_field.pause_image_id)
            self.ui_field.pause_image_id = None
        else:
            self.ui_field.pause_image_id = self.ui_field.create_image(FIELD_WIDTH / 2 * CELL_SIZE,
                                                                      FIELD_HEIGHT / 2 * CELL_SIZE,
                                                                      anchor=tk.CENTER, image=self._pause_image)


def main():
    # Create root UI thread and main window
    root = TkTetrisUI()

    game_over_event = threading.Event()

    # Bind keyboard listener
    key_handler = keyboard_handler.KeyboardHandler(game_over_event)
    root.bind(sequence='<KeyPress>', func=key_handler.on_key_press)
    root.bind(sequence='<KeyRelease>', func=key_handler.on_key_release)

    def on_close():
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)

    # Game field binds UI and logic together
    game.Game(width=FIELD_WIDTH, height=FIELD_HEIGHT + FIELD_HIDDEN_TOP_ROWS_NUMBER,
              paint_filled=root.paint_filled,
              paint_falling=root.paint_falling,
              paint_next=root.paint_next,
              delete_image=root.ui_field.delete,
              toggle_pause=root.toggle_pause,
              refresh_ui=root.ui_field.update,
              game_over_event=game_over_event,
              game_over_ui=root.game_over,
              keyboard_handler=key_handler)

    root.geometry("+960+500")

    # Start application
    root.mainloop()
