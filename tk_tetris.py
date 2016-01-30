import os
import tkinter as tk

import custom_threads
import game_logic
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

# Draw background, draw labels etc.
ui_field = tk.Canvas(master=root, background=COLOR_BACKGROUND,
                     height=FIELD_HEIGHT * CELL_SIZE,
                     width=FIELD_WIDTH * CELL_SIZE)
ui_field.grid()
# TODO: get rid of this magic number!
ui_field.create_image(2, 2, anchor=tk.NW, image=background_image)
game_score = tk.Label(master=root, text="Scores: 0")
game_score.grid(column=1, row=0, sticky=tk.N)

# Game field binds UI and logic together
field = game_logic.Field(FIELD_WIDTH, FIELD_HEIGHT)

repaint_event = custom_threads.NeedRepaintEvent()

# Create game instance
logic = game_logic.Game(field)

key_handler = keyboard_handler.KeyboardHandler(field)

# Bind keyboard listener
root.bind(sequence='<KeyPress>', func=key_handler.on_key_press)
root.bind(sequence='<KeyRelease>', func=key_handler.on_key_release)


all_points = []
for _x in range(FIELD_WIDTH):
    for _y in range(FIELD_HEIGHT):
        all_points.append((_x, _y))


def repaint(points=all_points):
    for x, y in points:
        cell = field.get_cell_copy(x, y)
        if (cell.state == game_logic.CellState.EMPTY and cell.image_id is not None) or cell.need_img_replace:
            ui_field.delete(cell.image_id)
            field.set_cell_image_id(x, y, None)
            field.set_cell_need_img_replace(x, y, False)
        if cell.state in (game_logic.CellState.FILLED, game_logic.CellState.FALLING) and cell.image_id is None:
            _x = x * CELL_SIZE + 2  # TODO: get rid of this magic number!
            _y = y * CELL_SIZE + 2
            img = filled_cell_image if cell.state == game_logic.CellState.FILLED else falling_cell_image
            field.set_cell_image_id(x, y, ui_field.create_image(_x, _y, anchor=tk.NW, image=img))
    ui_field.update()


def on_close():
    # TODO: find a way to stop background threads immediately
    root.destroy()
    print("!! Bye !!")

root.protocol("WM_DELETE_WINDOW", on_close)

repaint_thread = custom_threads.RepaintThread(repaint_event, repaint)
repaint_thread.start()

field.spawn_figure()

# Start application
root.mainloop()