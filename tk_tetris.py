import os
import threading
import tkinter as tk

import time

import field
import game_logic

# Default key binds
MOVE_LEFT = 37  # Left arrow
MOVE_RIGHT = 39  # Right arrow
ROTATE = 38  # Up arrow
FORCE_DOWN = 40  # Down arrow
PAUSE = 32  # Space

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


def key_pressed(event):
    """
    Keyboard handler
    """
    print("Key pressed: {} {}".format(event.keycode, event.keysym))
    # Make a decision what should we do with this key (Where is my switch keyword??)
    if event.keycode == MOVE_LEFT:
        process_move_left()
    elif event.keycode == MOVE_RIGHT:
        process_move_right()
    elif event.keycode == ROTATE:
        process_rotate()
    elif event.keycode == FORCE_DOWN:
        # import threading
        process_force_down()
        # t = threading.Thread(target=process_force_down())
        # t.start()
    elif event.keycode == PAUSE:
        process_pause()


def process_move_left():
    print("Process move left...")


def process_move_right():
    print("Process move right...")


def process_rotate():
    print("Process rotate...")


def process_force_down():
    print("Process force down...")
    points = [(6, 2), (6, 3), (6, 4), (5, 4), (7, 4)]
    for p in points:
        game_field.get_cell(p[0], p[1]).state = field.CellState.FILLED
    repaint_all()


def process_pause():
    print("Process pause...")
    test_draw()


def test_draw():
    import time
    import random

    x_list = list(range(FIELD_WIDTH))
    y_list = list(range(FIELD_HEIGHT))
    for i in range(10):
        x = random.choice(x_list)
        y = random.choice(y_list)
        state = random.choice([e for e in field.CellState])
        game_field.get_cell(x, y).state = state


# Bind keyboard listener
# TODO: try KeyPress event
root.bind(sequence='<Key>', func=key_pressed)

# Draw background, draw labels etc.
ui_field = tk.Canvas(master=root, background=COLOR_BACKGROUND,
                     height=FIELD_HEIGHT * CELL_SIZE,
                     width=FIELD_WIDTH * CELL_SIZE)
ui_field.grid()
# TODO: get rid of this magic number!
ui_field.create_image(2, 2, anchor=tk.NW, image=background_image)
game_score = tk.Label(master=root, text="Scores: 0")
game_score.grid(column=1, row=0, sticky=tk.N)


def repaint_all():
    for x in range(FIELD_WIDTH):
        for y in range(FIELD_HEIGHT):
            cell = game_field.get_cell(x, y)
            print(">>", cell.state)
            if cell.state in (field.CellState.FILLED, field.CellState.FALLING) and cell.image_id is None:
                _x = x * CELL_SIZE + 2  # TODO: get rid of this magic number!
                _y = y * CELL_SIZE + 2
                img = filled_cell_image if cell.state == field.CellState.FILLED else falling_cell_image
                cell.image_id = ui_field.create_image(_x, _y, anchor=tk.NW, image=img)
                ui_field.update()
            elif cell.state == field.CellState.EMPTY and cell.image_id is not None:
                ui_field.delete(cell.image_id)
                cell.image_id = None
                ui_field.update()


# Game field binds UI and logic together
game_field = field.Field(FIELD_WIDTH, FIELD_HEIGHT)


def tick():
    while True:
        test_draw()
        repaint_all()
        time.sleep(2)

tick_thread = threading.Thread(target=tick)
tick_thread.start()

# Start application
root.mainloop()