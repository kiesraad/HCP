from typing import Optional

from . import csv_write
from .eml import EML
from .neighbourhood import NeighbourhoodData


def create_csv_files(
    path_to_xml: str,
    dest_a: str,
    dest_b: str,
    dest_c: str,
    path_to_odt: Optional[str] = None,
    path_to_neighbourhood_data: Optional[str] = None,
) -> None:
    """Main entry point for running HCP on a given .eml.xml file. We can optionally specify
    the following data:
        - path_to_odt: if a path to the corresponding ODT (proces verbaal) is specified
        then HCP additionally checks if a given reporting unit has already recounted
        and thus is exempt from certain mandatory recounts.
        - path_to_neighbourhood_data: if a path to neighbourhood data is specified
        then we run some checks at a neighbourhood level in addition to the municipality
        level.

    Args:
        path_to_xml: Path to the .eml.xml file to run HCP on.
        dest_a: Path to write output file a (inexplicable differences) to.
        dest_b: Path to write output file b (warnings and remarkable results) to.
        dest_c: Path to write output file c (percentage deviation per reporting unit per affiliation) to.
        path_to_odt: Path to the ODT (proces verbaal) corresponding to the provided .eml.xml.
        path_to_neighbourhood_data: Path to either .csv or .parquet file containing neighbourhood data.
    """
    # Parse the eml from the path
    eml = EML.from_xml(path_to_xml)

    # Load in neighbourhood data
    neighbourhood_data = NeighbourhoodData.from_path(path_to_neighbourhood_data)

    # Run protocol
    check_results = eml.run_protocol(neighbourhood_data=neighbourhood_data)
    eml_metadata = eml.metadata

    csv_write.write_csv_a(check_results, eml_metadata, dest_a)
    csv_write.write_csv_b(
        check_results, eml_metadata, neighbourhood_data is not None, dest_b
    )
    csv_write.write_csv_c(check_results, eml_metadata, dest_c)
