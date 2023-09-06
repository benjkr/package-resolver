from all_package_resolver.downloaders.os.os_downloader import OsDownloader


class AlpineDownloader(OsDownloader):
    SETUP_ENV_COMMAND = "apk update"
    COMMAND = "cd $PR_DOWNLOAD_DIR && apk fetch -R $PR_PACKAGE"

    def get_os(self):
        return "alpine"

    def get_image(self):
        return "alpine:latest"
