import time
import threading


class TickThread(threading.Thread):
    """
    Special thread that endlessly run tick_function and can be stopped correctly
    """

    def __init__(self, tick_function, tick_interval_sec, game_over_event):
        super().__init__(target=tick_function, daemon=True)
        self.tick_interval = tick_interval_sec
        self._target = tick_function
        self._stop_event = threading.Event()
        self._game_over_event = game_over_event

    def stop(self):
        self._stop_event.set()

    def run(self):
        time.sleep(1)
        while not self._stop_event.is_set() and not self._game_over_event.is_set():
            start_time = time.time()
            self._target()
            sleep_time = self.tick_interval - time.time() + start_time
            time.sleep(sleep_time if sleep_time >= 0 else 0)
