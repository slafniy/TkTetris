import time
import threading

import simpleaudio as sa


class MusicThread(threading.Thread):
    """
    Special thread that endlessly run wav file
    """

    def __init__(self, wav: sa.WaveObject):
        super().__init__(daemon=True)
        self._wav = wav

    def run(self):
        while True:
            self._wav.play().wait_done()


class TickThread(threading.Thread):
    """
    Special thread that endlessly run tick_function and can be stopped correctly
    """

    def __init__(self, tick_function, tick_interval_sec, startup_sleep_sec=1):
        super().__init__(target=tick_function, daemon=True)
        self._tick_interval = tick_interval_sec
        self._target = tick_function
        self._stop_event = threading.Event()
        self._startup_sleep_sec = startup_sleep_sec

    def set_tick(self, new_tick_sec):
        self._tick_interval = new_tick_sec

    def stop(self):
        self._stop_event.set()

    def run(self):
        time.sleep(self._startup_sleep_sec)
        while not self._stop_event.is_set():
            start_time = time.time()
            self._target()
            # Using cycle instead of simple sleep to catch possible change of _tick_interval
            while start_time + self._tick_interval > time.time():
                time.sleep(self._tick_interval / 100)
                continue
