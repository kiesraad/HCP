from eml import EML
from odt import ODT
import csv_write


def create_csv_files(path_to_xml, dest_a, dest_b, dest_c, path_to_odt=None):
    # Parse the eml from the path and run all checks in the protocol
    eml = EML.from_xml(path_to_xml)

    check_results = eml.run_protocol()
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
                check_results[full_id]["already_recounted"] = True

    csv_write.write_csv_a(check_results, eml_metadata, dest_a)
    csv_write.write_csv_b(check_results, eml_metadata, dest_b)
    csv_write.write_csv_c(check_results, eml_metadata, dest_c)


def _create_csv_file_a_b_c(self):
    """
    Create three csv files based on an uploaded .xml
    This method produces three csv files; type 'a' type 'b' and type 'c'
    Note: This method is the main entry point to code provided by the client
    """
    if self.organizational_element.oe_type != "gemeente":
        return

    try:
        xml_file = self._get_path_xml_file()

        # NOTE @Orin, hier zou ik dus ook graag een pad naar de .odt die in de
        # **buitenste** laag van de te uploaden zip zit hebben.
        # Dit is ofwel Model_Na31-1.odt of Model_Na31-2.odt
        # Als deze niet gevonden is (is er niet in alle gevallen) zou ik hier
        # het liefst een `None` terugkrijgen zodat ik die logica in onze code
        # mee kan nemen.
        # Dus bijvoorbeeld:
        ## odt_file = self._get_path_odt_file()
        #
        odt_file = None

        create_csv_files(
            path_to_xml=xml_file,
            dest_a=self._filename_csv("a"),
            dest_b=self._filename_csv("b"),
            dest_c=self._filename_csv("c"),
            path_to_odt=odt_file,
        )

    except Exception:
        Log(
            level="DEBUG",
            originating_app=__name__,
            ip="",
            user=self.owner.user,
            request_type="POST",
            executed_method="",
            message=f"csv types a, b and c could not be created for {xml_file}",
        ).save()
