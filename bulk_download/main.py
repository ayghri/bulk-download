import argparse
from pathlib import Path
from .xml_parser import extract_dataset
from .utils import ncfile_subpath
from .downloader import launch_download


ENDPOINT = "https://tds.ucar.edu/thredds/fileServer/"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--xml", type=str)
    parser.add_argument("--target", type=str)
    parser.add_argument("--token", type=str)
    parser.add_argument("--port", type=int, default=6800)
    parser.add_argument("--checksum", type=bool, default=False)
    parser.add_argument("--dry-run", type=bool, default=False)
    args = parser.parse_args()

    xml_path = args.xml
    target_dir = args.target
    api_token = args.token

    URL_FORMAT = f"{ENDPOINT}{{url}}?api-token={api_token}"
    dataset = extract_dataset(xml_path)

    Path(target_dir).mkdir(parents=True, exist_ok=True)
    with Path(target_dir).joinpath("dataset.json").open("w") as f:
        f.write(dataset.model_dump_json(indent=2))

    launch_download(
        target_dir=target_dir,
        dataset=dataset,
        url_format=URL_FORMAT,
        locate_files_func=ncfile_subpath,
        port=args.port,
        dry_run=args.dry_run,
        should_checksum=args.checksum,
    )
