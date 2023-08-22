from all_package_resolver.downloaders.downloader import Downloader


class UbuntuDownloader(Downloader):
    SETUP_ENV_COMMAND = "apt-get update"
    COMMAND = "apt-get update && apt-get install -y --download-only {package} && cp /var/cache/apt/archives/*.deb {download_dir}"

    def __init__(self, package: str, output_dir: str):
        super().__init__(package, output_dir)

    def get_os(self):
        return "ubuntu"

    def get_download_command(self):
        return f"/bin/bash -c '{self.COMMAND.format(download_dir=self.CONTAINER_PACKAGE_DIR, package=self.package)}'"

    def get_setup_env_command(self):
        return f"/bin/bash -c '{self.SETUP_ENV_COMMAND}'"

    def get_image(self):
        return "ubuntu:latest"
