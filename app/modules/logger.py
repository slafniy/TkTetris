"""Logger module that provides basic logger"""
import logging
import sys


class Logger(logging.Logger):
    """Pre-formatted logger"""
    def __init__(self, name: str, level):
        super().__init__(name)
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(level)
        formatter = logging.Formatter('%(asctime)s %(name)s [%(levelname)s]: %(message)s')
        stream_handler.setFormatter(formatter)
        self.addHandler(stream_handler)


def __get_logger():
    """Generator to made logger initialized once"""
    one_logger = Logger('Tetris', logging.DEBUG)
    while True:
        yield one_logger


__get_logger_gen = __get_logger()
logger = next(__get_logger_gen)
