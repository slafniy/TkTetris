import pathlib

import simpleaudio as sa


RES_ROOT = pathlib.Path(__file__).parent.parent / 'res'


class SoundResources:
    """
    Contains all required sounds in WaveObject format
    """

    def __init__(self, skin_name='Default'):
        def get_wav(x):
            wav_path = RES_ROOT / skin_name / 'sound' / f'{x}.wav'
            if wav_path.exists():
                return sa.WaveObject.from_wave_file(str(wav_path))
            else:
                raise RuntimeError(f'Cannot find {wav_path}')

        self.move = get_wav('move')
        self.rotate = get_wav('rotate')
        self.row_delete = get_wav('row_delete')
        self.tick = get_wav('tick')
        self.fix_figure = get_wav('fix_figure')
        self.game_over = get_wav('game_over')
        self.startup = get_wav('startup')

