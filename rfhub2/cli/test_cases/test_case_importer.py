from pathlib import Path
from typing import Tuple, Dict, List, Optional

from rfhub2.cli.api_client import Client
from .test_cases_extractor import TestCasesExtractor, Suite
from ...model import SuiteHierarchy, SuiteHierarchyWithId


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
        return self.import_test_suites()

    def import_test_suites(self) -> Tuple[int, int]:
        extractor = TestCasesExtractor(self.paths)
        suites = extractor.get_suites()
        tests = extractor.get_test_cases()
        suites_with_id = self.add_test_suites(suites)
        ts_count = len(suites) + sum(self.count_test_suites(suite) for suite in suites)
        # tc_count = sum(self.count_test_cases(suite) for suite in suites)
        return ts_count, len(tests)  # , tc_count

    def add_test_suites(self, suites: List[SuiteHierarchy]) -> Optional[List[Dict]]:
        suites_with_id = []
        for suite in suites:
            suite_req = self.client.add_test_suites(suite)
            if suite_req[0] != 201:
                print(suite_req[1]["detail"])
                raise StopIteration
            suites_with_id.append(suite_req[1])
        return suites_with_id

    def add_test_cases(self, testcases: List) -> Optional[int]:
        pass

    def count_test_cases(self, suite: Suite) -> int:
        """
        Returns recursive number of test cases.
        """
        return sum(len(s.tests) + self.count_test_cases(s) for s in suite.suites)

    def count_test_suites(self, suite: SuiteHierarchy) -> int:
        """
        Returns recursive number of test suites.
        """
        return len(suite.suites) + sum(self.count_test_suites(s) for s in suite.suites)
