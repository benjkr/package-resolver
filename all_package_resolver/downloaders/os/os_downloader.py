from ..downloader import Downloader


class OsDownloader(Downloader):
    def __init__(self, package: str, output_dir: str):
        super().__init__(package, output_dir)
