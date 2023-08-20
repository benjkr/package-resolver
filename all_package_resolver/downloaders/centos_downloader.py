from all_package_resolver.downloaders.downloader import Downloader


class CentosDownloader(Downloader):
    COMMAND = "/bin/bash -c 'yum update -y && yum install -y --downloadonly --downloaddir={download_dir} {package}'"

    def __init__(self, package: str, output_dir: str):
        super().__init__(package, output_dir)

    def get_os(self):
        return "centos"

    def get_command(self):
        return self.COMMAND.format(download_dir=self.CONTAINER_PACKAGE_DIR, package=self.package)

    def get_image(self):
        return "centos:7"
