import os
import threading
import tkinter as tk

import custom_threads
import game
import keyboard_handler


# Default field parameters
CELL_SIZE = 24  # In pixels, this is base size for all
CELL_INTERNAL_BORDER = 4
FIELD_HEIGHT = 20  # In cells
FIELD_WIDTH = 10  # In cells
COLOR_BACKGROUND = "#FF00FF"
COLOR_FILLED = "#000000"


# Create root UI thread and main window
root = tk.Tk()

# Load resources
resources_path = os.path.join('Resources/Default')
filled_cell_image = tk.PhotoImage(file=os.path.join(resources_path, "cell_filled.png"))
falling_cell_image = tk.PhotoImage(file=os.path.join(resources_path, "cell_falling.png"))
background_image = tk.PhotoImage(file=os.path.join(resources_path, "background.png"))
game_over_image = tk.PhotoImage(file=os.path.join(resources_path, "game_over.png"))

# Draw background, draw labels etc.
ui_field = tk.Canvas(master=root, background=COLOR_BACKGROUND,
                     height=FIELD_HEIGHT * CELL_SIZE,
                     width=FIELD_WIDTH * CELL_SIZE)
ui_field.grid()
# TODO: get rid of this magic number!
ui_field.create_image(2, 2, anchor=tk.NW, image=background_image)
game_score = tk.Label(master=root, text="Scores: 0")
game_score.grid(column=1, row=0, sticky=tk.N)

key_handler = keyboard_handler.KeyboardHandler()

# Bind keyboard listener
root.bind(sequence='<KeyPress>', func=key_handler.on_key_press)
root.bind(sequence='<KeyRelease>', func=key_handler.on_key_release)


def paint_filled(x, y):
    _x = x * CELL_SIZE + 2  # TODO: get rid of this magic
    _y = y * CELL_SIZE + 2  # TODO: get rid of this magic
    return ui_field.create_image(_x, _y, anchor=tk.NW, image=filled_cell_image)


def paint_falling(x, y):
    _x = x * CELL_SIZE + 2  # TODO: get rid of this magic
    _y = y * CELL_SIZE + 2  # TODO: get rid of this magic
    return ui_field.create_image(_x, _y, anchor=tk.NW, image=falling_cell_image)


def on_close():
    # TODO: find a way to stop background threads immediately
    root.destroy()
    print("!! Bye !!")

root.protocol("WM_DELETE_WINDOW", on_close)

game_over_event = threading.Event()

# Game field binds UI and logic together
g = game.Game(width=FIELD_WIDTH, height=FIELD_HEIGHT,
              paint_filled=paint_filled,
              paint_falling=paint_falling,
              delete_image=ui_field.delete,
              refresh_ui=ui_field.update,
              game_over_event=game_over_event)

# Bind keyboard handler to Field methods
key_handler.move_left_func = g.move_left
key_handler.move_right_func = g.move_right
key_handler.force_down_func = g.move_down  # TODO: replace to force down when ready
key_handler.rotate_func = g.rotate
# TODO: bind all

# Start application
root.mainloop()