import os
import typer
from typing_extensions import Annotated
from enum import Enum
from .downloaders.downloader import Downloader

app = typer.Typer(
    help="Package downloader for different OS and Programming Languages")


class OS(str, Enum):
    ubuntu = "ubuntu"
    centos = "centos"
    alpine = "alpine"


class Lang(str, Enum):
    python = "python"
    node = "node"


state = {
    "verbose": None,
    "output_dir": None,
    "show_logs": None,
    "package": None,
}


@app.command("os")
def os_download(
    os_type: Annotated[OS, "operating system"],
    package: str = typer.Argument(..., help="Package to download"),
):
    downloader: Downloader

    match os_type:
        case OS.ubuntu:
            from .downloaders.ubuntu_downloader import UbuntuDownloader
            downloader = UbuntuDownloader(package, state["output_dir"])

        case OS.centos:
            from .downloaders.centos_downloader import CentosDownloader
            downloader = CentosDownloader(package, state["output_dir"])

        case OS.alpine:
            from .downloaders.alpine_downloader import AlpineDownloader
            downloader = AlpineDownloader(package, state["output_dir"])

        case _:
            raise ValueError(f"Unknown OS: {os_type}")

    downloader.run(show_logs=state["show_logs"])


@app.command("language")
def language_download(
    lang_type: Annotated[Lang, "programming language"],
    lang_version: str = typer.Argument(...,
                                       help="Programming language version"),
    package: str = typer.Argument(..., help="Package to download"),
):
    downloader: Downloader

    match lang_type:
        case Lang.python:
            from .downloaders.python_downloader import PythonDownloader
            downloader = PythonDownloader(
                package,
                state["output_dir"],
                lang_version,
            )

        case Lang.node:
            from .downloaders.node_downloader import NodeDownloader
            downloader = NodeDownloader(
                package,
                state["output_dir"],
                lang_version
            )

        case _:
            raise ValueError(f"Unknown language: {lang_type}")

    downloader.run(show_logs=state["show_logs"])


@ app.callback()
def main(
    # verbose: bool = False,
    output_dir: str = typer.Option(
        os.path.join(os.path.curdir, "out"),
        help="Output directory",
        show_default=True,
    ),
    show_logs: bool = typer.Option(
        False, "--show-logs", help="Show logs", show_default=True
    ),
):
    # state["verbose"] = verbose
    state["output_dir"] = output_dir
    state["show_logs"] = show_logs


if __name__ == "__main__":
    app()
