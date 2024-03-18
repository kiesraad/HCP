from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional
from xml.etree.ElementTree import Element as XmlElement
from zipfile import ZipFile

import xml_parser

NAMESPACE = {
    "office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
    "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
    "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
}


class ODT_TYPE(Enum):
    """Enumeration of the different types of PV (Proces verbaal)"""

    na31_1 = auto()
    na31_2 = auto()


@dataclass(frozen=True)
class PollingStation:
    """Polling station identifier used for comparing different polling stations"""

    id: int
    name: str
    zip: Optional[str]


@dataclass
class ODT:
    """Container for an ODT file (proces verbaal) which specifies the type of PV
    and the XML `ElementTree` of the contents of the ODT file.
    """

    type: ODT_TYPE
    odt_xml: XmlElement

    @staticmethod
    def from_path(odt_path: Optional[str]) -> Optional["ODT"]:
        """Constrcuts an `ODT` instance from a given file path.

        Returns:
            ODT class instance with all needed fields set for running methods.
        """
        if not odt_path:
            return None

        try:
            if "Model_Na31-1.odt" in odt_path:
                return ODT(
                    type=ODT_TYPE.na31_1, odt_xml=_extract_odt_xml_root(odt_path)
                )
            elif "Model_Na31-2.odt" in odt_path:
                return ODT(
                    type=ODT_TYPE.na31_2, odt_xml=_extract_odt_xml_root(odt_path)
                )
        except Exception:
            return None

    def get_already_recounted_polling_stations(self) -> List[PollingStation]:
        """Get a list of polling stations which according to the ODT (PV)
        have already recounted.

        Returns:
            List of polling stations, list is empty if either no polling stations recounted
                or some exception occurred when parsing the XML DOM-tree
        """
        try:
            if self.type == ODT_TYPE.na31_1:
                return _get_polling_stations_with_recounts_na31_1(self.odt_xml)
            elif self.type == ODT_TYPE.na31_2:
                return _get_polling_stations_with_recounts_na31_2(self.odt_xml)
            else:
                raise RuntimeError("Unreachable code path")
        except Exception:
            return []


def _extract_odt_xml_root(odt_file):
    with ZipFile(odt_file) as odt_zip:
        with odt_zip.open("content.xml") as odt_xml:
            return xml_parser.parse_xml(odt_xml)


def _table_rows_to_polling_stations(
    table_rows: List[XmlElement],
) -> List[PollingStation]:
    polling_stations = set()

    for table_row in table_rows:
        # Get three different span elements which describe the polling station
        # the first contains the id, the second the name and the third optionally
        # the zip code
        polling_station_descriptors = table_row.findall(
            ".//text:span[@text:description]", NAMESPACE
        )

        polling_station_id = xml_parser._get_text(polling_station_descriptors[0])
        polling_station_name = xml_parser._get_text(polling_station_descriptors[1])
        polling_station_zip = xml_parser._get_text(polling_station_descriptors[2])

        # Polling station id and name is *required* to be sure that a polling station
        # can be matched. Thus if these are not present we skip this polling station.
        if polling_station_id is None or polling_station_name is None:
            continue

        polling_stations.add(
            PollingStation(
                id=int(polling_station_id),
                name=polling_station_name,
                zip=polling_station_zip,
            )
        )

    return list(polling_stations)


def _get_polling_stations_with_recounts_na31_1(
    odt_root: XmlElement,
) -> List[PollingStation]:
    polling_stations_3b_a = odt_root.findall(
        "./office:body/office:text/table:table[@table:name='NieuweTelling']/table:table-row",
        NAMESPACE,
    )
    polling_stations_3b_b = odt_root.findall(
        "./office:body/office:text/table:table[@table:name='CorrigendumGeenVerklaring']/table:table-row",
        NAMESPACE,
    )
    polling_stations_3c = odt_root.findall(
        "./office:body/office:text/table:table[@table:name='Tabelle3']/table:table-row",
        NAMESPACE,
    )

    return _table_rows_to_polling_stations(
        polling_stations_3b_a + polling_stations_3b_b + polling_stations_3c
    )


def _get_polling_stations_with_recounts_na31_2(
    odt_root: XmlElement,
) -> List[PollingStation]:
    polling_stations = odt_root.findall(
        "./office:body/office:text/table:table[@table:name='NieuweTelling']/table:table-row",
        NAMESPACE,
    )

    return _table_rows_to_polling_stations(polling_stations)
