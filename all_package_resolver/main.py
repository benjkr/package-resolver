import os
import typer
from typing_extensions import Annotated
from enum import Enum

from all_package_resolver.downloaders.lang.lang_downloader import LangDownloader
from all_package_resolver.downloaders.os.os_downloader import OsDownloader
from .logger import get_logger, INFO, DEBUG

from all_package_resolver.parameters import output_dir_param, verbose_param, no_cleanup_param, package_param

app = typer.Typer(help="Package downloader for different OS and Programming Languages")
logger = get_logger()


class OS(str, Enum):
    ubuntu = "ubuntu"
    centos = "centos"
    alpine = "alpine"


class Lang(str, Enum):
    python = "python"
    node = "node"


state = {"verbose": None, "output_dir": None, "no_cleanup": None}


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

    downloader = downloader_class(package, state["output_dir"])
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

    downloader = downloader_class(package, state["output_dir"], lang_version)
    downloader.run(not state["no_cleanup"])


@app.callback()
def main(
    verbose: verbose_param = False,
    output_dir: output_dir_param = os.path.join(os.path.curdir, "out"),
    no_cleanup: no_cleanup_param = False,
):
    logger.setLevel(DEBUG if verbose else INFO)
    state["output_dir"] = output_dir
    state["no_cleanup"] = no_cleanup


if __name__ == "__main__":
    app()
