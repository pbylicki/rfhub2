from pathlib import Path
from typing import Tuple, Dict, List, Optional

from rfhub2.cli.api_client import Client
from rfhub2.cli.test_cases.test_cases_extractor import TestCasesExtractor, TestCase
from rfhub2.model import SuiteHierarchy, TestCaseCreate


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
        tc_count = self.add_test_cases(suites_with_id, tests)
        ts_count = len(suites) + sum(self.count_test_suites(suite) for suite in suites)
        return ts_count, tc_count

    def add_test_suites(self, suites: List[SuiteHierarchy]) -> Optional[List[Dict]]:
        suites_with_id = []
        for suite in suites:
            suite_req = self.client.add_test_suites(suite)
            if suite_req[0] != 201:
                print(suite_req[1]["detail"])
                raise StopIteration
            suites_with_id.append(suite_req[1])
        return suites_with_id

    def add_test_cases(
        self, suites: List[Dict], testcases: List[TestCase]
    ) -> Optional[int]:
        test_cases_with_ids = self._match_tests_with_suite_ids(suites, testcases)
        for test_case in test_cases_with_ids:
            test_case_req = self.client.add_test_case(test_case)
            if test_case_req[0] != 201:
                print(test_case_req[1]["detail"])
                raise StopIteration
        return len(test_cases_with_ids)

    @staticmethod
    def _match_tests_with_suite_ids(
        suites: List[Dict], testcases: List[TestCase]
    ) -> List[TestCaseCreate]:
        suite_ids = TestCaseImporter._extract_id_from_suites(suites)
        return [
            TestCaseCreate(
                name=testcase.name,
                line=testcase.line,
                suite_id=suite_ids.get(testcase.suite_longname),
                doc=testcase.doc,
                source=testcase.source,
                template=testcase.template,
                timeout=testcase.timeout,
                keywords=testcase.keywords,
                tags=testcase.tags,
            )
            for testcase in testcases
        ]

    @staticmethod
    def _extract_id_from_suites(suites: List[Dict]) -> Dict:
        flat_suites = {}
        for suite in suites:
            flat_suites[suite["longname"]] = suite["id"]
            flat_suites = {
                **flat_suites,
                **TestCaseImporter._extract_id_from_suites(suite["suites"]),
            }
        return flat_suites

    def count_test_suites(self, suite: SuiteHierarchy) -> int:
        """
        Returns recursive number of test suites.
        """
        return len(suite.suites) + sum(self.count_test_suites(s) for s in suite.suites)
