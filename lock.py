
import fcntl
import os
from contextlib import contextmanager
from pathlib import Path

LOCK_PATH = Path("data/notifier.lock")


class AlreadyRunningError(Exception):
    """Другой экземпляр проверки уже работает."""


@contextmanager
def single_instance():
    """Не допускает одновременных запусков."""
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)

    with LOCK_PATH.open("a+") as lock_file:
        try:
            fcntl.flock(
                lock_file.fileno(),
                fcntl.LOCK_EX | fcntl.LOCK_NB,
            )
        except BlockingIOError as error:
            raise AlreadyRunningError(
                "Проверка уже выполняется."
            ) from error

        try:
            lock_file.seek(0)
            lock_file.truncate()
            lock_file.write(str(os.getpid()))
            lock_file.flush()

            yield

        finally:
            fcntl.flock(
                lock_file.fileno(),
                fcntl.LOCK_UN,
            )
