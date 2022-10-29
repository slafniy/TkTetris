import os
import threading
import tkinter as tk
import typing as t

import figures
import keyboard_handler
import game

# Default field parameters
CELL_SIZE = 24  # In pixels, this is base size for all
CELL_INTERNAL_BORDER = 4
FIELD_HEIGHT = 20  # In cells
FIELD_HIDDEN_TOP_ROWS_NUMBER = 4
FIELD_WIDTH = 10  # In cells
COLOR_BACKGROUND = "#FF00FF"


def main():
    # Create root UI thread and main window
    root = tk.Tk()

    # Load resources
    resources_path = os.path.join(os.path.realpath(__file__), '../../res/ClassicMonochrome')
    filled_cell_image = tk.PhotoImage(file=os.path.join(resources_path, "cell_filled.png"))
    falling_cell_image = tk.PhotoImage(file=os.path.join(resources_path, "cell_falling.png"))
    background_image = tk.PhotoImage(file=os.path.join(resources_path, "background.png"))
    game_over_image = tk.PhotoImage(file=os.path.join(resources_path, "game_over.png"))
    pause_image = tk.PhotoImage(file=os.path.join(resources_path, "pause.png"))

    # Draw background, draw labels etc.
    ui_field = tk.Canvas(master=root, background=COLOR_BACKGROUND,
                         height=FIELD_HEIGHT * CELL_SIZE,
                         width=FIELD_WIDTH * CELL_SIZE)

    ui_field.pause_image_id: int = None  # Create field to control pause TODO: looks terrible. Or not?

    ui_field.grid()
    # TODO: get rid of this magic number!
    ui_field.create_image(2, 2, anchor=tk.NW, image=background_image)
    # game_score = tk.Label(master=root, text="Scores: 0")
    # game_score.grid(column=1, row=0, sticky=tk.N)

    # Create area to show the next figure
    next_figure_field = tk.Canvas(master=root, background=COLOR_BACKGROUND,
                                  height=4 * CELL_SIZE,
                                  width=4 * CELL_SIZE)
    next_figure_field.create_image(0, 0, anchor=tk.NW, image=background_image)
    next_figure_field.grid(column=1, row=0, sticky=tk.N)

    game_over_event = threading.Event()

    # Bind keyboard listener
    key_handler = keyboard_handler.KeyboardHandler(game_over_event)
    root.bind(sequence='<KeyPress>', func=key_handler.on_key_press)
    root.bind(sequence='<KeyRelease>', func=key_handler.on_key_release)

    def paint_filled(x, y):
        _x = x * CELL_SIZE + 2  # TODO: get rid of this magic
        _y = (y - FIELD_HIDDEN_TOP_ROWS_NUMBER) * CELL_SIZE + 2  # TODO: get rid of this magic
        return ui_field.create_image(_x, _y, anchor=tk.NW, image=filled_cell_image)

    def paint_falling(x, y):
        _x = x * CELL_SIZE + 2  # TODO: get rid of this magic
        _y = (y - FIELD_HIDDEN_TOP_ROWS_NUMBER) * CELL_SIZE + 2  # TODO: get rid of this magic
        return ui_field.create_image(_x, _y, anchor=tk.NW, image=falling_cell_image)

    def paint_next(points: t.List[figures.Point]):
        next_figure_field.create_image(0, 0, anchor=tk.NW, image=background_image)  # clear all previous
        for x, y in points:
            _x = x * CELL_SIZE + 2
            _y = y * CELL_SIZE + 2
            next_figure_field.create_image(_x, _y, anchor=tk.NW, image=falling_cell_image)

    def toggle_pause():
        if ui_field.pause_image_id is not None:
            ui_field.delete(ui_field.pause_image_id)
            ui_field.pause_image_id = None
        else:
            ui_field.pause_image_id = ui_field.create_image(FIELD_WIDTH / 2 * CELL_SIZE,
                                                            FIELD_HEIGHT / 2 * CELL_SIZE,
                                                            anchor=tk.CENTER, image=pause_image)

    def on_close():
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)

    # Game field binds UI and logic together
    g = game.Game(width=FIELD_WIDTH, height=FIELD_HEIGHT + FIELD_HIDDEN_TOP_ROWS_NUMBER,
                  paint_filled=paint_filled,
                  paint_falling=paint_falling,
                  paint_next=paint_next,
                  delete_image=ui_field.delete,
                  toggle_pause=toggle_pause,
                  refresh_ui=ui_field.update,
                  game_over_event=game_over_event)

    # Bind keyboard handler to Field methods
    key_handler.move_left_func = g.move_left
    key_handler.move_right_func = g.move_right
    key_handler.force_down_func = g.move_down  # TODO: replace to force down when ready
    key_handler.rotate_func = g.rotate
    key_handler.pause_func = g.pause

    root.geometry("+960+500")

    # Start application
    root.mainloop()
