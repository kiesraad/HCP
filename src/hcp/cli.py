import argparse
from os import remove, rmdir
from pathlib import Path
from zipfile import ZipFile

from .main import create_csv_files

CURRENT_NEIGHBOURHOOD_FILE = "zip_to_neighbourhood_2024.parquet"

p = argparse.ArgumentParser()
p.add_argument("data_source", help="The election result to run HCP on.")
p.add_argument("--neighbourhoods", required=False)


def start():
    args = p.parse_args()
    extract_path = Path() / "tmp"

    neighbourhood_file = (
        Path(args.neighbourhoods) if args.neighbourhoods is not None else None
    )

    # Neighbourhood file not specified as argument
    if not neighbourhood_file:
        # Find the packaged neighbourhood file
        neighbourhood_file = (
            Path(__file__).parent.parent / "data" / CURRENT_NEIGHBOURHOOD_FILE
        )

        # If we did not find the neighbourhood file, we might be in editable mode
        # for example when running `uv run hcp`. Then we use the data folder in the source
        # here.
        if not neighbourhood_file.exists():
            neighbourhood_file = (
                Path(__file__).parent.parent.parent
                / "data"
                / CURRENT_NEIGHBOURHOOD_FILE
            )

    # Path to the neighbourhood file should exist
    if not neighbourhood_file.exists():
        raise RuntimeError("Could not find specified or bundled neighbourhood file!")

    with ZipFile(args.data_source, "r") as outer_zipfile:
        # Find and extract the .eml.xml and .odt file
        odt_zipinfo = next(
            f for f in outer_zipfile.filelist if f.filename.endswith(".odt")
        )
        inner_zipinfo = next(
            f for f in outer_zipfile.filelist if f.filename.endswith(".zip")
        )
        with ZipFile(outer_zipfile.open(inner_zipinfo), "r") as inner_zipfile:
            eml_zipinfo = next(
                f for f in inner_zipfile.filelist if f.filename.endswith(".eml.xml")
            )
            inner_zipfile.extract(eml_zipinfo, extract_path)
        outer_zipfile.extract(odt_zipinfo, extract_path)

        # Run HCP
        create_csv_files(
            path_to_xml=str(extract_path / eml_zipinfo.filename),
            path_to_odt=str(extract_path / odt_zipinfo.filename),
            path_to_neighbourhood_data=str(neighbourhood_file),
            dest_a="a.csv",
            dest_b="b.csv",
            dest_c="c.csv",
        )

        # Clean up after ourselves
        remove(extract_path / eml_zipinfo.filename)
        remove(extract_path / odt_zipinfo.filename)
        try:
            rmdir(extract_path)
        except OSError as error:
            print(error)
            print(f"Not deleting {extract_path}, could not clean up")
