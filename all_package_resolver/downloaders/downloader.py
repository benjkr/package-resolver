from abc import ABC, abstractmethod
import docker
from datetime import datetime
from tempfile import mkdtemp
from os.path import join, getsize
import shutil
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress
from all_package_resolver.utils import format_size, format_time
from time import time
from pathlib2 import Path


class Downloader(ABC):
    CONTAINER_PACKAGE_DIR = "/mnt/packages"

    def __init__(self, package: str, output_dir: str):
        self.package = package
        self.output_dir = output_dir
        self.console = Console()
        self.tmp_dir = Path(mkdtemp())

        self.container = None

    def run(self, show_logs: bool = False):
        self.start_time = time()

        try:
            self.client = docker.from_env()
        except Exception as e:
            self.console.print("Error: {}".format(e))
            self.console.print("Make sure you have docker installed and running.")
            exit(1)

        try:
            # self.console.print(f"Temporary directory: {self.tmp_dir}")

            self.__setup_env_image()

            self.container = self.client.containers.run(
                self.__get_env_image_name(),
                self.get_download_command(),
                detach=True,
                volumes=[rf"{self.tmp_dir}:{self.CONTAINER_PACKAGE_DIR}"],
            )

            self.console.print(f"Running in container ID: {self.container.id}")
            self.__handle_show_logs(show_logs)

            self.__handle_status_code()
            self.__print_downloaded_files()
            self.__pack_downloaded_files_and_print_summary()
        except Exception as e:
            self.console.print_exception()
        finally:
            if self.container is not None:
                self.container.stop()
                self.container.remove()
            shutil.rmtree(self.tmp_dir)

    def __handle_show_logs(self, show_logs: bool):
        """
        Handles the logic for showing logs of the container. If `show_logs` is True, the logs of the container are streamed to
        the console. Otherwise, the logs are not shown.

        Args:
            show_logs (bool): Whether to show the logs or not.
        """
        if show_logs:
            self.console.print("---------------------------------------")
            for log in self.container.logs(stream=True, stdout=True, stderr=True):
                self.console.print(log.decode("utf-8").strip())
            self.console.print("---------------------------------------")
            self.container.wait()
        else:
            with self.console.status("Waiting for container to finish..."):
                self.container.wait()
            self.console.print("Done!")

    def __setup_env_image(self):
        """
        Sets up the base environment image for the container. If the image already exists and is not stale (older than 7 days),
        it is used. Otherwise, a new image is created by running the setup environment command in a container and committing
        the changes to a new image. If the container fails to start or exit with a non-zero exit code, an exception is raised.

        Raises:
            Exception: If the container fails to start or exit with a non-zero exit code.
        """
        try:
            env_image = self.client.images.get(self.__get_env_image_name())
        except Exception:
            env_image = None

        # Determine if the image is stale (older than 7 days). If so, remove it and
        if env_image is not None:
            now = datetime.utcnow()
            created_at = datetime.strptime(env_image.attrs["Created"][0:19], "%Y-%m-%dT%H:%M:%S")
            if (now - created_at).days < 7:
                self.console.print(f"Using cached env image: {self.__get_env_image_name()}")
                return
            else:
                self.console.print(f"Removing stale env image: {self.__get_env_image_name()}")
                env_image.remove()

        with self.console.status(f"Pulling {self.get_image()}") as status:
            self.client.images.pull(self.get_image())

            status.update(f"Creating env image with {self.get_image()}")
            setup_c = self.client.containers.run(self.get_image(), self.get_setup_env_command(), detach=True)
            setup_c.wait()

            if setup_c.attrs["State"]["ExitCode"] != 0:
                raise Exception("Could not env base image. ")

            status.update(f"Committing env image as {self.__get_env_image_name()}")
            setup_c.commit(self.__get_env_image_name())
            setup_c.remove()

    def __get_env_image_name(self):
        return f"{self.get_os()}-env"

    def __pack_downloaded_files_and_print_summary(self):
        """
        Packs the downloaded files into a zip archive and prints a summary of the operation. The archive is created in the
        specified directory with a name based on the current timestamp. If the archive creation fails, an exception is
        raised.

        Raises:
            Exception: If the archive creation fails.
        """
        now_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_file = join(self.output_dir, f"{self.get_os()}-{self.package.replace(' ', '_')}-{now_str}.zip")

        shutil.make_archive(output_file[:-4], "zip", self.tmp_dir.resolve())

        self.end_time = time()
        summary = f"* Archive saved as [bold]{output_file}[/bold]\n* Total Size: {format_size(getsize(output_file))}\n* Total time: {format_time(self.end_time - self.start_time)}"
        panel = Panel(summary, title="Summary")
        self.console.print(panel)

    def __handle_status_code(self):
        """
        Handles the status code of the container. If the status code is 0, the container is stopped and removed. Otherwise,
        the container is left running and an exception is raised.

        Raises:
            Exception: If the container is still running after executing the command or if the command fails to execute.
        """
        self.container.reload()
        status_code = self.container.attrs["State"]["ExitCode"]

        if status_code != 0:
            panel = Panel(
                f"{self.container.logs(stdout=False).decode('utf-8')}",
                title="Error logs",
                border_style="red",
                style="red",
            )
            self.console.print(panel)
            self.console.print(f"Error: Container exited with code {status_code}")

            raise Exception("Container exited with non-zero exit code")

    def __print_downloaded_files(self):
        """
        Prints the downloaded files to the console in a table. The files are sorted by size in descending order.
        """
        files_with_size = [
            (f, getsize(self.tmp_dir.joinpath(f))) for f in self.tmp_dir.iterdir() if self.tmp_dir.joinpath(f).is_file()
        ]
        files_with_size.sort(key=lambda x: x[1], reverse=True)

        table = Table(title="Files downloaded", show_header=True, header_style="bold magenta")
        table.add_column("File", style="cyan")
        table.add_column("Size", style="magenta")

        for file, size in files_with_size:
            file: Path = file
            table.add_row(file.name, format_size(size))

        self.console.print(table)

    @abstractmethod
    def get_os(self) -> str:
        pass

    def get_download_command(self):
        return f"/bin/sh -c '{self.COMMAND.format(download_dir=self.CONTAINER_PACKAGE_DIR, package=self.package)}'"

    def get_setup_env_command(self):
        return f"/bin/sh -c '{self.SETUP_ENV_COMMAND}'"

    @abstractmethod
    def get_image(self) -> str:
        pass
