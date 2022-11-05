"""Entry point and GUI"""
import argparse
import traceback
import tkinter as tk
import typing as t

from simpleaudio import PlayObject

from modules.abstract_ui import AbstractGUI
from modules.controls_handler import ControlsHandler
from modules.game import Game
from modules.field import CellState
from modules.figures import Point
from modules.logger import logger
from modules.skin import Skin, Sounds, get_skin

VERSION = '1.2d'


class TkTetrisGUI(tk.Tk, AbstractGUI):  # pylint: disable=too-many-instance-attributes  # Not sure what to do here
    """
    Main window class
    """

    def __init__(self):
        super().__init__()
        self.title(f'TkTetris {VERSION}')

        # to store ids and states of painted cell images
        self._game_field_cells: t.Dict[Point, t.Tuple[int, CellState]] = {}

        self._prepare_ui()  # initialize menus and binds

        self._pause_image_id: t.Optional[int] = None  # to toggle pause
        self._base_canvas: t.Optional[tk.Canvas] = None
        self._current_music: t.List[PlayObject] = []
        self._current_skin_rb: tk.StringVar  # this is for radiobutton
        self._loaded_skin: t.Optional[str] = None  # this is to control loading skin if it's already loaded
        self.skin: Skin

        self._next_figure_points: t.Set[Point] = set()  # store to repaint if skin changed
        self._next_figure_image_ids: t.Set[int] = set()

        self._score_image_ids = set()

        self._load_skin()  # paint all stuff now

    @property
    def sounds(self) -> Sounds:
        return self.skin.sounds

    def new_game(self):
        logger.info('Starting new game')

    def _load_skin(self, skin_name='Default'):
        """
        Loads gfx and sounds from resources and applies them
        """
        if skin_name == self._loaded_skin:
            return

        try:
            self.skin = get_skin(skin_name)
        except (KeyError, tk.TclError):
            logger.error(f'Cannot load skin "{skin_name}!')
            logger.debug(traceback.format_exc())
            return  # Leave current skin unchanged

        self._base_canvas = tk.Canvas(master=self,
                                      width=self.skin.base_image.width(),
                                      height=self.skin.base_image.height())
        self._base_canvas.create_image(0, 0, image=self.skin.base_image, anchor=tk.NW)
        self._base_canvas.grid(column=0, row=0, sticky=tk.NW)
        self.geometry(f'{self.skin.base_image.width()}x{self.skin.base_image.height()}')

        # Scores
        self.show_score(0)

        # Stop any music
        for i in self._current_music:
            i.stop()
        self._loaded_skin = skin_name

        # Repaint stuff if any
        self.show_next_figure(self._next_figure_points)
        for point, cell in self._game_field_cells.items():
            if cell[1] == CellState.FILLED:
                self._paint_cell(point, self.skin.cell_filled_image)

    def show_next_figure(self, points: t.Set[Point]):
        self._next_figure_points = points
        for i in self._next_figure_image_ids:
            self._base_canvas.delete(i)
        self._next_figure_image_ids = set()
        for x, y in points:
            _x = x * self.skin.cell_size + self.skin.next_figure_field_offset_x - self.skin.cell_anchor_offset_x
            _y = y * self.skin.cell_size + self.skin.next_figure_field_offset_y - self.skin.cell_anchor_offset_y
            self._next_figure_image_ids.add(
                self._base_canvas.create_image(_x, _y, anchor=tk.NW, image=self.skin.cell_falling_image))

    def show_score(self, score: int):
        for i in self._score_image_ids:
            self._base_canvas.delete(i)
        score_str = f'{score:04d}'
        for i, digit in enumerate(score_str):
            x = self.skin.score_digit_offset_x + i * self.skin.digit_width
            self._score_image_ids.add(self._base_canvas.create_image(x, self.skin.score_digit_offset_y,
                                                                     anchor=tk.NW, image=self.skin.digit_images[digit]))

    def _paint_cell(self, point: Point, cell_image: tk.PhotoImage) -> int:
        x = point.x * self.skin.cell_size + self.skin.game_field_offset_x - self.skin.cell_anchor_offset_x
        y = point.y * self.skin.cell_size + self.skin.game_field_offset_y - self.skin.cell_anchor_offset_y
        return self._base_canvas.create_image(x, y, anchor=tk.NW, image=cell_image)

    def apply_field_change(self, changed_points: t.OrderedDict[CellState, t.Set[Point]]):
        for cell_state, points in changed_points.items():
            if cell_state == CellState.EMPTY:
                self._remove_cells(points)
            else:
                self._paint_cells(points, cell_state)

    def _remove_cells(self, points: t.Set[Point]):
        for point in points:
            image_id, _ = self._game_field_cells.pop(point, None)
            if image_id is not None:
                self._base_canvas.delete(image_id)

    def _paint_cells(self, points: t.Set[Point], state: CellState):
        cell_image = self.skin.cell_falling_image if state == CellState.FALLING else self.skin.cell_filled_image
        for point in points:
            self._game_field_cells[point] = (self._paint_cell(point, cell_image), state)

    def game_over(self):
        pass

    def toggle_pause(self):
        if self._pause_image_id is not None:
            self._base_canvas.delete(self._pause_image_id)
            self._pause_image_id = None
        else:
            self._pause_image_id = self._base_canvas.create_image(self.skin.pause_image_offset_x,
                                                                  self.skin.pause_image_offset_y,
                                                                  anchor=tk.NW, image=self.skin.pause_image)

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
        popup.add_separator()
        popup.add_command(label='New Game', command=self.new_game)

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
    Connects GUI, controls and game logic
    """
    controls_handler = ControlsHandler()

    # Create main GUI class and bind controls handler to it
    gui = TkTetrisGUI()
    gui.bind(sequence='<KeyPress>', func=controls_handler.on_key_press)
    gui.bind(sequence='<KeyRelease>', func=controls_handler.on_key_release)
    gui.geometry("+800+300")

    # Game logic class - binds GUI, controls and logic together
    Game(controls_handler=controls_handler, gui=gui)

    # Start application
    gui.mainloop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--log-level', default='WARNING', dest='log_level',
                        help='Logging level. Example --loglevel=DEBUG, default level - WARNING')
    args = parser.parse_args()

    logger.setLevel(args.log_level.upper())

    main()
