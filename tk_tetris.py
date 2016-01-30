import os
import random
import subprocess
import threading
import tkinter as tk
import time

import sys

import field_impl
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


# class PressedKey:
#     def __init__(self):
#         self.key_code = None
#         self.times_processed = 0


class KeyboardHandler:
    """
    Possibly this will work fine only on Windows
    """
    def __init__(self, logic: game_logic.Game, interval=0.1):
        self._logic = logic
        self._last_time = time.time()
        self.interval = interval
        self._pressed_keys = dict()
        self._key_processor = threading.Thread(target=self._process_key)
        self._key_processor.start()
        self.processed_once = False

    def on_key_press(self, event):
        print('On key press')
        if event.keycode not in self._pressed_keys:
            self._pressed_keys[event.keycode] = 0

    def on_key_release(self, event):
        print("On key release")
        if event.keycode in self._pressed_keys:
            self._pressed_keys.pop(event.keycode)

    def _process_key(self):
        while True:
            for code in self._pressed_keys:
                # Make a decision what should we do with this key (Where is my switch keyword??)
                if code == MOVE_LEFT:
                    self._process_move_left()
                elif code == MOVE_RIGHT:
                    self._process_move_right()
                elif code == ROTATE:
                    self._process_rotate()
                elif code == FORCE_DOWN:
                    self._process_force_down()
                elif code == PAUSE:
                    self._process_pause()
                self.processed_once = True
            time.sleep(self.interval)

    def _process_move_left(self):
        self._logic.move_left()

    def _process_move_right(self):
        self._logic.move_right()

    def _process_rotate(self):
        pass

    def _process_force_down(self):
        pass

    def _process_pause(self):
        pass


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
field = field_impl.Field(FIELD_WIDTH, FIELD_HEIGHT)
# Create game instance
logic = game_logic.Game(field)

key_handler = KeyboardHandler(logic)

# Bind keyboard listener
root.bind(sequence='<KeyPress>', func=key_handler.on_key_press)
root.bind(sequence='<KeyRelease>', func=key_handler.on_key_release)


def repaint_all():
    for x in range(FIELD_WIDTH):
        for y in range(FIELD_HEIGHT):
            cell = field.get_cell(x, y)
            if (cell.state == field_impl.CellState.EMPTY and cell.image_id is not None) or cell.need_img_replace:
                ui_field.delete(cell.image_id)
                cell.image_id = None
                cell.need_img_replace = False
            if cell.state in (field_impl.CellState.FILLED, field_impl.CellState.FALLING) and cell.image_id is None:
                _x = x * CELL_SIZE + 2  # TODO: get rid of this magic number!
                _y = y * CELL_SIZE + 2
                img = filled_cell_image if cell.state == field_impl.CellState.FILLED else falling_cell_image
                cell.image_id = ui_field.create_image(_x, _y, anchor=tk.NW, image=img)
    ui_field.update()


def do_repaint(fps=60):
    target_step_time = 1 / fps
    while True:
        start_time = time.time()
        repaint_all()
        sleep_time = target_step_time - (time.time() - start_time)
        time.sleep(sleep_time if sleep_time >= 0 else 0)


def on_close():
    # TODO: find a way to stop tick_thread immediately
    tick_thread.stop()
    root.destroy()
    print("!! Bye !!")

root.protocol("WM_DELETE_WINDOW", on_close)

logic.spawn_z()  # TODO: remove

# Start tick tread
tick_thread = game_logic.TickThread(logic.next_step, tick_interval_sec=0.1)
tick_thread.start()

repaint_thread = threading.Thread(target=do_repaint, args=(60,))
repaint_thread.start()

# Start application
root.mainloop()