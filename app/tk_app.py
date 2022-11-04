import argparse
import tkinter as tk
import typing as t

import simpleaudio as sa
import yaml

import modules.abstract_ui as abstract_ui
import modules.game as game
import modules.controls_handler as ch

from modules.cell import CellState
from modules.figures import Point
from modules.logger import logger
from modules.resources import SoundResources, get_resources_path

VERSION = '1.1d'

COLOR_BACKGROUND = "#000000"


class TkTetrisUI(tk.Tk, abstract_ui.AbstractUI):
    """
    Main window class
    """

    def __init__(self, controls_handler: ch.ControlsHandler):
        super().__init__()
        self.title(f'TkTetris {VERSION}')
        self._controls_handler = controls_handler

        # to store ids of painted cell images
        self._game_field_cells_ids: t.Dict[Point, int] = {}

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
        self._pause_image: t.Optional[tk.PhotoImage] = None
        self._pause_image_offset_x: t.Optional[int] = None
        self._pause_image_offset_y: t.Optional[int] = None
        self._pause_image_id: t.Optional[int] = None  # to toggle pause
        self._current_music: t.List[sa.PlayObject] = []
        self._current_skin_rb: tk.StringVar  # this is for radiobutton
        self._loaded_skin: t.Optional[str] = None  # this is to control loading skin if it's already loaded

        self._next_figure_points: t.Set[Point] = set()  # store to repaint if skin changed
        self._next_figure_image_ids: t.Set[int] = set()

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

        gfx_resources_path = get_resources_path() / f'{skin_name}' / 'gfx'

        with (gfx_resources_path / "cfg.yaml").open() as yaml_file:
            cfg = yaml.safe_load(yaml_file)

        self._cell_size = cfg['cell_size']
        self._game_field_offset_x = cfg['game_field_nw']['x']
        self._game_field_offset_y = cfg['game_field_nw']['y']

        self._next_figure_field_offset_x = cfg['next_figure_field_nw']['x']
        self._next_figure_field_offset_y = cfg['next_figure_field_nw']['y']

        self._cell_anchor_offset_x = cfg['cell_anchor_nw']['x']
        self._cell_anchor_offset_y = cfg['cell_anchor_nw']['y']

        self._cell_falling_image = tk.PhotoImage(file=str(gfx_resources_path / "cell_falling.png"))
        self._cell_filled_image = tk.PhotoImage(file=str(gfx_resources_path / "cell_filled.png"))

        self._pause_image = tk.PhotoImage(file=str(gfx_resources_path / "pause.png"))
        self._pause_image_offset_x = cfg['pause_nw']['x']
        self._pause_image_offset_y = cfg['pause_nw']['y']

        self._base_image = tk.PhotoImage(file=str(gfx_resources_path / "base.png"))
        self._base_canvas = tk.Canvas(master=self,
                                      width=self._base_image.width(),
                                      height=self._base_image.height())
        self._base_canvas.create_image(0, 0, image=self._base_image, anchor=tk.NW)
        self._base_canvas.grid(column=0, row=0, sticky=tk.NW)
        self.geometry(f'{self._base_image.width()}x{self._base_image.height()}')

        if callable(self._controls_handler.skin_change_func):
            self._controls_handler.skin_change_func()

        # Stop any music if any and run new
        [i.stop() for i in self._current_music]
        # self._current_music.append(self.sounds.startup.play())
        self._loaded_skin = skin_name

        # Repaint stuff if any
        self.show_next_figure(self._next_figure_points)

    def show_next_figure(self, points: t.Set[Point]):
        self._next_figure_points = points
        [self.delete_image(i) for i in self._next_figure_image_ids]
        self._next_figure_image_ids = set()
        for x, y in points:
            _x = x * self._cell_size + self._next_figure_field_offset_x - self._cell_anchor_offset_x
            _y = y * self._cell_size + self._next_figure_field_offset_y - self._cell_anchor_offset_y
            self._next_figure_image_ids.add(
                self._base_canvas.create_image(_x, _y, anchor=tk.NW, image=self._cell_falling_image))

    def refresh_ui(self):
        self._base_canvas.update()

    def delete_image(self, img_id):
        self._base_canvas.delete(img_id)

    def _paint_cell(self, point: Point, cell_image: tk.PhotoImage) -> int:
        x = point.x * self._cell_size + self._game_field_offset_x - self._cell_anchor_offset_x
        y = point.y * self._cell_size + self._game_field_offset_y - self._cell_anchor_offset_y
        return self._base_canvas.create_image(x, y, anchor=tk.NW, image=cell_image)

    def apply_field_change(self, changed_points: t.OrderedDict[CellState, t.Set[Point]]):
        for cell_state, points in changed_points.items():
            if cell_state == CellState.EMPTY:
                self._remove_cells(points)
            else:
                self._paint_cells(points, cell_state)

    def _remove_cells(self, points: t.Set[Point]):
        for point in points:
            image_id = self._game_field_cells_ids.pop(point, None)
            if image_id is not None:
                self.delete_image(image_id)

    def _paint_cells(self, points: t.Set[Point], state: CellState):
        cell_image = self._cell_falling_image if state == CellState.FALLING else self._cell_filled_image
        for point in points:
            self._game_field_cells_ids[point] = self._paint_cell(point, cell_image)

    def game_over(self):
        pass

    def toggle_pause(self):
        if self._pause_image_id is not None:
            self.delete_image(self._pause_image_id)
            self._pause_image_id = None
        else:
            self._pause_image_id = self._base_canvas.create_image(self._pause_image_offset_x,
                                                                  self._pause_image_offset_y,
                                                                  anchor=tk.NW, image=self._pause_image)

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
    controls_handler = ch.ControlsHandler()

    ui_root = TkTetrisUI(controls_handler)

    # Bind keyboard listener
    ui_root.bind(sequence='<KeyPress>', func=controls_handler.on_key_press)
    ui_root.bind(sequence='<KeyRelease>', func=controls_handler.on_key_release)

    # Game field binds UI and logic together
    game.Game(controls_handler=controls_handler,
              ui_root=ui_root)

    ui_root.geometry("+800+300")

    # Start application
    ui_root.mainloop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--log-level', default='WARNING', dest='log_level',
                        help='Logging level. Example --loglevel=DEBUG, default level - WARNING')
    args = parser.parse_args()

    logger.setLevel(args.log_level.upper())

    main()
