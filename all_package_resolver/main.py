import os
import tempfile
from datetime import datetime
from logging import DEBUG, INFO

import typer
from pathlib2 import Path
from typing_extensions import Annotated

from all_package_resolver.downloaders.lang.lang_downloader import Lang, LangDownloader
from all_package_resolver.downloaders.os.os_downloader import OS, OsDownloader
from all_package_resolver.logger import get_logger
from all_package_resolver.parameters import no_cleanup_param, output_dir_param, package_param, verbose_param
from all_package_resolver.state import state

FILE_LOG_PREFIX = "package-resolver-logs-{date}.log"

app = typer.Typer(help="Package downloader for different OS and Programming Languages")


@app.command("os")
def os_download(os_type: Annotated[OS, "operating system"], package: package_param = None):
    downloader_class: OsDownloader

    match os_type:
        case OS.ubuntu:
            from .downloaders.os.ubuntu_downloader import UbuntuDownloader

            downloader_class = UbuntuDownloader

        case OS.centos:
            from .downloaders.os.centos_downloader import CentosDownloader

            downloader_class = CentosDownloader

        case OS.alpine:
            from .downloaders.os.alpine_downloader import AlpineDownloader

            downloader_class = AlpineDownloader

        case _:
            raise ValueError(f"Unknown OS: {os_type}")

    downloader = downloader_class(state["logger"], package, state["output_dir"])
    downloader.run(not state["no_cleanup"])


@app.command("lang")
def language_download(
    lang_type: Annotated[Lang, "programming language"],
    lang_version: str = typer.Argument(..., help="Programming language version"),
    package: package_param = None,
):
    downloader_class: LangDownloader

    match lang_type:
        case Lang.python:
            from .downloaders.lang.python_downloader import PythonDownloader

            downloader_class = PythonDownloader

        case Lang.node:
            from .downloaders.lang.node_downloader import NodeDownloader

            downloader_class = NodeDownloader

        case _:
            raise ValueError(f"Unknown language: {lang_type}")

    downloader = downloader_class(state["logger"], package, state["output_dir"], lang_version)
    downloader.run(not state["no_cleanup"])


@app.callback()
def main(
    verbose: verbose_param = False,
    output_dir: output_dir_param = os.path.join(os.path.curdir, "out"),
    no_cleanup: no_cleanup_param = False,
):
    log_path = Path(tempfile.gettempdir(), FILE_LOG_PREFIX.format(date=datetime.now().isoformat().replace(":", "_")))
    logger = get_logger(log_path)
    logger.setLevel(DEBUG if verbose else INFO)
    state["log_path"] = log_path
    state["logger"] = logger
    state["output_dir"] = output_dir
    state["no_cleanup"] = no_cleanup


if __name__ == "__main__":
    app()
