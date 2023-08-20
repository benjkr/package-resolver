from all_package_resolver.downloaders.downloader import Downloader


class AlpineDownloader(Downloader):
    COMMAND = "/bin/sh -c 'apk update && cd {download_dir} && apk fetch -R {package}'"

    def __init__(self, package: str, output_dir: str):
        super().__init__(package, output_dir)

    def get_os(self):
        return "alpine"

    def get_command(self):
        return self.COMMAND.format(download_dir=self.CONTAINER_PACKAGE_DIR, package=self.package)

    def get_image(self):
        return "alpine:latest"
