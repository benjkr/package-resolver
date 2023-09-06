from all_package_resolver.downloaders.lang.lang_downloader import LangDownloader


class PythonDownloader(LangDownloader):
    SETUP_ENV_COMMAND = "apk update && apk upgrade && python -m pip install --upgrade pip"
    COMMAND = "cd $PR_DOWNLOAD_DIR && python -m pip download $PR_PACKAGE -d ."

    def get_os(self):
        return f"python-{self.version}-alpine"

    def get_image(self):
        return f"python:{self.version}-alpine"
