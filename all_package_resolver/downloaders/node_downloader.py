from all_package_resolver.downloaders.downloader import Downloader


class NodeDownloader(Downloader):
    SETUP_ENV_COMMAND = "apk update && apk add parallel && npm install -g npm && cd /root && npm i {package} && cd {download_dir}"
    DOWNLOAD_DEPS_COMMAND = "cat /root/package-lock.json | grep -Eo \"(http|https)://[a-zA-Z0-9./?=_%:-]*.tgz\" | parallel --gnu -j 5 \"wget {}\""

    def __init__(self, package: str, output_dir: str, node_version: str = "18"):
        super().__init__(package, output_dir)
        self.node_version = node_version

    def get_os(self):
        return f"node-{self.node_version}-alpine"

    def get_command(self):
        return f"/bin/sh -c '{self.SETUP_ENV_COMMAND.format(download_dir=self.CONTAINER_PACKAGE_DIR, package=self.package)} && {self.DOWNLOAD_DEPS_COMMAND}'"

    def get_image(self):
        return f"node:{self.node_version}-alpine"
