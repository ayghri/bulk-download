import argparse
from .downloader import Downloader
from .xml_parser import extract_dataset
from pathlib import Path


ENDPOINT = "https://tds.ucar.edu/thredds/fileServer/"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--xml", type=str)
    parser.add_argument("--target", type=str)
    parser.add_argument("--token", type=str)
    parser.add_argument("--port", type=int, default=6800)
    parser.add_argument("--checksum", type=bool, default=False)
    parser.add_argument("--dry-run", type=bool, default=False)
    # xml_path = "/datasets/ssh/simulations/cesm2/TAUX_atm.xml"
    # target_dir = "/datasets/ssh/simulations/cesm2/TAUX"
    args = parser.parse_args()

    xml_path = args.xml
    target_dir = args.target
    dataset = extract_dataset(xml_path)
    api_token = args.token
    URL_FORMAT = f"{ENDPOINT}{{url_path}}?api-token={api_token}"

    Path(target_dir).mkdir(parents=True, exist_ok=True)
    with Path(target_dir).joinpath("dataset.json").open("w") as f:
        f.write(dataset.model_dump_json(indent=2))

    downloader = Downloader(
        target_dir=target_dir,
        url_format=URL_FORMAT,
        files_list=dataset.files,
        port=args.port,
        mock=args.dry_run,
        should_checksum=args.checksum,
    )

    downloader.start()
