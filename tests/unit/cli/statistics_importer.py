from pathlib import Path
from responses import RequestsMock
import unittest

from rfhub2.cli.statistics_importer import StatisticsImporter
from rfhub2.cli.api_client import Client
from rfhub2.model import KeywordStatistics, KeywordStatisticsList

FIXTURE_PATH = Path.cwd() / "tests" / "fixtures" / "statistics"
OUTPUT_PATH = FIXTURE_PATH / "output.xml"
EXPECTED_GET_EXECUTION_PATHS = {OUTPUT_PATH, FIXTURE_PATH / "subdir" / "output.xml"}

STATISTICS_1 = KeywordStatistics(
    collection="BuiltIn",
    keyword="Log",
    execution_time="2019-12-25 11:38:08.868000",
    times_used=2,
    total_elapsed=2,
    min_elapsed=1,
    max_elapsed=1,
)
STATISTICS_2 = KeywordStatistics(**{**STATISTICS_1.dict(), "keyword": "Comment"})
STATISTICS_3 = KeywordStatistics(**{**STATISTICS_1.dict(), "keyword": "Should Be True"})
STATISTICS_4 = KeywordStatistics(
    **{
        **STATISTICS_1.dict(),
        "collection": "Test Collection 1",
        "keyword": "Test Keyword 2",
    }
)
STATISTICS_5 = KeywordStatistics(
    **{
        **STATISTICS_1.dict(),
        "collection": "Test Collection 2",
        "keyword": "Test Keyword 1",
    }
)
STATISTICS = [STATISTICS_1, STATISTICS_2, STATISTICS_3]
EXPECTED_STATISTICS_COUNT = 2
VALID_OUTPUT_XML = FIXTURE_PATH / "output.xml"
INVALID_OUTPUT_XML = FIXTURE_PATH / "invalid_output.xml"
SUBDIR = FIXTURE_PATH / "subdir"


class StatisticsImporterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture_path = FIXTURE_PATH
        self.client = Client("http://localhost:8000", "rfhub", "rfhub")
        self.rfhub_importer = StatisticsImporter(self.client, (self.fixture_path,))
        self.stats_url = f"{self.client.api_url}/statistics/keywords/"

    def mock_post_request(
        self, mock: RequestsMock, data: KeywordStatisticsList, status: int = 201
    ) -> None:
        mock.add(
            mock.POST,
            self.stats_url,
            json=data.json(),
            status=status,
            adding_headers={
                "Content-Type": "application/json",
                "accept": "application/json",
            },
        )

    def test_import_data_should_import_data(self):
        with RequestsMock() as mock:
            self.mock_post_request(mock, KeywordStatisticsList.of(STATISTICS))
            rfhub_importer = StatisticsImporter(self.client, (SUBDIR,))
            result = rfhub_importer.import_data()
            self.assertTupleEqual(result, (1, 3), msg=f"{result}")

    def test_import_statistics_should_import_statistics(self):
        with RequestsMock() as mock:
            self.mock_post_request(mock, KeywordStatisticsList.of(STATISTICS))
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
        with RequestsMock() as mock:
            self.mock_post_request(
                mock, KeywordStatisticsList.of([STATISTICS_4, STATISTICS_5]), 201
            )
            result = self.rfhub_importer.add_statistics(
                [STATISTICS_4, STATISTICS_5], OUTPUT_PATH
            )
            self.assertEqual(result, EXPECTED_STATISTICS_COUNT)

    def test_add_statistics_should_fail_on_error_response(self):
        with RequestsMock() as mock:
            mock.add(
                mock.POST,
                self.stats_url,
                json={"detail": "Critical error"},
                status=500,
                adding_headers={
                    "Content-Type": "application/json",
                    "accept": "application/json",
                },
            )
            self.rfhub_importer.add_statistics([STATISTICS_4], OUTPUT_PATH)

    def test_add_statistics_should_fail_on_duplicated_entries(self):
        with RequestsMock() as mock:
            self.mock_post_request(
                mock, KeywordStatisticsList.of([STATISTICS_4, STATISTICS_5]), 400
            )
            result = self.rfhub_importer.add_statistics(
                [STATISTICS_4, STATISTICS_5], OUTPUT_PATH
            )
            self.assertEqual(result, 0)

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
