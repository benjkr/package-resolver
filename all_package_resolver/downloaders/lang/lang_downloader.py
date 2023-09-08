from enum import Enum
from logging import Logger

from all_package_resolver.downloaders.downloader import Downloader


class Lang(str, Enum):
    python = "python"
    node = "node"


class LangDownloader(Downloader):
    def __init__(self, logger: Logger, package: str, output_dir: str, version: str):
        super().__init__(logger, package, output_dir)
        self.version = version
