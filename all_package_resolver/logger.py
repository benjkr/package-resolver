from logging import DEBUG, FileHandler, Formatter, StreamHandler, getLogger

import colorlog
from pathlib2 import Path

FORMAT = "|%(asctime)s|%(levelname)-5.5s| %(message)s"
COLORED_FORMAT = f"%(log_color)s{FORMAT}"
LOG_COLORS = {
    "DEBUG": "purple",
    "INFO": "cyan",
    "WARNING": "yellow",
    "ERROR": "red",
    "CRITICAL": "red,bg_white",
}


def get_logger(log_path: Path):
    logger = getLogger(__name__)

    if not logger.hasHandlers():
        colored_formatter = colorlog.ColoredFormatter(COLORED_FORMAT, log_colors=LOG_COLORS)
        formatter = Formatter(FORMAT)

        console_h = StreamHandler()
        console_h.setFormatter(colored_formatter)

        file_h = FileHandler(log_path)
        file_h.setFormatter(formatter)
        file_h.setLevel(DEBUG)

        logger.addHandler(file_h)
        logger.addHandler(console_h)

    return logger
