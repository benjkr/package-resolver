from all_package_resolver.downloaders.downloader import Downloader


class PythonDownloader(Downloader):
    SETUP_ENV_COMMAND = "apk update && apk upgrade && python -m pip install --upgrade pip"
    COMMAND = "cd {download_dir} && python -m pip download {package} -d ."

    def __init__(self, package: str, output_dir: str, python_version: str = "3.9"):
        super().__init__(package, output_dir)
        self.python_version = python_version

    def get_os(self):
        return f"python-{self.python_version}-alpine"

    def get_image(self):
        return f"python:{self.python_version}-alpine"
