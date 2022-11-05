"""Module to read skin files, configs and prepare data for use"""
import dataclasses
import pathlib
import sys
import typing as t
import tkinter as tk

import simpleaudio as sa
import yaml


@dataclasses.dataclass
class Sounds:
    """
    Contains all required sounds in WaveObject format
    """
    move: sa.WaveObject
    rotate: sa.WaveObject
    row_delete: sa.WaveObject
    tick: sa.WaveObject
    fix_figure: sa.WaveObject
    game_over: sa.WaveObject
    startup: sa.WaveObject


@dataclasses.dataclass
class Skin:  # pylint: disable=too-many-instance-attributes # it's fine for a dataclass
    """Describes skin images and image coordinates and sounds"""
    # The big one
    base_image: tk.PhotoImage
    game_field_offset_x: int
    game_field_offset_y: int

    next_figure_field_offset_x: int
    next_figure_field_offset_y: int

    pause_image: tk.PhotoImage
    pause_image_offset_x: int
    pause_image_offset_y: int

    # Cells
    cell_falling_image: tk.PhotoImage
    cell_filled_image: tk.PhotoImage
    cell_size: int
    cell_anchor_offset_x: int
    cell_anchor_offset_y: int

    # Score digits
    digit_images: t.Dict[str, tk.PhotoImage]
    digit_width: int
    digit_height: int
    score_digit_offset_x: int
    score_digit_offset_y: int

    # Sounds
    sounds: Sounds


def _get_resources_path() -> pathlib.Path:
    """
    Need this for PyInstaller
    """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        base_path = pathlib.Path(sys._MEIPASS) / 'app'  # pylint: disable=protected-access
    else:
        base_path = pathlib.Path(__file__).parent.parent
    return base_path / 'res'


def _get_sounds(skin_name) -> Sounds:
    """Returns initialized sounds"""

    def get_wav(wav_name: str):
        return sa.WaveObject.from_wave_file(
            str(_get_resources_path() / skin_name / 'sound' / f'{wav_name}.wav'))

    return Sounds(
        move=get_wav('move'),
        rotate=get_wav('rotate'),
        row_delete=get_wav('row_delete'),
        tick=get_wav('tick'),
        fix_figure=get_wav('fix_figure'),
        game_over=get_wav('game_over'),
        startup=get_wav('startup')
    )


def get_skin(skin_name) -> Skin:
    """Returns initialized skin"""
    gfx_resources_path = _get_resources_path() / f'{skin_name}' / 'gfx'

    with (gfx_resources_path / "cfg.yaml").open() as yaml_file:
        cfg = yaml.safe_load(yaml_file)

    return Skin(

        base_image=tk.PhotoImage(file=str(gfx_resources_path / "base.png")),

        cell_size=cfg['cell_size'],
        game_field_offset_x=cfg['game_field_nw']['x'],
        game_field_offset_y=cfg['game_field_nw']['y'],

        next_figure_field_offset_x=cfg['next_figure_field_nw']['x'],
        next_figure_field_offset_y=cfg['next_figure_field_nw']['y'],

        cell_anchor_offset_x=cfg['cell_anchor_nw']['x'],
        cell_anchor_offset_y=cfg['cell_anchor_nw']['y'],

        cell_falling_image=tk.PhotoImage(file=str(gfx_resources_path / "cell_falling.png")),
        cell_filled_image=tk.PhotoImage(file=str(gfx_resources_path / "cell_filled.png")),

        pause_image=tk.PhotoImage(file=str(gfx_resources_path / "pause.png")),
        pause_image_offset_x=cfg['pause_nw']['x'],
        pause_image_offset_y=cfg['pause_nw']['y'],

        # Scores
        score_digit_offset_x=cfg['score_digit_nw']['x'],
        score_digit_offset_y=cfg['score_digit_nw']['y'],
        digit_width=cfg['digit_size']['width'],
        digit_height=cfg['digit_size']['height'],
        digit_images={str(digit): tk.PhotoImage(file=str(gfx_resources_path / f"{digit}.png"))
                      for digit in range(10)},

        sounds=_get_sounds(skin_name)
    )
