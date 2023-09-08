from enum import Enum
from logging import Logger

from all_package_resolver.downloaders.downloader import Downloader


class OS(str, Enum):
    ubuntu = "ubuntu"
    centos = "centos"
    alpine = "alpine"


class OsDownloader(Downloader):
    def __init__(self, logger: Logger, package: str, output_dir: str):
        super().__init__(logger, package, output_dir)
