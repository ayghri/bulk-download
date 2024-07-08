from datetime import datetime
from pathlib import Path
from typing import Dict, List
from pydantic import BaseModel
from .utils import compare_checksum


class DownloadInfo(BaseModel):
    name: str
    url: str
    checksum: str = ""
    checksum_type: str = ""
    size: int = -1


class FileInfo(BaseModel):
    name: str
    url_path: str
    checksum: str
    checksum_type: str
    size: int
    mod_time: datetime

    def to_download(self, url_format: str) -> DownloadInfo:
        return DownloadInfo(
            name=self.name,
            url=url_format.format(
                url_path=self.url_path, name=self.name, hash=self.checksum
            ),
            checksum=self.checksum,
            checksum_type=self.checksum_type,
            size=self.size,
        )

    def already_downloaded(
        self,
        target_dir: Path,
        should_checksum=True,
    ):
        path = target_dir.joinpath(self.name)
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
    properties: Dict
    files: List[FileInfo]
