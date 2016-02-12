import enum

import actions
import game
import os
import tkinter as tk

# Default field parameters
CELL_SIZE = 24  # In pixels, this is base size for all
CELL_INTERNAL_BORDER = 4
FIELD_HEIGHT = 20  # In cells
FIELD_WIDTH = 10  # In cells
COLOR_BACKGROUND = "#FF00FF"
COLOR_FILLED = "#000000"


class TkTetris(tk.Tk, game.Game):
    """
    Tk UI class for tetris
    """

    def __init__(self):
        super().__init__(className="tkTetris")
        game.Game.__init__(self, width=FIELD_WIDTH, height=FIELD_HEIGHT)

        # Load resources
        self._resources_path = os.path.join('Resources/Default')
        self._filled_cell_image = tk.PhotoImage(file=os.path.join(self._resources_path, "cell_filled.png"))
        self._falling_cell_image = tk.PhotoImage(file=os.path.join(self._resources_path, "cell_falling.png"))
        self._background_image = tk.PhotoImage(file=os.path.join(self._resources_path, "background.png"))
        self._game_over_image = tk.PhotoImage(file=os.path.join(self._resources_path, "game_over.png"))

        # Draw background, draw labels etc.
        self._ui_field = tk.Canvas(master=self, background=COLOR_BACKGROUND,
                                   height=FIELD_HEIGHT * CELL_SIZE,
                                   width=FIELD_WIDTH * CELL_SIZE)
        self._ui_field.grid()

        # TODO: get rid of this magic number!
        self._ui_field.create_image(2, 2, anchor=tk.NW, image=self._background_image)
        self._game_score = tk.Label(master=self, text="Score: \n00000000")
        self._game_score.grid(column=1, row=0, sticky=tk.N)

        # Bind keys
        self.bind(sequence='<KeyPress>', func=self.on_key_press)
        self.bind(sequence='<KeyRelease>', func=self.on_key_release)

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def paint_filled(self, x, y):
        _x = x * CELL_SIZE + 2  # TODO: get rid of this magic
        _y = y * CELL_SIZE + 2  # TODO: get rid of this magic
        return self._ui_field.create_image(_x, _y, anchor=tk.NW, image=self._filled_cell_image)

    def paint_falling(self, x, y):
        _x = x * CELL_SIZE + 2  # TODO: get rid of this magic
        _y = y * CELL_SIZE + 2  # TODO: get rid of this magic
        return self._ui_field.create_image(_x, _y, anchor=tk.NW, image=self._falling_cell_image)

    def delete_image(self, image_id) -> None:
        self._ui_field.delete(image_id)

    def refresh_ui(self) -> None:
        self._ui_field.update()

    def update_score(self, score: int):
        self._game_score['text'] = "Score: \n{}".format(score)

    def _on_close(self):
        # TODO: find a way to stop background threads immediately
        self.stop_threads()
        self.destroy()
        print("!! Bye !!")

    def on_key_press(self, event):
        self.add_action(actions.KeyDown(event.keycode))

    def on_key_release(self, event):
        self.add_action(actions.KeyUp(event.keycode))