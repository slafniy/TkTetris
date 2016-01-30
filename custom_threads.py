import time
import threading


class NeedRepaintEvent(threading.Event):
    def __init__(self):
        super().__init__()
        self.points = []


class TickThread(threading.Thread):
    """
    Special thread that endlessly run tick_function and can be stopped correctly
    """
    def __init__(self, tick_function, tick_interval_sec=1):
        super().__init__(target=tick_function)
        self.tick_interval = tick_interval_sec
        self._stop_event = threading.Event()
        self._time_counter = 0

    def stop(self):
        self._stop_event.set()

    def run(self):
        while not self._stop_event.is_set():
            start_time = time.time()
            self._target()
            self._time_counter = 0
            sleep_time = self.tick_interval - time.time() + start_time
            time.sleep(sleep_time)


class RepaintThread(threading.Thread):
    def __init__(self, repaint_event: NeedRepaintEvent, repaint_func):
        super().__init__(target=repaint_func)
        self._repaint_event = repaint_event

    def run(self):
        while True:
            if self._repaint_event.is_set():
                self._target(self._repaint_event.points)
                self._repaint_event.clear()
