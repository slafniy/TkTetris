"""Custom thread for endless background task"""
import time
import threading


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
        """
        Adjust target function call frequency
        :param new_tick_sec: - interval between task function calls
        """
        self._tick_interval = new_tick_sec

    def stop(self):
        """Conveniently stops thread after next tick"""
        self._stop_event.set()

    def run(self):
        time.sleep(self._startup_sleep_sec)
        while not self._stop_event.is_set():
            start_time = time.time()
            self._target()
            # Using cycle instead of simple sleep to catch possible change of _tick_interval
            while start_time + self._tick_interval > time.time():
                time.sleep(self._tick_interval / 100)
