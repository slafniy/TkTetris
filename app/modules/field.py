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
        with self._lock:
            return self._try_place(f.Point(self._figure.position.x + x_diff, self._figure.position.y + y_diff))

    def move_left(self):
        """Move current figure one cell left"""
        return self._move(x_diff=-1)

    def move_right(self):
        """Move current figure one cell right"""
        return self._move(x_diff=1)

    def move_down(self):
        """Move current one cell down"""
        return self._move(y_diff=1)

    def rotate(self) -> bool:
        """Rotate current figure clockwise"""
        with self._lock:
            current_rotation = self._figure.rotation
            self._figure.set_next_rotation()
            if self._try_place(f.Point(self._figure.position.x, self._figure.position.y)):
                return True
            if self._try_place(f.Point(self._figure.position[0] - 1, self._figure.position[1])):
                return True
            if self._try_place(f.Point(self._figure.position[0], self._figure.position[1] - 1)):
                return True
            if self._try_place(f.Point(self._figure.position[0] - 1, self._figure.position[1] - 1)):
                return True
            self._figure.rotation = current_rotation
            return False

    def spawn_figure(self):
        """Spawn the new figure"""
        with self._lock:
            if self._figure is not None:
                for point in self._figure.get_points():
                    self.set(point.x, point.y, CellState.FILLED)
            self._figure = self._next_figure
            self._next_figure = random.choice(f.all_figures)()
            result = self._try_place(f.Point(FIELD_HIDDEN_TOP_ROWS_NUMBER, 0))  # if it's False - game over
            if not result:
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

    def _try_place(self, new_position: f.Point) -> bool:
        with self._lock:
            # Check if we can place figure into new position
            target_points = self._figure.get_points(new_position)
            for new_x, new_y in target_points:
                if not (0 <= new_x < self.width and 0 <= new_y < self.height and
                        self.get(new_x, new_y) != CellState.FILLED):
                    logger.debug(f'Cannot place figure to {new_position}')
                    return False

            # Can place figure, now clear its old points and fill new
            points_to_clear = self._figure.get_points()
            logger.debug('Old points: %s', sorted(points_to_clear))
            logger.debug('New points: %s', sorted(target_points))
            self._figure.position = new_position
            for point in points_to_clear:
                self.set(point.x, point.y, CellState.EMPTY)
            for point in target_points:
                self.set(point.x, point.y, CellState.FALLING)
            logger.debug('Field after _try_place: %s', self)
            return True

    def __str__(self):
        header = '   ' + ''.join([f' {i} ' for i in range(self.width)]) + '  \n'
        field_str = '\n' + header
        for y in range(self.height):
            field_str += f'{y:>2d}-'
            for x in range(self.width):
                state = self.get(x, y)
                # M for moving, X for fiXed
                field_str += ' : ' if state == CellState.EMPTY else '[M]' if state == CellState.FALLING else '[X]'
            field_str += f'-{y:<2d}\n'
        field_str += header
        return field_str
