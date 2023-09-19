from eml import EMLZip
import csv_write
import traceback


def create_csv_file_a_b_c(path_to_zip: str) -> None:
    try:
        eml_zip = EMLZip.from_zip(path_to_zip)
        check_result = eml_zip.run_protocol()

        csv_write.write_csv_a(check_result.get("eml_checks"), "a.csv")
        csv_write.write_csv_b(check_result.get("eml_checks"), "b.csv")
        csv_write.write_csv_c(check_result.get("eml_checks"), "c.csv")

    except Exception as e:
        print(f"Could not run checks for {path_to_zip}\n{e}")


if __name__ == "__main__":
    create_csv_file_a_b_c(
        "./eml/definitieve-documenten_tk2023_gemeente_dordrecht-20230828-135349.zip"
    )
