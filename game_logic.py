import threading
import time

import field


class Game:
    """
    Game logic
    """
    def __init__(self, game_field: field.Field):
        self._field = game_field


class TickThread(threading.Thread):
    """
    Special thread that endlessly run tick_function and can be stopped correctly
    """
    def __init__(self, tick_function, tick_interval_sec=1):
        super().__init__(target=tick_function)
        self._stop_event = threading.Event()
        self.tick_interval = tick_interval_sec
        self._control_tick_interval = 0.05
        self._time_counter = 0
        self._lock = threading.Lock()

    def stop(self):
        self._stop_event.set()

    def run(self):
        while not self._stop_event.is_set():
            print("Stop event set:", self._stop_event.is_set())
            # assert self._control_tick_interval < self.tick_interval, "Tick interval is too small"
            if self._time_counter >= self.tick_interval:
                with self._lock:
                    self._target()
                self._time_counter = 0
            self._time_counter += self._control_tick_interval
            time.sleep(self._control_tick_interval)