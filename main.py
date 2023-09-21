from eml import EML
import csv_write


def create_csv_file_a_b_c(path_to_xml, dest_a, dest_b, dest_c, path_to_odt=None):
    eml = EML.from_xml(path_to_xml)

    check_results = eml.run_protocol()
    eml_metadata = eml.metadata

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
        ## odt_file = self.__get_path_odt_file()
        #
        odt_file = None

        create_csv_file_a_b_c(
            xml_file,
            self._filename_csv("a"),
            self._filename_csv("b"),
            self._filename_csv("c"),
            odt_file,
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


if __name__ == "__main__":
    create_csv_file_a_b_c(
        "./eml/Telling_TK2021_gemeente_Eemsdelta.eml.xml", "a.csv", "b.csv", "c.csv"
    )
