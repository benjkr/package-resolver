from all_package_resolver.downloaders.os.os_downloader import OsDownloader


class AlpineDownloader(OsDownloader):
    SETUP_ENV_COMMAND = "apk update"
    COMMAND = "cd {download_dir} && apk fetch -R {package}"

    def get_os(self):
        return "alpine"

    def get_image(self):
        return "alpine:latest"
