from all_package_resolver.downloaders.lang.lang_downloader import LangDownloader


class NodeDownloader(LangDownloader):
    SETUP_ENV_COMMAND = "apk update && apk add parallel && npm install -g npm npm-offline-packager"
    COMMAND = "npo fetch --no-tar -d {download_dir} {package}"

    def get_os(self):
        return f"node-{self.version}-alpine"

    def get_image(self):
        return f"node:{self.version}-alpine"
