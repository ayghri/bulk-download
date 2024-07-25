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
    """
    Starts the aria2c download manager with specified configurations.

    Parameters:
    port (int): The port on which the aria2c RPC server will listen.
    max_connections (int, optional): Maximum connections per server (default is 16).
    num_splits (int, optional): Number of splits for downloads (default is 16).
    overwrite (bool, optional): Whether to allow overwriting existing files (default is True).
    file_renaming (bool, optional): Whether to enable automatic file renaming (default is False).

    Returns:
    subprocess.Popen: The process object for the started aria2c instance.

    Raises:
    RuntimeError: If aria2c fails to start or if the specified port is in use.
    """
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


def compare_checksum(file_path, checksum, checksum_type):
    """
    Compares the checksum of a file with a provided checksum value.

    Parameters:
    file_path (str): The path to the file to be checked.
    checksum (str): The expected checksum value to compare against.
    checksum_type (str): The type of checksum algorithm to use (e.g., 'md5', 'sha256').

    Returns:
    bool: True if the computed checksum matches the provided checksum, False otherwise.

    Raises:
    ValueError: If the provided checksum_type is not recognized by hashlib.
    """
    if checksum_type not in hashlib.algorithms_available:
        raise ValueError(
            f"Unrecognized checksum type {checksum_type}. Supported: {hashlib.algorithms_available}"
        )
    with open(file_path, "rb") as f:
        digest = hashlib.file_digest(f, checksum_type)
    return digest.hexdigest().lower() == checksum.lower()


# def dataset_within_range(file_name: str, start_month: int, end_month: int):
#     pattern = r".*(\d{6})-(\d{6}).nc"
#     m = re.match(pattern, file_name)
#     if m is None:
#         raise ValueError(
#             f"Filename {file_name} doesn't match the expected pattern {pattern}"
#         )
#     start_p = int(m.group(1))
#     if start_month <= start_p and start_p <= end_month:
#         return True
#


def ncfile_subpath(file_info) -> str:
    """
    Extracts a subpath from a NetCDF filename based on its structure.

    The function expects the filename to the pattern "...[SIM]...[VAR]..[MONTH1]-[MONTH2]"
    the simulation identifier SIM and the start and end months to point to "SIM/MONTH1-MONTH2.nc"

    Parameters:
    nc_filename (str): The NetCDF filename to parse.

    Returns:
    str: A formatted subfolder path in the form 'sim/start_month-end_month.nc'.

    Raises:
    AssertionError: If the filename does not match the expected pattern or if
                    the number of captured groups is not as expected.
    """
    result = re.match(
        r".*-(\d{4}\.\d{3})\..*\.([A-Z]*)\.(\d{6})-(\d{6})\.nc", file_info.name
    )
    assert result is not None
    assert result.lastindex == 4

    sim = result.group(1)
    start_month = int(result.group(3))
    end_month = int(result.group(4))
    subfolder = f"{sim}/{start_month}-{end_month}.nc"
    return subfolder
