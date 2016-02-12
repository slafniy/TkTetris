import time
import threading


class TickThread(threading.Thread):
    """
    Special thread that endlessly run tick_function and can be stopped correctly
    """

    def __init__(self, tick_function, tick_interval_sec):
        super().__init__(target=tick_function)
        self.tick_interval = tick_interval_sec
        self._stop_event = threading.Event()
        self._die_event = threading.Event()
        self._stop_event.set()
        self._time_counter = 0

    def stop_ticking(self):
        self._stop_event.set()

    def start_ticking(self):
        self._stop_event.clear()

    def run(self):
        time.sleep(1)
        while not self._die_event.is_set():
            if not self._stop_event.is_set():
                start_time = time.time()
                self._target()
                self._time_counter = 0
                sleep_time = self.tick_interval - time.time() + start_time
                time.sleep(sleep_time if sleep_time >= 0 else 0)

    def die(self):
        self._die_event.set()
