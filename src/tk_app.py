import os
import threading
import tkinter as tk
import typing as t

import simpleaudio as sa

import figures
import keyboard_handler
import game
import abstract_ui
from resources import SoundResources

VERSION = '1.0d'

# Default field parameters
CELL_SIZE = 24  # In pixels, this is base size for all
CELL_INTERNAL_BORDER = 4
FIELD_HEIGHT = 20  # In cells
FIELD_HIDDEN_TOP_ROWS_NUMBER = 4
FIELD_WIDTH = 10  # In cells
COLOR_BACKGROUND = "#000000"


class TkTetrisUI(tk.Tk, abstract_ui.AbstractUI):
    """
    Main window class
    """

    def __init__(self):
        super(TkTetrisUI, self).__init__()
        self.title(f'TkTetris {VERSION}')

        # Load resources - graphics
        self._resources_path = os.path.join(os.path.realpath(__file__), '../../res/ClassicMonochrome')
        self._filled_cell_image = tk.PhotoImage(file=os.path.join(self._resources_path, "cell_filled.png"))
        self._falling_cell_image = tk.PhotoImage(file=os.path.join(self._resources_path, "cell_falling.png"))
        self._background_image = tk.PhotoImage(file=os.path.join(self._resources_path, "background.png"))
        self._game_over_image = tk.PhotoImage(file=os.path.join(self._resources_path, "game_over.png"))
        self._pause_image = tk.PhotoImage(file=os.path.join(self._resources_path, "pause.png"))

        # Audio
        def _get(x):
            return sa.WaveObject.from_wave_file(os.path.join(self._resources_path, f'{x}.wav'))

        self._sounds = SoundResources(
            move=_get('move'),
            rotate=_get('rotate'),
            fix_figure=_get('fix'),
            row_delete=_get('row'),
            tick=_get('tick'),
            game_over=_get('game_over'),
            startup=_get('startup')
        )

        self._game_field: t.Optional[tk.Canvas] = None
        self._next_figure_field: t.Optional[tk.Canvas] = None
        self._pause_image_id: t.Optional[int] = None
        self._game_score: t.Optional[tk.Label] = None

        self.create_ui()  # Initialize or re-initialize UI from resources

    @property
    def sounds(self) -> SoundResources:
        return self._sounds

    def create_ui(self):
        """
        Draw from resources
        """
        self._game_field = tk.Canvas(master=self, background=COLOR_BACKGROUND,
                                     height=FIELD_HEIGHT * CELL_SIZE,
                                     width=FIELD_WIDTH * CELL_SIZE)
        # TODO: get rid of this magic number!
        self._game_field.create_image(2, 2, anchor=tk.NW, image=self._background_image)
        self._next_figure_field = tk.Canvas(master=self, background=COLOR_BACKGROUND,
                                            height=4 * CELL_SIZE,
                                            width=4 * CELL_SIZE)
        self._next_figure_field.create_image(0, 0, anchor=tk.NW, image=self._background_image)
        self._game_score = tk.Label(master=self, text="Score: 0")

        # Place elements on grid
        self._game_field.grid(column=0, row=0, columnspan=2, rowspan=9)
        self._next_figure_field.grid(column=2, row=0, sticky=tk.NW)
        self._game_score.grid(column=2, row=1, sticky=tk.NW)

    def show_next_figure(self, points: t.List[figures.Point]):
        self._next_figure_field.create_image(0, 0, anchor=tk.NW, image=self._background_image)  # clear all previous
        for x, y in points:
            _x = x * CELL_SIZE + 2
            _y = y * CELL_SIZE + 2
            self._next_figure_field.create_image(_x, _y, anchor=tk.NW, image=self._falling_cell_image)

    def refresh_ui(self):
        self._game_field.update()

    def delete_image(self, img_id):
        self._game_field.delete(img_id)

    def paint_filled(self, x, y):
        _x = x * CELL_SIZE + 2  # TODO: get rid of this magic
        _y = (y - FIELD_HIDDEN_TOP_ROWS_NUMBER) * CELL_SIZE + 2  # TODO: get rid of this magic
        return self._game_field.create_image(_x, _y, anchor=tk.NW, image=self._filled_cell_image)

    def paint_falling(self, x, y):
        _x = x * CELL_SIZE + 2  # TODO: get rid of this magic
        _y = (y - FIELD_HIDDEN_TOP_ROWS_NUMBER) * CELL_SIZE + 2  # TODO: get rid of this magic
        return self._game_field.create_image(_x, _y, anchor=tk.NW, image=self._falling_cell_image)

    def game_over(self):
        self._game_field.create_image(FIELD_WIDTH / 2 * CELL_SIZE,
                                      FIELD_HEIGHT / 2 * CELL_SIZE,
                                      anchor=tk.CENTER, image=self._game_over_image)

    def toggle_pause(self):
        if self._pause_image_id is not None:
            self._game_field.delete(self._pause_image_id)
            self._pause_image_id = None
        else:
            self._pause_image_id = self._game_field.create_image(FIELD_WIDTH / 2 * CELL_SIZE,
                                                                 FIELD_HEIGHT / 2 * CELL_SIZE,
                                                                 anchor=tk.CENTER, image=self._pause_image)


def main():
    """
    Connects UI and game logic
    """

    ui_root = TkTetrisUI()

    game_over_event = threading.Event()

    # Bind keyboard listener
    key_handler = keyboard_handler.KeyboardHandler(game_over_event)
    ui_root.bind(sequence='<KeyPress>', func=key_handler.on_key_press)
    ui_root.bind(sequence='<KeyRelease>', func=key_handler.on_key_release)

    def on_close():
        ui_root.destroy()

    ui_root.protocol("WM_DELETE_WINDOW", on_close)

    # Game field binds UI and logic together
    game.Game(width=FIELD_WIDTH, height=FIELD_HEIGHT + FIELD_HIDDEN_TOP_ROWS_NUMBER,
              game_over_event=game_over_event,
              keyboard_handler=key_handler,
              ui_root=ui_root)

    ui_root.geometry("+960+500")

    # Start application
    ui_root.mainloop()
