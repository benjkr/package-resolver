from all_package_resolver.downloaders.downloader import Downloader


class AlpineDownloader(Downloader):
    SETUP_ENV_COMMAND = "apk update"
    COMMAND = "cd {download_dir} && apk fetch -R {package}"

    def __init__(self, package: str, output_dir: str):
        super().__init__(package, output_dir)

    def get_os(self):
        return "alpine"

    def get_image(self):
        return "alpine:latest"
