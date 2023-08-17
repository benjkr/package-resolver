import os
import typer
from typing_extensions import Annotated
from enum import Enum
from downloaders.downloader import Downloader

app = typer.Typer(help="Package downloader for different OSes")


class OS(str, Enum):
    ubuntu = "ubuntu"
    centos = "centos"
    alpine = "alpine"


@app.command()
def download(
    os: Annotated[OS, "operating system"],
    package: str = typer.Argument(..., help="Package to download"),
    output_dir: str = typer.Option(
        os.path.join(os.path.curdir, "out"),
        help="Output directory",
        show_default=True,
    ),
    show_logs: bool = typer.Option(
        False, "--show-logs", help="Show logs", show_default=True
    ),
):
    downloader: Downloader
    match os:
        case OS.ubuntu:
            from downloaders.ubuntu_downloader import UbuntuDownloader
            downloader = UbuntuDownloader(package, output_dir)

        case OS.centos:
            from downloaders.centos_downloader import CentosDownloader
            downloader = CentosDownloader(package, output_dir)

        case OS.alpine:
            from downloaders.alpine_downloader import AlpineDownloader
            downloader = AlpineDownloader(package, output_dir)
        case _:
            raise ValueError(f"Unknown OS: {os}")

    downloader.run(show_logs=show_logs)


if __name__ == "__main__":
    app()
