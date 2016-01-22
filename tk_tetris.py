import os
import tkinter as tk

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
filled_cell_image = tk.PhotoImage(file=os.path.join(resources_path, "cell.png"))
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
    clear_cell(1, 1)


def process_force_down():
    print("Process force down...")
    draw_cell(1, 1)


def process_pause():
    print("Process pause...")


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


def draw_cell(x, y):
    print("Drawing ", x, y)
    # Check that we tries to fill an existing unfilled cell:
    if 0 <= x <= FIELD_WIDTH - 1 and 0 <= y <= FIELD_HEIGHT - 1 and ui_cells[x][y] is None:
        _x = x * CELL_SIZE + 2  # TODO: get rid of this magic number!
        _y = y * CELL_SIZE + 2
        img_index = ui_field.create_image(_x, _y, anchor=tk.NW, image=filled_cell_image)
        ui_cells[x][y] = img_index
        ui_field.update()


def clear_cell(x, y):
    # Check that we tries to fill an existing cell:
        if 0 <= x <= FIELD_WIDTH - 1 and 0 <= y <= FIELD_HEIGHT - 1:
            ui_field.delete(ui_cells[x][y])
            ui_cells[x][y] = None
            ui_field.update()


def repaint_all():
    pass


# Create game instance
game = game_logic.Game(FIELD_WIDTH, FIELD_HEIGHT)
# Create container for filled cells
ui_cells = [[None for _ in range(FIELD_HEIGHT)] for _ in range(FIELD_WIDTH)]

game.field[0][4] = game_logic.Cell.FALLING
game.field[2][5] = game_logic.Cell.FALLING
game.field[3][1] = game_logic.Cell.FALLING
repaint_all()

# Start application
root.mainloop()