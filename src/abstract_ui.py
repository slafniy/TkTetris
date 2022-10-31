import typing as t
from abc import ABC, abstractmethod

import simpleaudio as sa

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

    @property
    @abstractmethod
    def wav_background(self) -> sa.WaveObject:
        """
        Background music
        """
        pass

    @property
    @abstractmethod
    def wav_move(self) -> sa.WaveObject:
        """
        Sound for figure move
        """
        pass

    @property
    @abstractmethod
    def wav_rotate(self) -> sa.WaveObject:
        """
        Sound for figure rotates
        """
        pass

    @property
    @abstractmethod
    def wav_fix(self) -> sa.WaveObject:
        """
        Sound when figure fixes
        """
        pass

    @property
    @abstractmethod
    def wav_row_delete(self) -> sa.WaveObject:
        """
        Sound when row removed
        """
        pass

    @property
    @abstractmethod
    def wav_tick(self) -> sa.WaveObject:
        """
        Sound when figure falls one cell down
        """
        pass
