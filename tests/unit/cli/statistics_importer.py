import responses
import unittest
from pathlib import Path

from rfhub2.cli.statistics_importer import StatisticsImporter
from rfhub2.cli.api_client import Client

FIXTURE_PATH = Path.cwd() / "tests" / "fixtures" / "statistics"
EXPECTED_GET_EXECUTION_PATHS = {
    FIXTURE_PATH / "output.xml",
    FIXTURE_PATH / "subdir" / "output.xml",
}

STATISTICS_1 = {
    "collection": "BuiltIn",
    "keyword": "Log",
    "execution_time": "2019-12-25 11:38:08.868000",
    "times_used": 2,
    "total_elapsed": 2,
    "min_elapsed": 1,
    "max_elapsed": 1,
}
STATISTICS_2 = {**STATISTICS_1, "keyword": "Comment"}
STATISTICS_3 = {**STATISTICS_1, "keyword": "Should Be True"}
STATISTICS_4 = {
    "collection": "Test Collection 1",
    "keyword": "Test Keyword 2",
    "execution_time": "2019-12-25 11:38:08.868000",
    "times_used": 2,
    "total_elapsed": 2,
    "min_elapsed": 1,
    "max_elapsed": 1,
}
STATISTICS_5 = {
    **STATISTICS_4,
    "collection": "Test Collection 2",
    "keyword": "Test Keyword 1",
}
STATISTICS_6 = {"detail": "dummy request destined to fail"}
STATISTICS = [STATISTICS_1, STATISTICS_2, STATISTICS_3]
EXPECTED_STATISTICS_COUNT = 2, 2
EXPECTED_STATISTICS_DUPL_COUNT = 1, 1
VALID_OUTPUT_XML = FIXTURE_PATH / "output.xml"
INVALID_OUTPUT_XML = FIXTURE_PATH / "invalid_output.xml"
SUBDIR = FIXTURE_PATH / "subdir"


class StatisticsImporterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture_path = FIXTURE_PATH
        self.client = Client("http://localhost:8000", "rfhub", "rfhub")
        self.rfhub_importer = StatisticsImporter(self.client, (self.fixture_path,))

    def test_import_data_should_import_data(self):
        with responses.RequestsMock() as rsps:
            for stat in STATISTICS:
                rsps.add(
                    responses.POST,
                    f"{self.client.api_url}/statistics/",
                    json=stat,
                    status=201,
                    adding_headers={
                        "Content-Type": "application/json",
                        "accept": "application/json",
                    },
                )
            rfhub_importer = StatisticsImporter(self.client, (SUBDIR,))
            result = rfhub_importer.import_data()
            self.assertTupleEqual(result, (1, 3), msg=f"{result}")

    def test_import_statistics_should_import_statistics(self):
        with responses.RequestsMock() as rsps:
            for stat in STATISTICS:
                rsps.add(
                    responses.POST,
                    f"{self.client.api_url}/statistics/",
                    json=stat,
                    status=201,
                    adding_headers={
                        "Content-Type": "application/json",
                        "accept": "application/json",
                    },
                )
            rfhub_importer = StatisticsImporter(self.client, (SUBDIR,))
            result = rfhub_importer.import_statistics()
            self.assertTupleEqual(result, (1, 3), msg=f"{result}")

    def test_get_execution_files_paths_without_subdir_provided_should_return_set_of_paths(
        self
    ):
        result = self.rfhub_importer.get_execution_files_paths()
        self.assertSetEqual(result, EXPECTED_GET_EXECUTION_PATHS)

    def test_get_execution_files_paths_with_subdir_provided_should_return_set_of_paths(
        self
    ):
        rfhub_importer = StatisticsImporter(
            self.client, (FIXTURE_PATH, FIXTURE_PATH / "subdir")
        )
        result = rfhub_importer.get_execution_files_paths()
        self.assertSetEqual(result, EXPECTED_GET_EXECUTION_PATHS)

    def test_add_statistics_should_return_number_of_loaded_collections_and_keywords(
        self
    ):
        with responses.RequestsMock() as rsps:
            for stat, rc in zip(
                [STATISTICS_4, STATISTICS_5, STATISTICS_5], (201, 201, 400)
            ):
                rsps.add(
                    responses.POST,
                    f"{self.client.api_url}/statistics/",
                    json=stat,
                    status=rc,
                    adding_headers={
                        "Content-Type": "application/json",
                        "accept": "application/json",
                    },
                )
            result = self.rfhub_importer.add_statistics(
                [STATISTICS_4, STATISTICS_5, STATISTICS_5]
            )
            self.assertTupleEqual(result, EXPECTED_STATISTICS_COUNT)

    def test_add_statistics_should_return_number_of_loaded_collections_and_keywords_with_duplicated_data(
        self
    ):
        with self.assertRaises(StopIteration) as cm:
            with responses.RequestsMock() as rsps:
                for stat, rc in zip([STATISTICS_4, STATISTICS_6], (201, 422)):
                    rsps.add(
                        responses.POST,
                        f"{self.client.api_url}/statistics/",
                        json=stat,
                        status=rc,
                        adding_headers={
                            "Content-Type": "application/json",
                            "accept": "application/json",
                        },
                    )
                self.rfhub_importer.add_statistics([STATISTICS_4, STATISTICS_6])

    def test__is_valid_execution_file_should_return_true_on_valid_file(self):
        result = StatisticsImporter._is_valid_execution_file(VALID_OUTPUT_XML)
        self.assertTrue(
            result, "method should return true if file is valid output.xml file"
        )

    def test__is_valid_execution_file_should_return_false_on_invalid_file(self):
        result = StatisticsImporter._is_valid_execution_file(INVALID_OUTPUT_XML)
        self.assertFalse(
            result, "method should return false if file is not valid output.xml file"
        )
