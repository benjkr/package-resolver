import logging
from logging import DEBUG, INFO
from rich.logging import RichHandler

FORMAT = "%(message)s"
logging.basicConfig(
    level="INFO", format=FORMAT, handlers=[RichHandler(omit_repeated_times=False, show_path=False)]
)


def get_logger():
    return logging.getLogger("rich")
