import re
import shutil
from abc import ABC, abstractmethod
from datetime import datetime
from logging import Logger
from os.path import getsize, join
from tempfile import mkdtemp
from time import time
from typing import List, Tuple

import docker
from pathlib2 import Path

from all_package_resolver.state import state
from all_package_resolver.utils import format_size, format_time


class Downloader(ABC):
    """
    This class is abstractive. Do not use it without inheritance. The child class MUST consist SETUP_ENV_COMMAND and COMMAND class properties.
    """

    CONTAINER_PACKAGE_DIR = "/mnt/packages"

    def __init__(self, logger: Logger, package: str, output_dir: str):
        self.logger = logger
        self.package = package
        self.output_dir = output_dir
        self.tmp_dir = Path(mkdtemp())

        self.container = None

    def run(self, cleanup: bool = True):
        self.start_time = time()

        try:
            self.client = docker.from_env()
        except Exception as e:
            self.logger.error(f"Make sure you have docker installed and running. {e}")
            exit(1)

        try:
            self.logger.debug(f"Temporary directory: {self.tmp_dir}")

            self.__setup_env_image()

            self.container = self.client.containers.run(
                self.__env_image_name,
                self.get_download_command(),
                detach=True,
                volumes=[rf"{self.tmp_dir}:{self.CONTAINER_PACKAGE_DIR}"],
                environment={"PR_PACKAGE": self.package, "PR_DOWNLOAD_DIR": self.CONTAINER_PACKAGE_DIR},
            )

            self.logger.info(f"Running in container ID: {self.container.id}")
            self.__handle_show_logs()

            self.__handle_status_code()
            self.__print_downloaded_files()
            self.__pack_downloaded_files_and_print_summary()
        except Exception as e:
            self.logger.error(e)
        finally:
            if cleanup:
                self.__cleanup()
            else:
                self.logger.info("Skipping cleanup.")
            self.logger.info(f"All logs are saved in '{state['log_path']}'")

    def __cleanup(self):
        self.logger.debug("Starting cleanup...")

        if self.container is not None:
            self.logger.debug("Stopping container")
            self.container.stop()

            self.logger.debug("Removing container")
            self.container.remove()

        self.logger.debug("Removing temp folder")
        shutil.rmtree(self.tmp_dir)

        self.logger.debug("Finished cleanup.")

    def __handle_show_logs(self):
        """
        Print container logs in debug.
        """
        self.logger.info("Waiting for container to finish...")

        self.logger.debug("Streaming container logs...")
        for log in self.container.logs(stream=True):
            log_str = log.decode("utf-8").strip()
            self.logger.debug(log_str)
        self.logger.debug("End of container logs.")
        self.container.wait()

    def __setup_env_image(self):
        """
        Sets up the base environment image for the container. If the image already exists and is not stale (older than 7 days),
        it is used. Otherwise, a new image is created by running the setup environment command in a container and committing
        the changes to a new image. If the container fails to start or exit with a non-zero exit code, an exception is raised.

        Raises:
            Exception: If the container fails to start or exit with a non-zero exit code.
        """
        try:
            env_image = self.client.images.get(self.__env_image_name)
        except Exception:
            env_image = None

        # Determine if the image is stale (older than 7 days). If so, remove it and
        if env_image is not None:
            now = datetime.utcnow()
            created_at = datetime.strptime(env_image.attrs["Created"][0:19], "%Y-%m-%dT%H:%M:%S")
            if (now - created_at).days < 7:
                self.logger.info(f"Using cached env image: {self.__env_image_name}")
                return
            else:
                self.logger.info(f"Removing stale env image: {self.__env_image_name}")
                env_image.remove()

        self.client.images.pull(self.get_image())

        self.logger.info(f"Creating env image with {self.get_image()}")
        setup_c = self.client.containers.run(self.get_image(), self.get_setup_env_command(), detach=True)
        setup_c.wait()

        if setup_c.attrs["State"]["ExitCode"] != 0:
            raise Exception("Could not create env base image.")

        self.logger.info(f"Committing env image as {self.__env_image_name}")
        setup_c.commit(self.__env_image_name)
        setup_c.remove()

    @property
    def __env_image_name(self):
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
        merged_packages = re.sub(r"[\s\/]", "-", self.package)
        output_file = join(self.output_dir, f"{self.get_os()}-{merged_packages}-{now_str}.zip")

        shutil.make_archive(output_file[:-4], "zip", self.tmp_dir.resolve())

        self.end_time = time()
        self.logger.info(f"Archive saved as '{output_file}'")
        self.logger.info(f"Total Size: {format_size(getsize(output_file))}")
        self.logger.info(f"Total time: {format_time(self.end_time - self.start_time)}")

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
            err_logs = self.container.logs(stdout=False).decode("utf-8")
            self.logger.error(f"Container exited with code {status_code}")
            self.logger.error(err_logs)

            raise Exception("Container exited with non-zero exit code")
        self.logger.info(f"Container finished running.")

    def __print_downloaded_files(self):
        """
        Prints the downloaded files to the console in a table. The files are sorted by size in descending order.
        """
        files_with_size: List[Tuple[Path, int]] = [
            (f, getsize(self.tmp_dir.joinpath(f))) for f in self.tmp_dir.iterdir() if self.tmp_dir.joinpath(f).is_file()
        ]
        files_with_size.sort(key=lambda x: x[1], reverse=True)
        max_file_name = max(map(lambda f: len(f[0].name), files_with_size))

        for file, size in files_with_size:
            self.logger.debug(f"{file.name.ljust(max_file_name, ' ')} {format_size(size)}")

    @abstractmethod
    def get_os(self) -> str:
        pass

    def get_download_command(self):
        return f"/bin/sh -c '{self.COMMAND}'"

    def get_setup_env_command(self):
        return f"/bin/sh -c '{self.SETUP_ENV_COMMAND}'"

    @abstractmethod
    def get_image(self) -> str:
        pass
