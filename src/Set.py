import logging
import threading
import time


log = logging.getLogger(__name__)


class Interval:
    """A class that loops every interval."""

    def __init__(self, interval, action, id=None) -> None:
        """Initialize the interval loop.
        Args:
            interval (float): The interval in seconds.
            action (function): The action to do.
        """
        self.interval = interval
        self.action = action

        self.id = id

        self.stop = threading.Event()

        thread = threading.Thread(target=self._setInterval)
        thread.start()

    def _setInterval(self) -> None:
        """Does things."""
        next = time.time() + self.interval
        while not self.stop.wait(next - time.time()):
            next += self.interval
            try:
                self.action(self.id)
            except OSError as e:
                log.exception(e)
                pass

    def cancel(self) -> None:
        """Cancels the interval."""
        self.stop.set()
