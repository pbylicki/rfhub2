from pathlib import Path
from typing import Tuple, List

from rfhub2.cli.api_client import Client
from .test_cases_extractor import TestCasesExtractor, Suite
from ...model import SuiteHierarchy


class TestCaseImporter:
    def __init__(self, client: Client, paths: Tuple[Path, ...], load_mode: str) -> None:
        self.client = client
        self.paths = paths
        self.load_mode = load_mode

    def import_data(self) -> Tuple[int, int]:
        """
        Wrapper for import_libraries, import_statistics and import_test_cases to unify modules.
        :return: Number of suites and testcases loaded
        """
        return self.import_test_cases()

    def import_test_cases(self) -> Tuple[int, int]:
        extractor = TestCasesExtractor(self.paths)
        suites = extractor.create_testdoc_from_paths()
        tc_count = sum(self.count_test_cases(suite) for suite in suites)
        ts_count = len(suites) + sum(self.count_test_suites(suite) for suite in suites)
        for suite in suites:
            suite_req = self.client.add_test_suites(SuiteHierarchy(suite))
            if suite_req[0] != 201:
                print(suite_req[1]["detail"])
                raise StopIteration

        return ts_count, tc_count



    def count_test_cases(self, suite: Suite) -> int:
        """
        Returns recursive number of test cases.
        """
        return sum(len(s.tests) + self.count_test_cases(s) for s in suite.suites)

    def count_test_suites(self, suite: Suite) -> int:
        """
        Returns recursive number of test suites.
        """
        return len(suite.suites) + sum(self.count_test_suites(s) for s in suite.suites)
