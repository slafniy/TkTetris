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

key_handler = keyboard_handler.KeyboardHandler()

# Bind keyboard listener
root.bind(sequence='<KeyPress>', func=key_handler.on_key_press)
root.bind(sequence='<KeyRelease>', func=key_handler.on_key_release)


all_points = []
for _x in range(FIELD_WIDTH):
    for _y in range(FIELD_HEIGHT):
        all_points.append((_x, _y))


# TODO: move to repaint thread
def repaint(points=None):
    if points is None:
        points = all_points
    for x, y in points:
        cell_params = field.get_cell_params(x, y)
        if cell_params is not None:
            state, image_id, need_repaint = cell_params
            if need_repaint:
                if state == game_logic.CellState.EMPTY and image_id is not None:
                    ui_field.delete(image_id)
                    field.set_cell_image_id(x, y, None)
                elif state in (game_logic.CellState.FILLED, game_logic.CellState.FALLING) and image_id is None:
                    _x = x * CELL_SIZE + 2  # TODO: get rid of this magic number!
                    _y = y * CELL_SIZE + 2
                    img = filled_cell_image if state == game_logic.CellState.FILLED else falling_cell_image
                    field.set_cell_image_id(x, y, ui_field.create_image(_x, _y, anchor=tk.NW, image=img))
                field.set_cell_need_img_replace(x, y, False)
    ui_field.update()


def on_close():
    # TODO: find a way to stop background threads immediately
    root.destroy()
    print("!! Bye !!")

root.protocol("WM_DELETE_WINDOW", on_close)

repaint_event = custom_threads.NeedRepaintEvent()
repaint_thread = custom_threads.RepaintThread(repaint_event, repaint)

# Game field binds UI and logic together
field = game_logic.Field(FIELD_WIDTH, FIELD_HEIGHT, repaint_event)

# Bind keyboard handler to Field methods
key_handler.move_left_func = field.move_left
key_handler.move_right_func = field.move_right
key_handler.force_down_func = field.move_down  # TODO: replace to force down when ready
# TODO: bind all

# Create game instance
logic = game_logic.Game(field)

tick_thread = custom_threads.TickThread(field.tick, tick_interval_sec=0.5)

# Start application
repaint_thread.start()
tick_thread.start()
root.mainloop()