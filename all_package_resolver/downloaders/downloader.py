from abc import ABC, abstractmethod
from typing import List, Tuple
import docker
from datetime import datetime
from tempfile import mkdtemp
from os.path import join, getsize
import shutil
import re

from all_package_resolver.logger import get_logger
from all_package_resolver.utils import format_size, format_time
from time import time
from pathlib2 import Path

logger = get_logger()


class Downloader(ABC):
    """
    This class is abstractive. Do not use it without inheritance. The child class MUST consist SETUP_ENV_COMMAND and COMMAND class properties.
    """

    CONTAINER_PACKAGE_DIR = "/mnt/packages"

    def __init__(self, package: str, output_dir: str):
        self.package = package
        self.output_dir = output_dir
        self.tmp_dir = Path(mkdtemp())

        self.container = None

    def run(self, cleanup: bool = True):
        self.start_time = time()

        try:
            self.client = docker.from_env()
        except Exception as e:
            logger.error(f"Make sure you have docker installed and running. {e}")
            exit(1)

        try:
            logger.debug(f"Temporary directory: {self.tmp_dir}")

            self.__setup_env_image()

            self.container = self.client.containers.run(
                self.__env_image_name,
                self.get_download_command(),
                detach=True,
                volumes=[rf"{self.tmp_dir}:{self.CONTAINER_PACKAGE_DIR}"],
                environment={"PR_PACKAGE": self.package, "PR_DOWNLOAD_DIR": self.CONTAINER_PACKAGE_DIR},
            )

            logger.info(f"Running in container ID: {self.container.id}")
            self.__handle_show_logs()

            self.__handle_status_code()
            self.__print_downloaded_files()
            self.__pack_downloaded_files_and_print_summary()
        except Exception as e:
            logger.error(e)
        finally:
            if cleanup:
                self.__cleanup()
            else:
                logger.info("Skipping cleanup.")

    def __cleanup(self):
        logger.debug("Starting cleanup...")

        if self.container is not None:
            logger.debug("Stopping container")
            self.container.stop()

            logger.debug("Removing container")
            self.container.remove()

        logger.debug("Removing temp folder")
        shutil.rmtree(self.tmp_dir)

        logger.debug("Finished cleanup.")

    def __handle_show_logs(self):
        """
        Print container logs in debug.
        """
        logger.info("Waiting for container to finish...")

        logger.debug("Streaming container logs...")
        for log in self.container.logs(stream=True):
            log_str = log.decode("utf-8").strip()
            logger.debug(log_str)
        logger.debug("End of container logs.")
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
                logger.info(f"Using cached env image: {self.__env_image_name}")
                return
            else:
                logger.info(f"Removing stale env image: {self.__env_image_name}")
                env_image.remove()

        self.client.images.pull(self.get_image())

        logger.info(f"Creating env image with {self.get_image()}")
        setup_c = self.client.containers.run(self.get_image(), self.get_setup_env_command(), detach=True)
        setup_c.wait()

        if setup_c.attrs["State"]["ExitCode"] != 0:
            raise Exception("Could not env base image. ")

        logger.info(f"Committing env image as {self.__env_image_name}")
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
        summary = f"* Archive saved as {output_file}\n* Total Size: {format_size(getsize(output_file))}\n* Total time: {format_time(self.end_time - self.start_time)}"
        logger.info(summary)

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
            logger.error(f"Container exited with code {status_code}")
            logger.error(err_logs)

            raise Exception("Container exited with non-zero exit code")
        logger.info(f"Container finished running.")

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
            logger.debug(f"{file.name.ljust(max_file_name, ' ')} {format_size(size)}")

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
