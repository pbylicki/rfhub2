from dataclasses import dataclass
from pathlib import Path

from robot.running.model import TestSuite
from robot.testdoc import TestSuiteFactory
from typing import List, Tuple, Optional

from rfhub2.model import KeywordType, MetadataItem, SuiteHierarchy, KeywordRef


@dataclass
class Keyword:
    name: str
    args: List[str]
    kw_type: KeywordType


# @dataclass
# class Test:
#     doc: str
#     id: str
#     longname: str
#     name: str
#     parent: str
#     source: str
#     tags: List[str]
#     template: str
#     timeout: str
#     keywords: List[Keyword]
#     # setup: List[Keyword]
#     # teardown: List[Keyword]


@dataclass
class TestCase:
    name: str
    # longname: str
    suite_longname: str
    line: int
    # suite_id: int
    doc: Optional[str]
    source: Optional[str]
    template: Optional[str]
    timeout: Optional[str]
    keywords: List[KeywordRef]
    tags: List[str]


# @dataclass
# class Suite:
#     name: str
#     doc: str
#     # id: str
#     # longname: str
#     # parent: str
#     source: str
#     # test_count: int
#     tests: List[Test]
#     keywords: List[Keyword]
#     suites: List["Suite"]
#     metadata: List[MetadataItem]
#     rpa: bool = False
#     # setup: List[Keyword]
#     # teardown: List[Keyword]


class TestCasesExtractor:
    def __init__(self, paths: Tuple[Path, ...]) -> None:
        self.paths = paths
        self.testdocs: List[TestSuite] = self.create_testdoc_from_paths()

    def create_testdoc_from_paths(self) -> List[TestSuite]:
        """
        Creates TestDoc objects based on robot.testdoc.TestSuiteFactory method.
        """
        return [TestSuiteFactory(str(path)) for path in self.paths]

    def get_suites(self) -> List[SuiteHierarchy]:
        return [self.serialize_testdoc_to_suite(testdoc) for testdoc in self.testdocs]

    def serialize_testdoc_to_suite(self, testdoc: TestSuite) -> SuiteHierarchy:
        """
        Serializes testdoc object into Suite dataclass object.
        """
        return SuiteHierarchy(
            name=testdoc.name,
            doc=testdoc.doc,
            source=testdoc.source,
            # tests=[],#self.get_tests(testdoc),
            keywords=[],  # self.get_keywords(testdoc),
            suites=[
                self.serialize_testdoc_to_suite(suite)
                for suite in testdoc.suites
                if testdoc.suites
            ],
            metadata=[],  # [testdoc.metadata],
            rpa=testdoc.rpa if testdoc.rpa is not None else False,
        )

    def get_test_cases(self) -> List[TestCase]:
        """
        Returns list of tests.
        """
        tests = []
        for testdoc in self.testdocs:
            tests.extend(self._traverse_suites_for_tests(testdoc))
        return tests

    def _traverse_suites_for_tests(self, testdoc: TestSuite) -> List[TestCase]:
        """
        Traverses all suites in top level suites and returns suites list.
        """
        tests = [self._serialize_testcase(test) for test in testdoc.tests]
        for suite in testdoc.suites:
            tests += self._traverse_suites_for_tests(suite)
        return tests

    def _serialize_testcase(self, test):
        return TestCase(
            doc=test.doc,
            line=test.lineno,
            suite_longname=test.longname.replace(f".{test.name}", ""),
            name=test.name,
            source=test.source if hasattr(test, "source") else None,
            tags=list(test.tags),
            template=test.template,
            timeout=test.timeout,
            keywords=self.get_keywords(test),
        )

    def get_keywords(self, testdoc: TestSuite) -> List[KeywordRef]:
        """
        Returns list of keywords.
        """
        return (
            self.get_abnormal_keywords(testdoc, KeywordType.SETUP)
            + self.get_normal_keywords(testdoc)
            + self.get_abnormal_keywords(testdoc, KeywordType.TEARDOWN)
        )

    def get_abnormal_keywords(
        self, testdoc: TestSuite, keyword_type: KeywordType
    ) -> List[KeywordRef]:
        """
        Returns list of setup or teardown keywords.
        """
        kw_type = keyword_type.lower()
        if getattr(testdoc.keywords, kw_type):
            if isinstance(getattr(testdoc.keywords, kw_type), list):
                return [
                    KeywordRef(
                        name=keyword.name,
                        args=list(getattr(testdoc.keywords, kw_type).args),
                        kw_type=keyword_type,
                    )
                    for keyword in getattr(testdoc.keywords, kw_type)
                ]
            else:
                return [
                    KeywordRef(
                        name=getattr(testdoc.keywords, kw_type).name,
                        args=list(getattr(testdoc.keywords, kw_type).args),
                        kw_type=keyword_type,
                    )
                ]
        else:
            return []

    def get_normal_keywords(self, testdoc: TestSuite) -> List[KeywordRef]:
        """
        Returns list of keywords.
        """
        return [
            KeywordRef(
                name=keyword.name, args=list(keyword.args), kw_type=KeywordType.NORMAL
            )
            for keyword in testdoc.keywords.normal._items
        ]
