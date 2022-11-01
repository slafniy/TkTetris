import os
import threading
import tkinter as tk
import typing as t

import simpleaudio as sa
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

        self._prepare_ui()  # initialize menus and binds

        # Skin stuff
        self._sounds: t.Optional[SoundResources] = None
        self._base_canvas: t.Optional[tk.Canvas] = None
        self._cell_falling_image: t.Optional[tk.PhotoImage] = None
        self._cell_filled_image: t.Optional[tk.PhotoImage] = None
        self._base_image: t.Optional[tk.PhotoImage] = None
        self._cell_size: t.Optional[int] = None
        self._cell_anchor_offset_x: t.Optional[int] = None
        self._cell_anchor_offset_y: t.Optional[int] = None
        self._game_field_offset_x: t.Optional[int] = None
        self._next_figure_field_offset_x: t.Optional[int] = None
        self._next_figure_field_offset_y: t.Optional[int] = None
        self._game_field_offset_y: t.Optional[int] = None
        self._current_music: t.List[sa.PlayObject] = []
        self._current_skin_rb: tk.StringVar  # this is for radiobutton
        self._loaded_skin: t.Optional[str] = None  # this is to control loading skin if it's already loaded
        self._next_figure_image_ids = []

        self._load_skin()  # paint all stuff now

    @property
    def sounds(self) -> SoundResources:
        return self._sounds

    def new_game(self):
        pass

    def _load_skin(self, skin_name='Default'):
        """
        Loads gfx and sounds from resources
        """
        if skin_name == self._loaded_skin:
            return

        self._sounds = SoundResources(skin_name)  # Audio

        resources_path = os.path.join(os.path.realpath(__file__), f'../../res/{skin_name}/gfx')

        with open(os.path.join(resources_path, "cfg.yaml")) as yaml_file:
            cfg = yaml.safe_load(yaml_file)

        self._cell_size = cfg['cell_size']
        self._game_field_offset_x = cfg['game_field_nw']['x']
        self._game_field_offset_y = cfg['game_field_nw']['y']

        self._next_figure_field_offset_x = cfg['next_figure_field_nw']['x']
        self._next_figure_field_offset_y = cfg['next_figure_field_nw']['y']

        self._cell_anchor_offset_x = cfg['cell_anchor_nw']['x']
        self._cell_anchor_offset_y = cfg['cell_anchor_nw']['y']

        self._cell_falling_image = tk.PhotoImage(file=os.path.join(resources_path, "cell_falling.png"))
        self._cell_filled_image = tk.PhotoImage(file=os.path.join(resources_path, "cell_filled.png"))

        self._base_image = tk.PhotoImage(file=os.path.join(resources_path, "base.png"))
        self._base_canvas = tk.Canvas(master=self,
                                      width=self._base_image.width(),
                                      height=self._base_image.height())
        self._base_canvas.create_image(0, 0, image=self._base_image, anchor=tk.NW)
        self._base_canvas.grid(column=0, row=0, sticky=tk.NW)
        self.geometry(f'{self._base_image.width()}x{self._base_image.height()}')

        # Stop any music if any and run new
        [i.stop() for i in self._current_music]
        self._current_music.append(self.sounds.startup.play())
        self._loaded_skin = skin_name

    def show_next_figure(self, points: t.List[figures.Point]):
        [self.delete_image(i) for i in self._next_figure_image_ids]
        self._next_figure_image_ids = []
        for x, y in points:
            _x = x * self._cell_size + self._next_figure_field_offset_x - self._cell_anchor_offset_x
            _y = y * self._cell_size + self._next_figure_field_offset_y - self._cell_anchor_offset_y
            self._next_figure_image_ids.append(
                self._base_canvas.create_image(_x, _y, anchor=tk.NW, image=self._cell_falling_image))

    def refresh_ui(self):
        self._base_canvas.update()

    def delete_image(self, img_id):
        self._base_canvas.delete(img_id)

    def _paint_cell(self, x, y, cell_image):
        _x = x * self._cell_size + self._game_field_offset_x - self._cell_anchor_offset_x
        _y = y * self._cell_size + self._game_field_offset_y - self._cell_anchor_offset_y
        return self._base_canvas.create_image(_x, _y, anchor=tk.NW, image=cell_image)

    def paint_filled(self, x, y):
        return self._paint_cell(x, y, self._cell_filled_image)

    def paint_falling(self, x, y):
        return self._paint_cell(x, y, self._cell_falling_image)

    def game_over(self):
        pass

    def toggle_pause(self):
        pass

    def _prepare_ui(self):

        def on_close():
            self.destroy()

        self.protocol("WM_DELETE_WINDOW", on_close)

        # Add Menu
        popup = tk.Menu(self, tearoff=0)
        self._current_skin_rb = tk.StringVar(value='Default')
        popup.add_radiobutton(label="Default", command=lambda: self._load_skin('Default'),
                              variable=self._current_skin_rb, value='Default')
        popup.add_radiobutton(label="Matrix", command=lambda: self._load_skin('Matrix'),
                              variable=self._current_skin_rb, value='Matrix')

        def menu_popup(event):
            # display the popup menu
            try:
                popup.tk_popup(event.x_root, event.y_root, 0)
            finally:
                # Release the grab
                popup.grab_release()

        self.bind("<Button-3>", menu_popup)


def main():
    """
    Connects UI and game logic
    """

    ui_root = TkTetrisUI()

    # Bind keyboard listener
    key_handler = keyboard_handler.KeyboardHandler()
    ui_root.bind(sequence='<KeyPress>', func=key_handler.on_key_press)
    ui_root.bind(sequence='<KeyRelease>', func=key_handler.on_key_release)

    # Game field binds UI and logic together
    game.Game(keyboard_handler=key_handler,
              ui_root=ui_root)

    ui_root.geometry("+800+300")

    # Start application
    ui_root.mainloop()
