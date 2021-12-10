from dataclasses import dataclass
from pathlib import Path

from robot.running.model import TestSuite, Keyword
from robot.testdoc import TestSuiteFactory
from typing import List, Tuple, Optional

from rfhub2.model import KeywordType, MetadataItem, SuiteHierarchy, KeywordRef


@dataclass
class TestCase:
    name: str
    suite_longname: str
    line: int
    doc: Optional[str]
    source: Optional[str]
    template: Optional[str]
    timeout: Optional[str]
    keywords: List[KeywordRef]
    tags: List[str]


class TestCasesExtractor:
    def __init__(self, paths: Tuple[Path, ...]) -> None:
        self.paths = paths
        self.testdocs: List[TestSuite] = self._create_testdoc_from_paths()

    def _create_testdoc_from_paths(self) -> List[TestSuite]:
        """
        Creates TestDoc objects based on robot.testdoc.TestSuiteFactory method.
        """
        return [TestSuiteFactory(str(path)) for path in self.paths]

    def get_suites(self) -> List[SuiteHierarchy]:
        return [self._serialize_testdoc_to_suite(testdoc) for testdoc in self.testdocs]

    def get_test_cases(self) -> List[TestCase]:
        """
        Returns list of tests.
        """
        test_cases = []
        for testdoc in self.testdocs:
            test_cases.extend(TestCasesExtractor._traverse_suites_for_tests(testdoc))
        return test_cases

    def _serialize_testdoc_to_suite(self, testdoc: TestSuite) -> SuiteHierarchy:
        """
        Serializes testdoc object into Suite dataclass object.
        """
        return SuiteHierarchy(
            name=testdoc.name,
            doc=testdoc.doc,
            source=testdoc.source,
            keywords=self._get_keywords(testdoc),
            suites=[
                self._serialize_testdoc_to_suite(suite)
                for suite in testdoc.suites
                if testdoc.suites
            ],
            metadata=[
                MetadataItem(key=md.key, value=md.value) for md in testdoc.metadata
            ],
            rpa=testdoc.rpa if testdoc.rpa is not None else False,
        )

    @staticmethod
    def _traverse_suites_for_tests(testdoc: TestSuite) -> List[TestCase]:
        """
        Traverses all suites in top level suites and returns suites list.
        """
        tests = [TestCasesExtractor._serialize_testcase(test) for test in testdoc.tests]
        for suite in testdoc.suites:
            tests += TestCasesExtractor._traverse_suites_for_tests(suite)
        return tests

    @staticmethod
    def _serialize_testcase(test):
        return TestCase(
            doc=test.doc,
            line=test.lineno,
            suite_longname=test.longname.replace(f".{test.name}", ""),
            name=test.name,
            source=test.source if hasattr(test, "source") else None,
            tags=list(test.tags),
            template=test.template,
            timeout=test.timeout,
            keywords=TestCasesExtractor._get_keywords(test),
        )

    @staticmethod
    def _get_keywords(testdoc: TestSuite) -> List[KeywordRef]:
        """
        Returns list of keywords.
        """
        return (
            TestCasesExtractor._get_abnormal_keywords(testdoc, KeywordType.SETUP)
            + TestCasesExtractor._get_normal_keywords(testdoc)
            + TestCasesExtractor._get_abnormal_keywords(testdoc, KeywordType.TEARDOWN)
        )

    @staticmethod
    def _get_abnormal_keywords(
        testdoc: TestSuite, keyword_type: KeywordType
    ) -> List[KeywordRef]:
        """
        Returns list of setup or teardown keywords.
        """
        kw_type = keyword_type.lower()
        if getattr(testdoc.keywords, kw_type):
            return [
                TestCasesExtractor._serialize_keyword(
                    getattr(testdoc.keywords, kw_type), keyword_type
                )
            ]
        else:
            return []

    @staticmethod
    def _get_normal_keywords(testdoc: TestSuite) -> List[KeywordRef]:
        """
        Returns list of keywords.
        """
        return [
            TestCasesExtractor._serialize_keyword(keyword, KeywordType.NORMAL)
            for keyword in testdoc.keywords.normal._items
        ]

    @staticmethod
    def _serialize_keyword(keyword: Keyword, kw_type: KeywordType) -> KeywordRef:
        return KeywordRef(name=keyword.name, args=list(keyword.args), kw_type=kw_type)
