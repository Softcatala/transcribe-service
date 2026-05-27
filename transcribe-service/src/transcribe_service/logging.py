import logging
from pathlib import Path

from transcribe_service.constants import LOGDIR, LOGLEVEL


def init_logging() -> None:
    """TODO: Docstring this."""
    logger = logging.getLogger()
    logfile = Path(LOGDIR) / "transcribe-service.log"
    hdlr = logging.handlers.RotatingFileHandler(
        logfile, maxBytes=1024 * 1024, backupCount=1
    )
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(LOGLEVEL)

    console = logging.StreamHandler()
    console.setLevel(LOGLEVEL)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    console.setFormatter(formatter)
    logger.addHandler(console)
