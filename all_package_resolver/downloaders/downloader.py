from abc import ABC, abstractmethod
import docker
from datetime import datetime
from tempfile import mkdtemp
from os.path import join, getsize, isfile
from os import listdir
import shutil
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from all_package_resolver.utils import format_size, format_time
from time import time


class Downloader(ABC):
    CONTAINER_PACKAGE_DIR = "/mnt/tmp"

    def __init__(self, package: str, output_dir: str):
        self.package = package
        self.output_dir = output_dir
        self.console = Console()
        self.tmp_dir = mkdtemp()

    def run(self, show_logs: bool = False):
        self.start_time = time()

        try:
            client = docker.from_env()
        except Exception as e:
            print("Error: {}".format(e))
            print("Make sure you have docker installed and running.")
            exit(1)

        self.console.print(f"Temporary directory: {self.tmp_dir}")

        self.console.print(
            f"Creating container from image: {self.get_image()}")

        command = self.get_command()
        self.console.print(f"Running command: {command}")
        self.container = client.containers.run(
            self.get_image(),
            self.get_command(),
            detach=True,
            volumes=[rf"{self.tmp_dir}:{self.CONTAINER_PACKAGE_DIR}"],
        )

        self.console.print(f"Container ID: {self.container.id}")

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

        self.__handle_status_code()
        self.container.remove()
        self.__print_downloaded_files()
        self.__pack_downloaded_files_and_print_summary()

        shutil.rmtree(self.tmp_dir)

    def __pack_downloaded_files_and_print_summary(self):
        now_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_file = join(
            self.output_dir, f"{self.get_os()}-{self.package}-{now_str}")
        output_file_with_ext = f"{output_file}.zip"

        shutil.make_archive(
            output_file,
            "zip",
            self.tmp_dir
        )

        self.end_time = time()
        panel = Panel(
            f"* Archive saved as [bold]{output_file_with_ext}[/bold]\n* Total Size: {format_size(getsize(output_file_with_ext))}\n* Total time: {format_time(self.end_time - self.start_time)}",
            title="Summary"
        )
        self.console.print(panel)

    def __handle_status_code(self):
        self.container.reload()
        status_code = self.container.attrs["State"]["ExitCode"]

        if status_code != 0:
            panel = Panel(
                f"{self.container.logs(stdout=False).decode('utf-8')}",
                title="Error logs",
                border_style="red",
                style="red"
            )
            self.console.print(panel)
            self.console.print(
                f"Error: Container exited with code {status_code}")

            self.container.remove()
            exit(1)

    def __print_downloaded_files(self):
        table = Table(title="Files downloaded")
        table.add_column("File")
        table.add_column("Size")

        list_of_files = filter(lambda x: isfile(join(self.tmp_dir, x)),
                               listdir(self.tmp_dir))
        files_with_size = [(file_name, getsize(join(self.tmp_dir, file_name)))
                           for file_name in list_of_files]
        files_with_size.sort(key=lambda x: x[1], reverse=True)
        for file, size in files_with_size:
            table.add_row(file, format_size(size))
        self.console.print(table)

    @abstractmethod
    def get_os(self):
        pass

    @abstractmethod
    def get_command(self):
        pass

    @abstractmethod
    def get_image(self):
        pass
