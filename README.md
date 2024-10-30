# Climate Models Bulk downloader library

I've created this package to manage downloading the datasets of the climate
models from the Earth System Grid.

Provided as is. It requires >=Python 3.10, but can be used for lower versions if
dependencies are satisfied, especially
[aria2p](https://github.com/pawamoy/aria2p).

## Requirements

-   Ensure that `aria2` is installed on your system, as it is used by the script
    to manage downloads.

## Installation

```
pip install git+https://github.com/aghriss/bulk-download
```

## Usage by example

The key component for using this library is the `FileInfo` class defined in
`downloader.py`

```python
from bulk_download.downloader import launch_download
from bulk_download.downloader import FileInfo
from bulk_download.downloader import DatasetInfo


URL = "https://raw.githubusercontent.com/aghriss/bulk-download/master/bulk_download/{url}"
f1 = FileInfo(name="file1.py", url="downloader.py")
f2 = FileInfo(name="file2.py", url="utils.py")
f3 = FileInfo(name="file3.py", url="__init__.py", metadata={"hidden": True})
dataset = DatasetInfo(files=[f1, f2, f3])

# it will save "files_list.json" to target_dir
launch_download(target_dir="/tmp/bulk_test", url_format=URL, dataset=dataset, port=6800)

# ls /tmp/bulk_test
## ❯ ls /tmp/bulk_test
## total 16K
##    0   120  .
##    0   860  ..
## 8.0K  6.5K  file1.py
## 4.0K  1.8K  file2.py
##    0     0  file3.py
## 4.0K   431  files_list.json
```

We can provide a `locate_files_func` to specify the sub-path of `target_dir` for
each file:

```python

URL = "https://raw.githubusercontent.com/aghriss/bulk-download/master/bulk_download/{url}"
f1 = FileInfo(name="file1.py", url="downloader.py")
f2 = FileInfo(name="file2.py", url="utils.py")
f3 = FileInfo(name="file3.py", url="__init__.py", metadata={"hidden": True})
dataset = DatasetInfo(files=[f1, f2, f3])


# let's say we want to put the files in subfolders depending on their type
def locate_file(f: FileInfo):
    if f.metadata.get("hidden", False):
        return f".sub/{f.name}"
    return f"main/{f.name}"


launch_download(
    target_dir="/tmp/bulk_test",
    url_format=URL,
    dataset=dataset,
    port=6800,
    locate_files_func=locate_file,
)

## ❯ find /tmp/bulk_test -type f -name "*.py"
## /tmp/bulk_test/main/file1.py
## /tmp/bulk_test/main/file2.py
## /tmp/bulk_test/.sub/file3.py
```

The script will add a `files_list.json` in the `target_dir` that contains the
file information for later use.

## Demo

This is a demo that uses the library to download CESM2 data.
[More details here](docs/cesm_download.md)
https://github.com/aghriss/clim_downloader/assets/32200675/ba02a545-eab1-4988-81e8-7f5d8a17b852
