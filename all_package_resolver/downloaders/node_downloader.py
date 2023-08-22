from all_package_resolver.downloaders.downloader import Downloader


class NodeDownloader(Downloader):
    SETUP_ENV_COMMAND = "apk update && apk add parallel && npm install -g npm npm-offline-packager"
    COMMAND = "npo fetch --no-tar -d {download_dir} {package}"

    def __init__(self, package: str, output_dir: str, node_version: str = "18"):
        super().__init__(package, output_dir)
        self.node_version = node_version

    def get_os(self):
        return f"node-{self.node_version}-alpine"

    def get_download_command(self):
        return f"/bin/sh -c '{self.COMMAND.format(download_dir=self.CONTAINER_PACKAGE_DIR, package=self.package)}'"

    def get_setup_env_command(self) -> str:
        return f"/bin/sh -c '{self.SETUP_ENV_COMMAND}'"
    
    def get_image(self):
        return f"node:{self.node_version}-alpine"
