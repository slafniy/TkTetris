"""Description of UI interface"""
import typing as t
from abc import ABC, abstractmethod

from .figures import Point
from .resources import SoundResources
from .cell import CellState


class AbstractGUI(ABC):
    """Interface-like class to describe what abstract UI should have"""

    @abstractmethod
    def apply_field_change(self, changed_points: t.OrderedDict[CellState, t.Set[Point]]) -> int:
        """
        Paints filled cell on game field
        """

    @abstractmethod
    def toggle_pause(self):
        """
        Shows/hides PAUSE text
        """

    @abstractmethod
    def game_over(self):
        """
        Shows GAME OVER banner
        """

    @abstractmethod
    def new_game(self):
        """
        Actions on new game
        """

    @abstractmethod
    def refresh_ui(self):
        """
        Trigger re-painting event
        """

    @abstractmethod
    def show_next_figure(self, points: t.Set[Point]):
        """
        Show the next figure in the separate field
        """

    @abstractmethod
    def show_score(self, score: int):
        """
        Show given score number
        """

    @property
    @abstractmethod
    def sounds(self) -> SoundResources:
        """
        Returns dataclass with game sounds
        """
