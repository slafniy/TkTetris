from dataclasses import dataclass

import simpleaudio as sa


@dataclass(kw_only=True)
class SoundResources:
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
