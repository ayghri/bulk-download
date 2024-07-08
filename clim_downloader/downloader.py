from typing import List
import subprocess
from pathlib import Path
import time
from aria2p import API
from aria2p import Options
from aria2p import Client
from tqdm import tqdm
from .utils import start_aria2c
from .files import DownloadInfo
from .files import FileInfo


class Downloader:
    """
    Attributes:
        api_token: To be retrieved from the user accounts settings
    """

    process: subprocess.Popen
    aria2: API
    options: Options

    def __init__(
        self,
        target_dir: str,
        url_format: str,
        files_list: List[FileInfo],
        port: int = 6800,
        should_checksum=True,
        mock=False,
        check_period=5,
    ):
        self.target_dir = Path(target_dir)
        self.url_format = url_format
        self.files_list = files_list
        self.port = port
        self.should_checksum = should_checksum
        self.mock = mock
        self.check_period = check_period

        self.target_dir.mkdir(parents=True, exist_ok=True)
        self.to_download = []


    def filter_downloads(self):
        print("Filtering out already downloaded files", end=" ")
        if self.should_checksum:
            print("via chucksum")
        else:
            print("via size check")
        for file in tqdm(self.files_list):
            if not file.already_downloaded(
                self.target_dir, should_checksum=self.should_checksum
            ):
                self.to_download.append(file.to_download(self.url_format))

    def start(self):

        self.process = start_aria2c(port=self.port)
        print(f"Started aria2c in the background")
        print(f"Saving downloaded files to {self.target_dir}")
        self.aria2 = API(Client(host="http://localhost", port=self.port, secret=""))
        self.options = Options(self.aria2, struct={})
        self.options.set("dir", str(self.target_dir))
        print(f"Downloading {len(self.files_list)} urls")
        self.filter_downloads()
        print(
            f"{len(self.files_list)-len(self.to_download)}/{len(self.files_list)} "
            f"urls already downloaded"
        )
        print(f"{len(self.to_download)}/{len(self.files_list)} urls to download")
        print(f"Use 'aria2p -p {self.port}' to monitor downloads")
        if not self.mock:
            print(f"Starting in {self.check_period} seconds:")
            self.download_all()

        self.process.terminate()
        print("Downloading Done")

    def submit_download(self, download_info: DownloadInfo):
        # url = self.endpoint + file_info["url"] + f"?api-token={self.api_token}"
        self.aria2.add(download_info.url, options=self.options)

    def download_all(self):
        for download_info in self.to_download:
            self.submit_download(download_info)
        done = False
        done_count = 0
        while not done:
            if done_count == len(self.to_download):
                break
            downloads = self.aria2.get_downloads()
            for d in downloads:
                if d.is_complete:
                    done_count += 1
                    d.remove()
            # done_count +=sum([d.is_complete for d in downloads])
            print(f"{done_count}/{len(self.to_download)} is done")
            time.sleep(self.check_period)


# class DatasetDownloader:
#     def __init__(
#         self,
#         list_path,
#         target_dir,
#         start_date,
#         end_date,
#         concurrent_downloads=16,
#     ):
#         self.list_path = list_path
#         self.target_dir = target_dir
#         self.start = start_date
#         self.end = end_date
#         self.download_requests: List[FileDownloadRequest] = []
#         self.current_downloads: List[FileDownloadRequest] = []
#         self.finished_requests: List[FileDownloadRequest] = []
#         self.concurrent_downloads = concurrent_downloads
#         self.create_download_requests()
#
#     def create_download_requests(self):
#         with open(self.list_path, "r") as f:
#             lines = f.readlines()
#         for line in lines:
#             fields = line.strip().split(" ")
#             for i, field in enumerate(fields):
#                 fields[i] = field.replace("'", "")
#             filename = fields[0]
#
#             start_p, end_p = [int(s) for s in re.findall(r"\d{6}", filename)]
#             if self.start > end_p or self.end < start_p:
#                 continue
#
#             self.download_requests.append(
#                 FileDownloadRequest(
#                     file_name=fields[0],
#                     url=fields[1],
#                     hash=fields[3],
#                     target_dir=self.target_dir,
#                 )
#             )
#         print(f"Created {len(self.download_requests)}/{len(lines)} download requests")
#
#     def start_downloads(self):
#         ic(f"Starting downloads for {len(self.download_requests)} files")
#         i = 1
#         for download_request in tqdm(self.download_requests):
#             ic(f"Downloading, {i}/{len(self.download_requests)}")
#             if download_request.downloaded:
#                 ic(f"Already downloaded {download_request.filename}")
#                 continue
#             while len(self.current_downloads) == self.concurrent_downloads:
#                 time.sleep(1)
#                 self.check_downloads()
#             ic(
#                 f"Starting download of {i}/{len(self.download_requests)}, {download_request.filename}"
#             )
#             download_request.download()
#             self.current_downloads.append(download_request)
#             i = i + 1
#         while len(self.current_downloads) > 0:
#             ic(f"Waiting for {len(self.current_downloads)} downloads to finish")
#             self.check_downloads()
#             time.sleep(1)
#
#     def check_downloads(self):
#         for i, download_request in enumerate(self.current_downloads):
#             ic(
#                 f"Checking download {i+1}/{len(self.current_downloads)}, {download_request.filename}"
#             )
#             if download_request.downloaded():
#                 ic(f"Downloaded {download_request.filename}")
#                 self.current_downloads.pop(i)
#                 break
#
#     def count_remaining(self):
#         return sum([1 if d.not_downloaded else 0 for d in self.download_requests])
#
#     def print_remaining(self):
#         files_list = "\n\t".join(
#             [d.filename for d in self.download_requests if d.not_downloaded]
#         )
#         ic(f"Remaining files to download:\n\t{files_list}")
#
#
