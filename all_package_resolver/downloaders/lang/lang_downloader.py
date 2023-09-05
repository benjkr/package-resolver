from ..downloader import Downloader


class LangDownloader(Downloader):
    def __init__(self, package: str, output_dir: str, version: str):
        super().__init__(package, output_dir)
        self.version = version
