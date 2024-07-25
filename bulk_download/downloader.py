import time
from typing import Callable, List
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Callable
from pydantic import BaseModel

from aria2p import API
from aria2p import Options
from aria2p import Client

from .utils import start_aria2c
from .utils import compare_checksum


class FileInfo(BaseModel):
    name: str
    url: str
    checksum: str = ""
    checksum_type: str = ""
    size: int = -1
    mod_time: datetime | None = None
    metadata: Dict = {}

    def already_downloaded(
        self,
        path: Path,
        should_checksum: bool = True,
    ) -> bool:
        """
        Checks if a file has already been downloaded.

        Parameters:
        path (Path): The file path to check for existence and download status.
        should_checksum (bool): Flag indicating whether to perform checksum verification. Defaults to True.
            If false, we check using filesize if > 0 or if *.aria2 exists (unfinished download)

        Returns:
        bool: True if the file is considered already downloaded, False otherwise.
        """
        if not path.exists():
            return False
        if path.with_suffix(".aria2").exists():
            return False
        if should_checksum and self.checksum != "":
            return compare_checksum(
                path,
                checksum=self.checksum,
                checksum_type=self.checksum_type,
            )
        if self.size > 0:
            return self.size == path.stat().st_size
        return True


class DatasetInfo(BaseModel):
    properties: Dict | None = None
    files: List[FileInfo]


class Downloader:
    """
    Attributes:
        api_token: To be retrieved from the user accounts settings
    """

    def __init__(
        self,
        target_dir: str,
        url_format: str,
        files_list: List[FileInfo],
        locate_files_func: Callable[[FileInfo], str | Path],
        port: int = 6800,
        should_checksum=True,
        dry_run=False,
        check_period=5,
    ):
        self.target_dir = Path(target_dir)
        self.url_format = url_format
        self.files_list = files_list
        self.port = port
        self.locate_files_func = locate_files_func
        self.should_checksum = should_checksum
        self.dry_run = dry_run
        self.refresh_interval = check_period

        self.target_dir.mkdir(parents=True, exist_ok=True)
        self.download_queue = []

    def filter_downloads(self):
        print("Filtering out already downloaded files", end=" ")
        if self.should_checksum:
            print("via chucksum")
        else:
            print("via size check")
        for file_info in self.files_list:
            if not file_info.already_downloaded(
                self.target_dir.joinpath(self.locate_files_func(file_info)),
                should_checksum=self.should_checksum,
            ):
                self.download_queue.append(file_info)

    def start_server(self):

        self.process = start_aria2c(port=self.port)
        print(f"Started aria2c in the background")
        print(f"Saving downloaded files to {self.target_dir}")
        self.aria2 = API(Client(host="http://localhost", port=self.port, secret=""))
        print(f"Use 'aria2p -p {self.port}' to monitor downloads")

    def start_downloads(self):
        print(f"Downloading {len(self.files_list)} urls")
        self.filter_downloads()
        print(
            f"{len(self.files_list)-len(self.download_queue)}/{len(self.files_list)} "
            f"urls already downloaded"
        )
        print(f"{len(self.download_queue)}/{len(self.files_list)} urls to download")
        if not self.dry_run:
            print(f"Starting in {self.refresh_interval} seconds:")
            self.download_all()

        self.process.terminate()
        print("Downloading Done")

    def download_one(self, file_info: FileInfo):
        """
        Submits a download request to the aria2 download manager.

        Parameters:
            file_info (FileInfo): An object containing information about the file to be downloaded,
                                  including its URL, name, checksum, and any additional metadata.
        Returns: None
        Raises:
            Exception: May raise exceptions related to the aria2 download manager if the submission fails.
        """
        options = Options(self.aria2, struct={})
        options.set("dir", self.target_dir.__str__())
        options.set("out", str(self.locate_files_func(file_info)))
        self.aria2.add(
            self.url_format.format(
                url=file_info.url,
                name=file_info.name,
                checksum=file_info.checksum,
                **file_info.metadata,
            ),
            options=options,
        )

    def download_all(self):
        for download_info in self.download_queue:
            self.download_one(download_info)
        done = False
        done_count = 0
        while not done:
            if done_count == len(self.download_queue):
                break
            downloads = self.aria2.get_downloads()
            for d in downloads:
                if d.is_complete:
                    done_count += 1
                    d.remove()
            print(f"{done_count}/{len(self.download_queue)} is done")
            time.sleep(self.refresh_interval)


def launch_download(
    target_dir,
    dataset: DatasetInfo,
    url_format,
    port,
    locate_files_func: Callable[[FileInfo], str | Path] | None = None,
    dry_run=False,
    should_checksum=False,
):
    """
    Initiates the download process for a specified dataset.

    Parameters:
    target_dir (str or Path): The directory where downloaded files will be stored.
    dataset (DatasetInfo): An object containing metadata and list of FileInfos to be downloaded.
    url_format (str): The format string for constructing download URLs.
    port (int): The port number for the aria2 download server.
    locate_files_func (Callable[[FileInfo], str | Path], optional): A function to determine the file location.
                                                        Defaults to a function that returns the file name.
    dry_run (bool, optional): If True, simulates the download without actual file transfers. Defaults to False.
    should_checksum (bool, optional): If True, enables checksum verification for downloaded files. Defaults to False.

    Returns:
    None
    """
    if locate_files_func is None:
        locate_files_func = lambda x: x.name
    Path(target_dir).mkdir(parents=True, exist_ok=True)
    with Path(target_dir).joinpath("files_list.json").open("w") as f:
        f.write(dataset.model_dump_json(indent=2))
    downloader = Downloader(
        target_dir=target_dir,
        url_format=url_format,
        files_list=dataset.files,
        locate_files_func=locate_files_func,
        port=port,
        dry_run=dry_run,
        should_checksum=should_checksum,
    )
    try:
        downloader.start_server()
        downloader.start_downloads()
    except Exception as e:
        downloader.process.terminate()
        raise e
