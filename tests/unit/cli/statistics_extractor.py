import unittest
from pathlib import Path

from rfhub2.cli.statistics_extractor import StatisticsExtractor

FIXTURE_PATH = Path.cwd() / "tests" / "fixtures" / "statistics"
SUBDIR = FIXTURE_PATH / "subdir"
SMALL_OUTPUT_XML = SUBDIR / "output.xml"

KEYWORD_1 = {"library": "BuiltIn", "name": "Log", "elapsed": 1}
KEYWORD_2 = {"library": "BuiltIn", "name": "Comment", "elapsed": 1}
KEYWORD_3 = {"library": "BuiltIn", "name": "Should Be True", "elapsed": 1}
KEYWORD = [KEYWORD_1, KEYWORD_2, KEYWORD_3, KEYWORD_1, KEYWORD_2, KEYWORD_3]

STATISTICS_1 = {
    "collection": "BuiltIn",
    "keyword": "Log",
    "execution_time": "2019-12-25 11:38:08.868000",
    "times_used": 2,
    "total_elapsed": 2,
    "min_elapsed": 1,
    "max_elapsed": 1,
}
STATISTICS_2 = {
    "collection": "BuiltIn",
    "keyword": "Comment",
    "execution_time": "2019-12-25 11:38:08.868000",
    "times_used": 2,
    "total_elapsed": 2,
    "min_elapsed": 1,
    "max_elapsed": 1,
}
STATISTICS_3 = {
    "collection": "BuiltIn",
    "keyword": "Should Be True",
    "execution_time": "2019-12-25 11:38:08.868000",
    "times_used": 2,
    "total_elapsed": 2,
    "min_elapsed": 1,
    "max_elapsed": 1,
}
STATISTICS = [STATISTICS_1, STATISTICS_2, STATISTICS_3]


class StatisticsExtractorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.statistics_extractor = StatisticsExtractor(SMALL_OUTPUT_XML)

    def test_compute_statistics_should_return_expected_data(self):
        result = self.statistics_extractor.compute_statistics()
        self.assertListEqual(result, STATISTICS)

    def test_parse_xml_keywords_should_return_expected_statistics(self):
        result = self.statistics_extractor.parse_xml_keywords()
        self.assertListEqual(result, KEYWORD)

    def test_get_execution_time_should_return_correct_time(self):
        # se = StatisticsExtractor(SMALL_OUTPUT_XML)
        result = self.statistics_extractor.get_execution_time()
        self.assertEquals(result, "2019-12-25 11:38:08.868000")
