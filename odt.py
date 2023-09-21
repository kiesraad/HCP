from zipfile import ZipFile
from enum import Enum, auto
from typing import List
import xml_parser


class ODT_TYPE(Enum):
    na31_1 = auto()
    na31_2 = auto()


class ODT:
    def __init__(self, type: ODT_TYPE, odt_xml):
        self.type = type
        self.odt_xml = odt_xml

    @staticmethod
    def from_path(odt_path):
        try:
            if "Model_Na31-1.odt" in odt_path:
                return ODT(
                    type=ODT_TYPE.na31_1, odt_xml=_extract_odt_xml_root(odt_path)
                )
            elif "Model_Na31-2.odt" in odt_path:
                return ODT(
                    type=ODT_TYPE.na31_2, odt_xml=_extract_odt_xml_root(odt_path)
                )
            return None
        except Exception:
            return None

    def get_already_recounted_polling_stations(self) -> List[str]:
        try:
            match self.type:
                case ODT_TYPE.na31_1:
                    return xml_parser.get_polling_stations_with_recounts(self.odt_xml)
                case ODT_TYPE.na31_2:
                    # TODO Not implemented
                    return []
                case _:
                    return []
        except Exception:
            return []


def _extract_odt_xml_root(odt_file):
    with ZipFile(odt_file) as odt_zip:
        with odt_zip.open("content.xml") as odt_xml:
            return xml_parser.parse_xml(odt_xml)
