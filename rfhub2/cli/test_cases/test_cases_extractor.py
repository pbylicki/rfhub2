from dataclasses import dataclass
from pathlib import Path

from robot.running.model import TestSuite
from robot.testdoc import TestSuiteFactory
from typing import List, Tuple

from rfhub2.model import KeywordType, MetadataItem


@dataclass
class Keyword:
    name: str
    args: List[str]
    kw_type: KeywordType


@dataclass
class Test:
    doc: str
    id: str
    longname: str
    name: str
    parent: str
    source: str
    tags: List[str]
    template: str
    timeout: str
    keywords: List[Keyword]
    # setup: List[Keyword]
    # teardown: List[Keyword]


@dataclass
class Suite:
    name: str
    doc: str
    # id: str
    # longname: str
    # parent: str
    source: str
    # test_count: int
    tests: List[Test]
    keywords: List[Keyword]
    suites: List["Suite"]
    metadata: List[MetadataItem]
    rpa: bool = False
    # setup: List[Keyword]
    # teardown: List[Keyword]


class TestCasesExtractor:
    def __init__(self, paths: Tuple[Path, ...]) -> None:
        self.paths = paths

    def create_testdoc_from_paths(self) -> List[Suite]:
        """
        Creates TestDoc objects based on robot.testdoc.TestSuiteFactory method.
        """
        testdocs = [TestSuiteFactory(str(path)) for path in self.paths]
        suites = [self.serialize_testdoc_to_suite(testdoc) for testdoc in testdocs]
        return suites

    def serialize_testdoc_to_suite(self, testdoc: TestSuite) -> Suite:
        """
        Serializes testdoc object into Suite dataclass object.
        """
        return Suite(
            name=testdoc.name,
            doc=testdoc.doc,
            source=testdoc.source,
            tests=self.get_tests(testdoc),
            keywords=self.get_keywords(testdoc),
            suites=[self.serialize_testdoc_to_suite(suite) for suite in testdoc.suites if testdoc.suites],
            metadata=[testdoc.metadata],
            rpa=testdoc.rpa,
        )

    def get_tests(self, testdoc: TestSuite) -> List[Test]:
        """
        Returns list of tests.
        """
        return [
            Test(
                doc=test.doc,
                id=test.id,
                longname=test.longname,
                name=test.name,
                parent=test.parent.name,
                source=test.source if hasattr(test, "source") else None,
                tags=list(test.tags),
                template=test.template,
                timeout=test.timeout,
                keywords=self.get_keywords(test),
            )
            for test in testdoc.tests
        ]

    def get_keywords(self, testdoc: TestSuite) -> List[Keyword]:
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
    ) -> List[Keyword]:
        """
        Returns list of setup or teardown keywords.
        """
        kw_type = keyword_type.lower()
        if getattr(testdoc.keywords, kw_type):
            if isinstance(getattr(testdoc.keywords, kw_type), list):
                return [
                    Keyword(
                        name=keyword.name,
                        args=list(getattr(testdoc.keywords, kw_type).args),
                        kw_type=keyword_type,
                    )
                    for keyword in getattr(testdoc.keywords, kw_type)
                ]
            else:
                return [
                    Keyword(
                        name=getattr(testdoc.keywords, kw_type).name,
                        args=list(getattr(testdoc.keywords, kw_type).args),
                        kw_type=keyword_type,
                    )
                ]
        else:
            return []

    def get_normal_keywords(self, testdoc: TestSuite) -> List[Keyword]:
        """
        Returns list of keywords.
        """
        return [
            Keyword(
                name=keyword.name, args=list(keyword.args), kw_type=KeywordType.NORMAL
            )
            for keyword in testdoc.keywords.normal._items
        ]
