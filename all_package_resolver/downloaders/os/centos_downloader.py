from all_package_resolver.downloaders.os.os_downloader import OsDownloader


class CentosDownloader(OsDownloader):
    SETUP_ENV_COMMAND = "yum update -y"
    COMMAND = "yum install -y --downloadonly --downloaddir=$PR_DOWNLOAD_DIR $PR_PACKAGE"

    def get_os(self):
        return "centos"

    def get_image(self):
        return "centos:7"
