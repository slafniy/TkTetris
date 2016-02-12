import abc
import copy
import enum
import queue
import random
import threading
import time

import actions
import custom_threads
import figures


class CellState(enum.IntEnum):
    EMPTY = 0
    FILLED = 1
    FALLING = 2


class KeyBinds(enum.Enum):
    """
    Default key binds
    """
    MOVE_LEFT = 37  # Left arrow
    MOVE_RIGHT = 39  # Right arrow
    ROTATE = 38  # Up arrow
    FORCE_DOWN = 40  # Down arrow
    PAUSE = 32  # Space


class Cell:
    """
    Describes cell - internal state and related image id
    """
    def __init__(self):
        self.state = CellState.EMPTY
        self.image_id = None


class BusyWarning(Exception):
    def __init__(self):
        super().__init__()


class GameState(enum.Enum):
    NOT_STARTED = 0
    RUNNING = 1
    PAUSED = 2
    GAME_OVER = 3


class Game(metaclass=abc.ABCMeta):

    """
    Contains information about game field.
    GUI classes should inherit this class and override abstract methods
    """

    def __init__(self, *, width, height):
        self.width = width
        self.height = height
        # An internal structure to store field state (two-dimensional list)
        # TODO: try to use arrays
        self._field = [[Cell() for _ in range(self.height)] for _ in range(self.width)]
        # Current falling figure
        self._figure = None

        self.state = GameState.RUNNING
        self.tick_interval = 0.35
        self.score = 0
        self.level = 1

        self.tick_thread = custom_threads.TickThread(self._tick, self.tick_interval)
        self.tick_thread.start()
        self.tick_thread.start_ticking()

        self._actions_queue = queue.Queue(maxsize=10)
        self._actions_processing_thread = threading.Thread(target=self._process_actions)
        self._actions_processing_thread.start()

        # To not allow simultaneous call of place()
        # TODO: this doesn't look smart, remade
        self._is_placing_figure = True

        self._pressed_keys = set()
        self._move_delay = 0.08
        self._move_thread = threading.Thread(target=self._do_move)
        self._move_thread.start()

    def _do_move(self):
        while True:
            requested_moves = set()
            if KeyBinds.MOVE_RIGHT.value in self._pressed_keys:
                requested_moves.add(self._move_right)
            elif KeyBinds.MOVE_LEFT.value in self._pressed_keys:
                requested_moves.add(self._move_left)
            elif KeyBinds.FORCE_DOWN.value in self._pressed_keys:
                requested_moves.add(self._move_down)
            for move in requested_moves:
                move()
            time.sleep(self._move_delay)

    def _process_actions(self):
        while True:  # TODO: move to the special thread class
            try:
                action = self._actions_queue.get()
            except queue.Empty:
                return
            if isinstance(action, actions.KeyDown):
                # print("Processing {} KeyDown".format(action.key))
                self._pressed_keys.add(action.key)
            elif isinstance(action, actions.KeyUp):
                # print("Processing {} KeyUp".format(action.key))
                if action.key == KeyBinds.ROTATE.value:
                    self._rotate()
                else:
                    try:
                        self._pressed_keys.remove(action.key)
                    except KeyError:
                        pass
            print(self._pressed_keys)

    def _set_cell_state(self, x, y, state: CellState):
        if 0 <= x < self.width and 0 <= y < self.height:
            cell = self._field[x][y]
            cell.state = state
            # Remove existing image
            if cell.image_id is not None:
                self.delete_image(cell.image_id)
            # Paint new image if needed
            if state == CellState.FILLED:
                cell.image_id = self.paint_filled(x, y)
            elif state == CellState.FALLING:
                cell.image_id = self.paint_falling(x, y)

    def _fix_figure(self):
        print("Fixing figure")
        for x, y in self._figure.current_points:
            self._set_cell_state(x, y, CellState.FILLED)
        self.refresh_ui()
        self._figure = None

    def _spawn_figure(self):
        # First, check full rows and clear them if needed
        self._clear_rows()

        # Spawn new if needed
        if self.state == GameState.RUNNING and self._figure is None:
            figure_cls = random.choice(figures.all_figures)
            self._figure = figure_cls()
            can_place = self._place()
            if can_place is False:
                self.state = GameState.GAME_OVER
                print('Cannot place new figure - game over')
            return can_place

    def _place(self, point=(4, 0)):
        self._is_placing_figure = True
        try:
            target_points = set()
            for _x, _y in self._figure.current_matrix():
                x = _x + point[0]
                y = _y + point[1]
                if not (0 <= x < self.width and 0 <= y < self.height and
                        self._field[x][y].state != CellState.FILLED):
                    # print("Cannot place figure to {}".format(point))
                    return False
                target_points.add((x, y))
            initial_points = copy.deepcopy(self._figure.current_points)
            draw_points = target_points.difference(initial_points)
            clear_points = initial_points.difference(target_points)
            self._figure.current_points = target_points

            for x, y in clear_points:
                self._set_cell_state(x, y, CellState.EMPTY)
            for x, y in draw_points:
                self._set_cell_state(x, y, CellState.FALLING)

            self._figure.position = point
            self.refresh_ui()
            # print("Figure placed to {}".format(point))
            return True
        finally:
            self._is_placing_figure = False

    def _move(self, x_diff=0, y_diff=0):
        # print("Trying to move...")
        try:
            if self._is_placing_figure:
                # print("place() method is busy, doing nothing!")
                raise BusyWarning()
            if self._figure is None or self._figure.position is None:
                # print("There is no figure to move")
                return False
            return self._place((self._figure.position[0] + x_diff, self._figure.position[1] + y_diff))
        except BusyWarning:
            pass

    def _move_left(self):
        return self._move(x_diff=-1)

    def _move_right(self):
        return self._move(x_diff=1)

    def _move_down(self):
        return self._move(y_diff=1)

    def _force_down(self):
        pass

    def _rotate(self):
        if self.state == GameState.RUNNING and self._figure is not None:
            current_rotation = self._figure.rotation
            self._figure.set_next_rotation()
            if not self._place(self._figure.position):
                if not self._place((self._figure.position[0] - 1, self._figure.position[1])):
                    if not self._place((self._figure.position[0], self._figure.position[1] - 1)):
                        if not self._place((self._figure.position[0] - 1, self._figure.position[1] - 1)):
                            self._figure.rotation = current_rotation

    def _tick(self):
        if self.state != GameState.RUNNING:
            print("Skip tick because game is not in RUNNING state")
            return

        if self._figure is None:
            print("Trying to spawn new figure")
            self._spawn_figure()
        else:
            # print("Trying to move down current figure")
            can_move = self._move_down()
            if can_move is False:
                print("Cannot move figure anymore, fixing...")
                self._fix_figure()

    def _get_full_row(self):
        for y in range(self.height - 1, -1, -1):
            is_full = True
            for x in range(self.width):
                if self._field[x][y].state != CellState.FILLED:
                    is_full = False
                    break
            if is_full:
                print("Full row:", y)
                return y
        return None

    def _clear_rows(self):
        cleaned_rows_count = 0
        while True:
            row_index = self._get_full_row()
            if row_index is None:
                break

            cells_to_destroy = [(x, row_index) for x in range(self.width)]
            cells_to_move_down = []
            for x in range(self.width):
                for y in range(0, row_index):
                    if self._field[x][y].state == CellState.FILLED:
                        cells_to_move_down.append((x, y))

            for x, y in cells_to_destroy:
                self._set_cell_state(x, y, CellState.EMPTY)
            self.refresh_ui()
            time.sleep(self.tick_interval / 2)

            for x, y in cells_to_move_down:
                self._set_cell_state(x, y, CellState.EMPTY)
            for x, y in cells_to_move_down:
                self._set_cell_state(x, y + 1, CellState.FILLED)
            time.sleep(self.tick_interval / 2)
            self.refresh_ui()
            cleaned_rows_count += 1
        if cleaned_rows_count > 0:
            pts = 100 * self.level * cleaned_rows_count ** 2
            self.score += pts
            print("Added: {} Total: {}".format(pts, self.score))
            self.update_score(self.score)

    @abc.abstractmethod
    def paint_filled(self, x: int, y: int) -> int:
        """
        Should draw a filled (fixed) cell on via coordinates
        :param x: x coord
        :param y: y coord
        :return: image id
        """
        return NotImplemented

    @abc.abstractmethod
    def paint_falling(self, x: int, y: int) -> int:
        """
        Should draw a filled (fixed) cell on via coordinates
        :param x: x coord
        :param y: y coord
        :return: image id
        """
        return NotImplemented

    @abc.abstractmethod
    def delete_image(self, image_id) -> None:
        return NotImplemented

    @abc.abstractmethod
    def refresh_ui(self) -> None:
        return NotImplemented

    @abc.abstractmethod
    def update_score(self, score: int) -> None:
        return NotImplemented

    def add_action(self, action: actions.Action):
        assert isinstance(action, actions.Action)
        try:
            self._actions_queue.put(action)
        except queue.Full:
            print("Cannot add action - queue is full!")
            raise RuntimeError  # TODO: make some decision about this

    def stop_threads(self):
        self.tick_thread.die()