from typing import Optional

from . import csv_write
from .eml import EML
from .neighbourhood import NeighbourhoodData
from .odt import ODT


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

    # If odt_path is specified we try to read the file and extract the relevant
    # parts, as a precaution we will not fail if anything goes wrong here, but
    # simply return 'None' for the odt object and then the empty list for the
    # already recounted variable
    odt = ODT.from_path(path_to_odt)
    if odt:
        recounted_polling_stations = odt.get_already_recounted_polling_stations()
        for polling_station in recounted_polling_stations:
            # Reconstruct the full polling station identifier
            full_id = f"{eml_metadata.authority_id}::SB{polling_station.id}"

            # Make sure that the name of the polling station matches so that
            # we are absolutely sure that the polling station in the eml
            # matches with the one in the odt.
            polling_station_name_eml = eml_metadata.reporting_unit_names.get(full_id)
            polling_station_name_odt = (
                f"Stembureau {polling_station.name} {polling_station.zip}"
                if polling_station.zip
                else f"Stembureau {polling_station.name}"
            )

            if (
                full_id in check_results.keys()
                and polling_station_name_eml == polling_station_name_odt
            ):
                check_results[full_id].already_recounted = True

    csv_write.write_csv_a(check_results, eml_metadata, odt is not None, dest_a)
    csv_write.write_csv_b(
        check_results, eml_metadata, neighbourhood_data is not None, dest_b
    )
    csv_write.write_csv_c(check_results, eml_metadata, dest_c)
