import hashlib
import subprocess
import time
import re


def start_aria2c(
    port: int,
    max_connections=16,
    num_splits=16,
    overwrite=True,
    file_renaming=False,
):

    aria2_command = [
        "aria2c",
        "--enable-rpc",
        f"--max-connection-per-server={max_connections}",
        f"--split={num_splits}",
        f"--allow-overwrite={str(overwrite).lower()}",
        f"--auto-file-renaming={str(file_renaming).lower()}",
        "--optimize-concurrent-downloads=true",
        "--file-allocation=none",
        "--rpc-listen-port",
        f"{port}",
    ]
    process = subprocess.Popen(aria2_command, stdout=subprocess.DEVNULL)
    time.sleep(0.5)
    if process.poll() == 1:
        raise RuntimeError(
            f"Make sure 'aria2' is installed and that port {port} is not already in use"
        )
    return process


def get_checksum(file_path, checksum_type):
    with open(file_path, "rb") as f:
        if checksum_type == "md5":
            return hashlib.md5(f.read()).hexdigest()
        elif checksum_type == "sha256":
            return hashlib.sha256(f.read()).hexdigest()
        else:
            raise ValueError(f"Unrecognized checksum type {checksum_type}")


def compare_checksum(file_path, checksum, checksum_type):
    return get_checksum(file_path, checksum_type.lower()) == checksum


def dataset_within_range(file_name: str, start_month: int, end_month: int):
    # start_p, _ = [int(s) for s in re.findall(r"\d{6}-", file_name)]
    pattern = r".*(\d{6})-(\d{6}).nc"
    m = re.match(pattern, file_name)
    if m is None:
        raise ValueError(
            f"Filename {file_name} doesn't match the expected pattern {pattern}"
        )
    start_p = int(m.group(1))
    if start_month <= start_p and start_p <= end_month:
        return True
