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
# STATISTICS_1 = {
#   "collection": "Test Collection 1",
#   "keyword": "Test Keyword 1",
#   "execution_time": "2019-12-25T09:29:48.636Z",
#   "times_used": 10,
#   "total_elapsed": 5000,
#   "min_elapsed": 3000,
#   "max_elapsed": 7000
# }
# STATISTICS_2 = {
#   "collection": "Test Collection 1",
#   "keyword": "Test Keyword 2",
#   "execution_time": "2019-12-25T09:29:48.636Z",
#   "times_used": 25,
#   "total_elapsed": 500,
#   "min_elapsed": 300,
#   "max_elapsed": 700
# }

STATISTICS_1 = {
    "collection": "BuiltIn",
    "keyword": "Log",
    "execution_time": "2019-12-25 11:38:08.868000",
    "times_used": 2,
    "total_elapsed": 2,
    "min_elapsed": 1,
    "max_elapsed": 1
}
STATISTICS_2 = {
    "collection": "BuiltIn",
    "keyword": "Comment",
    "execution_time": "2019-12-25 11:38:08.868000",
    "times_used": 2,
    "total_elapsed": 2,
    "min_elapsed": 1,
    "max_elapsed": 1
}
STATISTICS_3 = {
    "collection": "BuiltIn",
    "keyword": "Should Be True",
    "execution_time": "2019-12-25 11:38:08.868000",
    "times_used": 2,
    "total_elapsed": 1,
    "min_elapsed": 0,
    "max_elapsed": 1
}
STATISTICS_4 = {
    "collection": "a",
    "keyword": "b",
    "execution_time": "2019-12-25 11:38:08.868000",
    "times_used": 2,
    "total_elapsed": 2,
    "min_elapsed": 1,
    "max_elapsed": 1
}
STATISTICS_5 = {
    "collection": "b",
    "keyword": "a",
    "execution_time": "2019-12-25 11:38:08.868000",
    "times_used": 2,
    "total_elapsed": 2,
    "min_elapsed": 1,
    "max_elapsed": 1
}
STATISTICS = [STATISTICS_1, STATISTICS_2, STATISTICS_3]
EXPECTED_STATISTICS_COUNT = 1, 2
VALID_OUTPUT_XML = FIXTURE_PATH / "output.xml"
INVALID_OUTPUT_XML = FIXTURE_PATH / "invalid_output.xml"
SMALL_OUTPUT = FIXTURE_PATH / "subdir" / "output.xml"


class StatisticsImporterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture_path = FIXTURE_PATH
        self.client = Client("http://localhost:8000", "rfhub", "rfhub")
        self.rfhub_importer = StatisticsImporter(self.client, (self.fixture_path,))

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
            rfhub_importer = StatisticsImporter(self.client, (SMALL_OUTPUT,))
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
        rfhub_importer = StatisticsImporter(self.client, (FIXTURE_PATH, FIXTURE_PATH / "subdir"),)
        result = rfhub_importer.get_execution_files_paths()
        self.assertSetEqual(result, EXPECTED_GET_EXECUTION_PATHS)

    def test_add_statistics_should_return_number_of_loaded_collections_and_keywords(self):
        with responses.RequestsMock() as rsps:
            for stat in [STATISTICS_4, STATISTICS_5]:
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
            result = self.rfhub_importer.add_statistics([STATISTICS_1, STATISTICS_2])
            self.assertTupleEqual(result, EXPECTED_STATISTICS_COUNT)

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
