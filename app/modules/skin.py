"""Module to read skin files, configs and prepare data for use"""
import pathlib
import sys
import tkinter as tk

import simpleaudio as sa
import yaml


class Skin:
    """Loads skin image and sound resources from files"""
    def __init__(self, name: str):
        self.sounds = SoundResources(name)  # Audio

        gfx_resources_path = _get_resources_path() / f'{name}' / 'gfx'

        with (gfx_resources_path / "cfg.yaml").open() as yaml_file:
            cfg = yaml.safe_load(yaml_file)

        self.base_image = tk.PhotoImage(file=str(gfx_resources_path / "base.png"))

        self.cell_size = cfg['cell_size']
        self.game_field_offset_x = cfg['game_field_nw']['x']
        self.game_field_offset_y = cfg['game_field_nw']['y']

        self.next_figure_field_offset_x = cfg['next_figure_field_nw']['x']
        self.next_figure_field_offset_y = cfg['next_figure_field_nw']['y']

        self.cell_anchor_offset_x = cfg['cell_anchor_nw']['x']
        self.cell_anchor_offset_y = cfg['cell_anchor_nw']['y']

        self.cell_falling_image = tk.PhotoImage(file=str(gfx_resources_path / "cell_falling.png"))
        self.cell_filled_image = tk.PhotoImage(file=str(gfx_resources_path / "cell_filled.png"))

        self.pause_image = tk.PhotoImage(file=str(gfx_resources_path / "pause.png"))
        self.pause_image_offset_x = cfg['pause_nw']['x']
        self.pause_image_offset_y = cfg['pause_nw']['y']

        # Scores
        self.score_digit_offset_x = cfg['score_digit_nw']['x']
        self.score_digit_offset_y = cfg['score_digit_nw']['y']
        self.digit_width = cfg['digit_size']['width']
        self.digit_height = cfg['digit_size']['height']
        self.digit_images = {str(digit): tk.PhotoImage(file=str(gfx_resources_path / f"{digit}.png"))
                             for digit in range(10)}


class SoundResources:
    """
    Contains all required sounds in WaveObject format
    """

    def __init__(self, skin_name='Default'):
        def get_wav(x):
            wav_path = _get_resources_path() / skin_name / 'sound' / f'{x}.wav'
            if wav_path.exists():
                return sa.WaveObject.from_wave_file(str(wav_path))
            raise RuntimeError(f'Cannot find {wav_path}')

        self.move = get_wav('move')
        self.rotate = get_wav('rotate')
        self.row_delete = get_wav('row_delete')
        self.tick = get_wav('tick')
        self.fix_figure = get_wav('fix_figure')
        self.game_over = get_wav('game_over')
        self.startup = get_wav('startup')


def _get_resources_path() -> pathlib.Path:
    """
    Need this for PyInstaller
    """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        base_path = pathlib.Path(sys._MEIPASS) / 'app'  # pylint: disable=protected-access
    else:
        base_path = pathlib.Path(__file__).parent.parent
    return base_path / 'res'
