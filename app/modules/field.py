import random
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
    Game field
    """

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self._cell_states = [[CellState.EMPTY for _ in range(height)] for _ in range(width)]
        self._field_lock = threading.RLock()  # block simultaneous changes
        self._figure: t.Optional[f.Figure] = None  # Current falling figure
        self._next_figure: t.Optional[f.Figure] = random.choice(f.all_figures)()  # Next figure to spawn
        self.q: Queue[t.Dict[CellState, t.Set[f.Point]]] = Queue()  # cells events

    def _move(self, x_diff=0, y_diff=0) -> t.OrderedDict[CellState, t.Set[f.Point]]:
        """Move current figure"""
        with self._field_lock:
            if self._figure.position is None:  # Figure isn't placed anywhere
                return OrderedDict()
            changed_points = self._try_place(
                f.Point(self._figure.position.x + x_diff, self._figure.position.y + y_diff))
            self._apply_changes(changed_points)
            return changed_points

    def move_left(self) -> t.OrderedDict[CellState, t.Set[f.Point]]:
        """Move current figure one cell left"""
        return self._move(x_diff=-1)

    def move_right(self) -> t.OrderedDict[CellState, t.Set[f.Point]]:
        """Move current figure one cell right"""
        return self._move(x_diff=1)

    def move_down(self) -> t.OrderedDict[CellState, t.Set[f.Point]]:
        """Move current one cell down"""
        return self._move(y_diff=1)

    def tick(self) -> t.OrderedDict[CellState, t.Set[f.Point]]:
        """What to do on each step"""

        # Spawn figure if needed (on startup)
        if self._figure is None:
            spawn_result = self.spawn_figure()
            self._apply_changes(spawn_result)
            return spawn_result

        # Try to move current fig down
        move_result = self.move_down()
        if len(move_result) > 0:
            self._apply_changes(move_result)
            return move_result
        else:  # if we cannot move - we hit the bottom
            logger.debug('FIXING FIGURE')
            fix_result = self._fix_figure()
            self._apply_changes(fix_result)
            spawn_result = self.spawn_figure()
            fix_result.update(spawn_result)
            if len(spawn_result) == 0:
                return OrderedDict()  # game over
            return fix_result

    def _fix_figure(self) -> t.OrderedDict[CellState, t.Set[f.Point]]:
        result = OrderedDict()
        points = self._figure.get_points()
        result[CellState.EMPTY] = points
        result[CellState.FILLED] = points
        return result

    def rotate(self) -> t.OrderedDict[CellState, t.Set[f.Point]]:
        """Rotate current figure clockwise"""
        logger.debug('ROTATE')
        if self._figure.position is None:
            return OrderedDict()
        with self._field_lock:
            for position in [self._figure.position,
                             (f.Point(self._figure.position[0] - 1, self._figure.position[1])),
                             (f.Point(self._figure.position[0], self._figure.position[1] - 1)),
                             (f.Point(self._figure.position[0] - 1, self._figure.position[1] - 1))]:
                changed_points = self._try_place(position, next_rotation=True)
                if len(changed_points) > 0:
                    self._apply_changes(changed_points)
                    return changed_points
            return OrderedDict()

    def spawn_figure(self) -> t.OrderedDict[CellState, t.Set[f.Point]]:
        """Spawn the new figure"""
        with self._field_lock:
            self._figure = self._next_figure
            self._next_figure = random.choice(f.all_figures)()
            result = self._try_place(f.Point(int(self.width / 2) - 2, 0))  # if it's False - game over
            if len(result) == 0:
                logger.info('Cannot spawn new figure!')
            return result

    def get(self, x: int, y: int) -> CellState:
        """Returns cell by coordinates"""
        with self._field_lock:
            return self._cell_states[x][y]

    def set(self, x: int, y: int, cell: CellState):
        """Set cell to coordinates"""
        assert 0 <= x < self.width
        assert 0 <= y < self.height
        with self._field_lock:
            self._cell_states[x][y] = cell

    def get_full_row(self) -> t.Optional[int]:
        with self._field_lock:
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

    def _can_place(self, points: t.Set[f.Point]) -> bool:
        """Check if given set of points could be placed on field -
            it checks if it isn't out of borders and there is no filled cells"""
        with self._field_lock:
            for new_x, new_y in points:
                if not (0 <= new_x < self.width and 0 <= new_y < self.height and
                        self.get(new_x, new_y) != CellState.FILLED):
                    return False
            return True

    def _apply_changes(self, changed_points: t.OrderedDict[CellState, t.Set[f.Point]]):
        """Apply a bunch of changes to the field"""
        with self._field_lock:
            self.q.put(changed_points)
            for cell_state, points in changed_points.items():
                for point in points:
                    self.set(point.x, point.y, cell_state)
            logger.debug('Field after _apply_changes: %s', self)

    def _try_place(self, new_position: f.Point, next_rotation=False) -> t.OrderedDict[CellState, t.Set[f.Point]]:
        """
        Trying to place figure into given position.
        Returns a map which contains field coordinates to be changed and what state each of them should have
        """
        result = OrderedDict()
        with self._field_lock:
            # Check if we can place figure into new position
            points_to_clear = self._figure.get_points()
            logger.debug('Cur pts: %s', sorted(points_to_clear))
            target_points = self._figure.get_points(new_position, next_rotation)
            logger.debug('Tar pts: %s', sorted(target_points))
            if not self._can_place(target_points):
                logger.debug(f'Cannot place figure to {new_position}{" with next rotation" if next_rotation else ""}')
                return result

            # Can place figure, now clear its old points and fill new
            self._figure.position = new_position
            if next_rotation:
                self._figure.rotate()

            result[CellState.EMPTY] = points_to_clear
            result[CellState.FALLING] = target_points
            return result

    def __str__(self):
        header = '   ' + ''.join([f' {i} ' for i in range(self.width)]) + '  \n'
        field_str = '\n' + header
        for y in range(self.height):
            field_str += f'{y:>2d}|'
            for x in range(self.width):
                state = self.get(x, y)
                # M for moving, X for fiXed
                field_str += ' : ' if state == CellState.EMPTY else '[M]' if state == CellState.FALLING else '[X]'
            field_str += f'|{y:<2d}\n'
        field_str += header
        return field_str
