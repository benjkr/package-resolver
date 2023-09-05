from all_package_resolver.downloaders.os.os_downloader import OsDownloader


class UbuntuDownloader(OsDownloader):
    SETUP_ENV_COMMAND = "apt-get update"
    COMMAND = "apt-get update && apt-get install -y --download-only {package} && cp /var/cache/apt/archives/*.deb {download_dir}"

    def get_os(self):
        return "ubuntu"

    def get_image(self):
        return "ubuntu:latest"
