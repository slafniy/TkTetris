"""Game field logic"""
import random
import time
import threading
import typing as t
from collections import OrderedDict
from multiprocessing import Queue

from .logger import logger
from .cell import CellState
from . import figures as f

FIELD_HIDDEN_TOP_ROWS_NUMBER = 4


class Field:
    """
    Game field - provides methods to manipulate figures and queue to monitor changes
    """

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self._cell_states = [[CellState.EMPTY for _ in range(height)] for _ in range(width)]
        self._field_lock = threading.RLock()  # block simultaneous changes
        self._figure: t.Optional[f.Figure] = None  # Current falling figure
        self._next_figure: t.Optional[f.Figure] = random.choice(f.all_figures)()  # Next figure to spawn
        self.graphic_events_q: Queue[t.Dict[CellState, t.Set[f.Point]]] = Queue()  # cells events

    def _move(self, x_diff=0, y_diff=0) -> bool:
        """Move current figure"""
        with self._field_lock:
            if self._figure.position is None:  # Figure isn't placed anywhere
                return False
            return self._try_place(f.Point(self._figure.position.x + x_diff, self._figure.position.y + y_diff))

    def move_left(self) -> bool:
        """Move current figure one cell left"""
        return self._move(x_diff=-1)

    def move_right(self) -> bool:
        """Move current figure one cell right"""
        return self._move(x_diff=1)

    def move_down(self) -> bool:
        """Move current one cell down"""
        return self._move(y_diff=1)

    def tick(self) -> bool:
        """What to do on each step"""
        # Check if there is some row to destroy
        self._destroy_full_row()

        # Spawn figure if needed (on startup)
        if self._figure is None:
            self._new_figure()

        # Try to move current fig down
        if not self.move_down():
            return self._new_figure()  # try spawn new figure if we cannot move current

        return True

    def rotate(self) -> bool:
        """Rotate current figure clockwise"""
        logger.debug('ROTATE')
        if self._figure.position is None:
            return False
        with self._field_lock:
            for position in [self._figure.position,
                             (f.Point(self._figure.position[0] - 1, self._figure.position[1])),
                             (f.Point(self._figure.position[0], self._figure.position[1] - 1)),
                             (f.Point(self._figure.position[0] - 1, self._figure.position[1] - 1))]:
                if self._try_place(position, next_rotation=True):
                    return True
            return False

    def _fix_figure(self):
        logger.debug('Fixing current figure')
        result = OrderedDict()
        points = self._figure.get_points()
        result[CellState.EMPTY] = points
        result[CellState.FILLED] = points
        self._apply_changes(result)

    def _new_figure(self) -> bool:
        """Spawn the new figure"""
        with self._field_lock:
            if self._figure is not None:
                self._fix_figure()

            self._figure = self._next_figure
            self._next_figure = random.choice(f.all_figures)()
            if not self._try_place(f.Point(int(self.width / 2) - 2, 0)):  # if it's False - game over
                logger.info('Cannot spawn new figure!')
                return False
            return True

    def _get(self, x: int, y: int) -> CellState:
        """Returns cell by coordinates"""
        with self._field_lock:
            return self._cell_states[x][y]

    def _set(self, x: int, y: int, cell: CellState):
        """Set cell to coordinates"""
        assert 0 <= x < self.width
        assert 0 <= y < self.height
        with self._field_lock:
            self._cell_states[x][y] = cell

    def _destroy_full_row(self):
        row_index = self._get_full_row()
        if row_index is None:
            return

        cells_to_destroy = {f.Point(x, row_index) for x in range(self.width)}
        cells_to_move_down = set()
        for x in range(self.width):
            for y in range(0, row_index):
                if self._get(x, y) == CellState.FILLED:
                    cells_to_move_down.add(f.Point(x, y + 1))
                    cells_to_destroy.add(f.Point(x, y))

        self._apply_changes(OrderedDict({CellState.EMPTY: cells_to_destroy,
                                         CellState.FILLED: cells_to_move_down}))

    def _get_full_row(self) -> t.Optional[int]:
        with self._field_lock:
            for y in range(self.height - 1, -1, -1):
                is_full = True
                for x in range(self.width):
                    if self._get(x, y) != CellState.FILLED:
                        is_full = False
                        break
                if is_full:
                    logger.debug('Row %i is full', y)
                    return y
            return None

    def _can_place(self, points: t.Set[f.Point]) -> bool:
        """Check if given set of points could be placed on field -
            it checks if it isn't out of borders and there is no filled cells"""
        with self._field_lock:
            for new_x, new_y in points:
                if not (0 <= new_x < self.width and 0 <= new_y < self.height and
                        self._get(new_x, new_y) != CellState.FILLED):
                    return False
            return True

    def _apply_changes(self, changed_points: t.OrderedDict[CellState, t.Set[f.Point]]):
        """Apply a bunch of changes to the field"""
        with self._field_lock:
            for cell_state, points in changed_points.items():
                graphics_patch = {cell_state: set()}
                logger.debug(f'FIELD APPLY: {cell_state}: {points}')
                for point in points:
                    self._set(point.x, point.y, cell_state)
                    # make conversions to hide top cells from graphics - virtually move field up and ignore top rows
                    fake_y = point.y - FIELD_HIDDEN_TOP_ROWS_NUMBER
                    if fake_y >= 0:
                        graphics_patch[cell_state].add(f.Point(point.x, fake_y))
                self.graphic_events_q.put(graphics_patch)
            # logger.debug('Field after _apply_changes: %s', self)

    def _try_place(self, new_position: f.Point, next_rotation=False) -> bool:
        """
        Trying to place figure into given position.
        Returns True in case of success false otherwise
        """
        with self._field_lock:
            # Check if we can place figure into new position
            points_to_clear = self._figure.get_points()
            target_points = self._figure.get_points(new_position, next_rotation)
            if not self._can_place(target_points):
                logger.debug(f'Cannot place figure to {new_position}{" with next rotation" if next_rotation else ""}')
                return False

            # Can place figure, now clear its old points and fill new
            self._figure.position = new_position
            if next_rotation:
                self._figure.rotate()

            result = OrderedDict()
            result[CellState.EMPTY] = points_to_clear
            result[CellState.FALLING] = target_points
            self._apply_changes(result)
            return True

    def __str__(self):
        header = '   ' + ''.join([f' {i} ' for i in range(self.width)]) + '  \n'
        field_str = '\n' + header
        for y in range(self.height):
            field_str += f'{y:>2d}|'
            for x in range(self.width):
                state = self._get(x, y)
                # M for moving, X for fiXed
                field_str += ' : ' if state == CellState.EMPTY else '[M]' if state == CellState.FALLING else '[X]'
            field_str += f'|{y:<2d}\n'
        field_str += header
        return field_str
