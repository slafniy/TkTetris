import random
import threading
import typing as t

from .logger import logger
from .cell import CellState
from . import figures as f

FIELD_HIDDEN_TOP_ROWS_NUMBER = 4


class Field:
    """
    Game field
    """

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self._cell_states = [[CellState.EMPTY for _ in range(height)] for _ in range(width)]
        self._lock = threading.RLock()
        self._figure: t.Optional[f.Figure] = None  # Current falling figure
        self._next_figure: t.Optional[f.Figure] = random.choice(f.all_figures)()  # Next figure to spawn

    def _move(self, x_diff=0, y_diff=0) -> bool:
        """Move current figure"""
        result = self.try_place(f.Point(self._figure.position.x + x_diff, self._figure.position.y + y_diff))
        logger.debug('Move result: %s, field: %s', result, self)
        return result

    def move_left(self):
        """Move current figure one cell left"""
        return self._move(x_diff=-1)

    def move_right(self):
        """Move current figure one cell right"""
        return self._move(x_diff=1)

    def move_down(self):
        """Move current one cell down"""
        return self._move(y_diff=1)

    def spawn_figure(self):
        """Spawn the new figure"""
        with self._lock:
            if self._figure is not None:
                for point in self._figure.get_points():
                    self.set(point.x, point.y, CellState.FILLED)
            self._figure = self._next_figure
            self._next_figure = random.choice(f.all_figures)()
            result = self.try_place(f.Point(FIELD_HIDDEN_TOP_ROWS_NUMBER, 0))  # if it's False - game over
            logger.info('Cannot spawn new figure!')
            return result

    def get(self, x: int, y: int) -> CellState:
        """Returns cell by coordinates"""
        with self._lock:
            return self._cell_states[x][y]

    def set(self, x: int, y: int, cell: CellState) -> bool:
        """Set cell to coordinates"""
        with self._lock:
            if not (0 <= x < self.width and 0 <= y < self.height):
                return False
            self._cell_states[x][y] = cell
            return True

    def get_full_row(self) -> t.Optional[int]:
        with self._lock:
            for y in range(self.height - 1, -1, -1):
                is_full = True
                for x in range(self.width):
                    if self.get(x, y) != CellState.FILLED:
                        is_full = False
                        break
                if is_full:
                    logger.debug('Row %i is full', y)
                    return y
            return None

    def try_place(self, new_position: f.Point) -> bool:
        with self._lock:
            # Check if we can place figure into new position
            target_points = self._figure.get_points(new_position)
            for new_x, new_y in target_points:
                if not (0 <= new_x < self.width and 0 <= new_y < self.height and
                        self.get(new_x, new_y) != CellState.FILLED):
                    logger.debug(f'Cannot place figure to {new_position}')
                    return False

            # Can place figure, now clear its old points and fill new
            for point in self._figure.get_points():
                self.set(point.x, point.y, CellState.EMPTY)
            self._figure.position = new_position
            for point in target_points:
                self.set(point.x, point.y, CellState.FALLING)
            return True

    def __str__(self):
        field_str = '\n'
        for y in range(self.height):
            for x in range(self.width):
                state = self.get(x, y)
                # M for moving, X for fiXed
                field_str += '[ ]' if state == CellState.EMPTY else '[M]' if state == CellState.FALLING else '[X]'
            field_str += '\n'
        return field_str
