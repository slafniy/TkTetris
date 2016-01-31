import time
import threading


class TickThread(threading.Thread):
    """
    Special thread that endlessly run tick_function and can be stopped correctly
    """

    def __init__(self, tick_function, tick_interval_sec, game_over_event):
        super().__init__(target=tick_function)
        self.tick_interval = tick_interval_sec
        self._stop_event = threading.Event()
        self._time_counter = 0
        self._game_over_event = game_over_event

    def stop(self):
        self._stop_event.set()

    def run(self):
        time.sleep(1)
        while not self._stop_event.is_set() and not self._game_over_event.is_set():
            start_time = time.time()
            self._target()
            self._time_counter = 0
            sleep_time = self.tick_interval - time.time() + start_time
            time.sleep(sleep_time if sleep_time >= 0 else 0)


class RepaintThread(threading.Thread):
    def __init__(self, repaint_event: threading.Event, repaint_func):
        super().__init__()
        self._repaint_func = repaint_func
        self._repaint_event = repaint_event

    def run(self):
        while True:
            if self._repaint_event.is_set():
                self._repaint_func()
                self._repaint_event.clear()
