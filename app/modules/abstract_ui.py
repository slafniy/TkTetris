import typing as t
from abc import ABC, abstractmethod

from . import figures
from . resources import SoundResources


class AbstractUI(ABC):

    @abstractmethod
    def paint_filled(self, x: int, y: int) -> int:
        """
        Paints filled cell on game field
        """

    @abstractmethod
    def paint_falling(self, x: int, y: int) -> int:
        """
        Paints falling cell on game field
        """

    @abstractmethod
    def delete_image(self, img_id: int):
        """
        Deletes image from game field via ID
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
    def show_next_figure(self, points: t.Set[figures.Point]):
        """
        Show the next figure in the separate field
        """

    @property
    @abstractmethod
    def sounds(self) -> SoundResources:
        """
        Returns dataclass with game sounds
        """
