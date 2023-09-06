from all_package_resolver.downloaders.lang.lang_downloader import LangDownloader


class NodeDownloader(LangDownloader):
    SETUP_ENV_COMMAND = "apk update && apk add parallel wget && npm install -g npm"
    COMMAND = 'cd /root && npm i $PR_PACKAGE && cd $PR_DOWNLOAD_DIR && cat /root/package-lock.json | grep -Eo "(http|https)://[a-zA-Z0-9./?=_%:-]*.tgz" | parallel --gnu -j 5 "wget -nv {}"'

    def get_os(self):
        return f"node-{self.version}-alpine"

    def get_image(self):
        return f"node:{self.version}-alpine"
