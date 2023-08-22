from all_package_resolver.downloaders.downloader import Downloader


class AlpineDownloader(Downloader):
    SETUP_ENV_COMMAND = "apk update"
    COMMAND = "cd {download_dir} && apk fetch -R {package}"

    def __init__(self, package: str, output_dir: str):
        super().__init__(package, output_dir)

    def get_os(self):
        return "alpine"

    def get_download_command(self):
        return f"/bin/sh -c '{self.COMMAND.format(download_dir=self.CONTAINER_PACKAGE_DIR, package=self.package)}'"

    def get_setup_env_command(self) -> str:
        return f"/bin/sh -c '{self.SETUP_ENV_COMMAND}'"

    def get_image(self):
        return "alpine:latest"
