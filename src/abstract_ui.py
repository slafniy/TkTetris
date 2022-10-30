import typing as t
from abc import ABC, abstractmethod

import figures


class AbstractUI(ABC):

    @abstractmethod
    def paint_filled(self, x: int, y: int) -> int:
        """
        Paints filled cell on game field
        """
        pass

    @abstractmethod
    def paint_falling(self, x: int, y: int) -> int:
        """
        Paints falling cell on game field
        """
        pass

    @abstractmethod
    def delete_image(self, img_id: int):
        """
        Deletes image from game field via ID
        """
        pass

    @abstractmethod
    def toggle_pause(self):
        """
        Shows/hides PAUSE text
        """
        pass

    @abstractmethod
    def game_over(self):
        """
        Shows GAME OVER banner
        """
        pass

    @abstractmethod
    def refresh_ui(self):
        """
        Trigger re-painting event
        """
        pass

    @abstractmethod
    def show_next_figure(self, points: t.Set[figures.Point]):
        """
        Show the next figure in the separate field
        """
        pass
