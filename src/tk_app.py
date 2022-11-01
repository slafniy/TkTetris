import os
import threading
import tkinter as tk
import typing as t

import yaml

import figures
import keyboard_handler
import game
import abstract_ui
from resources import SoundResources

VERSION = '1.1d'

COLOR_BACKGROUND = "#000000"


class TkTetrisUI(tk.Tk, abstract_ui.AbstractUI):
    """
    Main window class
    """

    def __init__(self):
        super(TkTetrisUI, self).__init__()
        self.title(f'TkTetris {VERSION}')

        self._sounds: t.Optional[SoundResources] = None

        self._base_canvas: t.Optional[tk.Canvas] = None
        self._next_figure_field: t.Optional[tk.Canvas] = None
        self._pause_image_id: t.Optional[int] = None
        self._game_score: t.Optional[tk.Label] = None
        self._cell_image: t.Optional[tk.PhotoImage] = None
        self._base_image: t.Optional[tk.PhotoImage] = None

        self._cell_size: t.Optional[int] = None
        self._cell_anchor_offset_x: t.Optional[int] = None
        self._cell_anchor_offset_y: t.Optional[int] = None

        self._game_field_offset_x: t.Optional[int] = None
        self._game_field_offset_y: t.Optional[int] = None

        self.load_skin()  # Initialize or re-initialize UI from resources

    @property
    def sounds(self) -> SoundResources:
        return self._sounds

    def load_skin(self, skin_name='Default'):
        """
        Loads gfx and sounds from resources
        """
        self._sounds = SoundResources()  # Audio

        resources_path = os.path.join(os.path.realpath(__file__), f'../../res/{skin_name}/gfx')

        with open(os.path.join(resources_path, "cfg.yaml")) as yaml_file:
            cfg = yaml.safe_load(yaml_file)

        self._cell_size = cfg['cell_size']
        self._game_field_offset_x = cfg['game_field_nw']['x']
        self._game_field_offset_y = cfg['game_field_nw']['y']

        self._cell_anchor_offset_x = cfg['cell_anchor_nw']['x']
        self._cell_anchor_offset_y = cfg['cell_anchor_nw']['y']

        self._cell_image = tk.PhotoImage(file=os.path.join(resources_path, "cell.png"))
        self._base_image = tk.PhotoImage(file=os.path.join(resources_path, "base.png"))

        self._base_canvas = tk.Canvas(master=self,
                                      width=self._base_image.width(),
                                      height=self._base_image.height())
        self._base_canvas.create_image(0, 0, image=self._base_image, anchor=tk.NW)
        self._base_canvas.pack()

    def show_next_figure(self, points: t.List[figures.Point]):
        pass

    def refresh_ui(self):
        self._base_canvas.update()

    def delete_image(self, img_id):
        self._base_canvas.delete(img_id)

    def _paint_cell(self, x, y, cell_image=None):
        _x = x * self._cell_size + self._game_field_offset_x - self._cell_anchor_offset_x
        _y = y * self._cell_size + self._game_field_offset_y - self._cell_anchor_offset_y
        return self._base_canvas.create_image(_x, _y, anchor=tk.NW, image=cell_image or self._cell_image)

    def paint_filled(self, x, y):
        return self._paint_cell(x, y)

    def paint_falling(self, x, y):
        return self._paint_cell(x, y)

    def game_over(self):
        pass

    def toggle_pause(self):
        pass


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
    game.Game(game_over_event=game_over_event,
              keyboard_handler=key_handler,
              ui_root=ui_root)

    ui_root.geometry("+960+500")

    # Start application
    ui_root.mainloop()
