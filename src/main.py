from eml import EML
from odt import ODT
from neighbourhood import NeighbourhoodData
import csv_write


def create_csv_files(
    path_to_xml,
    dest_a,
    dest_b,
    dest_c,
    path_to_odt=None,
    path_to_neighbourhood_data=None,
) -> None:
    # Parse the eml from the path and run all checks in the protocol
    eml = EML.from_xml(path_to_xml)

    # Load in neighbourhood data
    neighbourhood_data = NeighbourhoodData.from_path(path_to_neighbourhood_data)

    check_results = eml.run_protocol(neighbourhood_data=path_to_neighbourhood_data)
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

    csv_write.write_csv_a(check_results, eml_metadata, dest_a)
    csv_write.write_csv_b(check_results, eml_metadata, dest_b)
    csv_write.write_csv_c(check_results, eml_metadata, dest_c)
