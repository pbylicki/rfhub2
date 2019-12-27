import unittest
from pathlib import Path

from rfhub2.cli.statistics_extractor import StatisticsExtractor

FIXTURE_PATH = Path.cwd() / "tests" / "fixtures" / "statistics"
VALID_OUTPUT_XML = FIXTURE_PATH / "output.xml"
INVALID_OUTPUT_XML = FIXTURE_PATH / "invalid_output.xml"
SUBDIR = FIXTURE_PATH / "subdir"


class StatisticsExtractorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.statistics_extractor = StatisticsExtractor(FIXTURE_PATH)

    def test_get_execution_time_should_return_correct_time(self):
        se = StatisticsExtractor(SUBDIR)
        result = se.get_execution_time()
        self.assertEquals(result, "20191225 11:38:08.868")
