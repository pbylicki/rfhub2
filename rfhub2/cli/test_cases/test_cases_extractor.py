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

    def create_testdoc_from_paths(self):
        """
        Creates TestDoc objects based on robot.testdoc.TestSuiteFactory method.
        """
        return [
            suite
            for path in self.paths
            for suite in self.create_testdoc_from_path(path)
        ]

    def create_testdoc_from_path(self, path: Path):
        """
        Creates TestDoc object based on robot.testdoc.TestSuiteFactory method.
        """
        testdoc = TestSuiteFactory(str(path))
        return self._traverse_suites(testdoc)

    def _traverse_suites(self, testdoc: TestSuite) -> List[Suite]:
        """
        Traverses all suites in top level suites and returns suites list.
        """
        suites = [self.serialize_testdoc(testdoc)]
        for suite in testdoc.suites:
            suites += self._traverse_suites(suite)
        return suites

    def serialize_testdoc(self, testdoc: TestSuite) -> Suite:
        """
        Serializes testdoc object into Suite dataclass object.
        """
        return Suite(
            doc=testdoc.doc,
            id=testdoc.id,
            longname=testdoc.longname,
            name=testdoc.name,
            parent=testdoc.parent._name if hasattr(testdoc.parent, "_name") else None,
            source=testdoc.source,
            test_count=testdoc.test_count,
            tests=self.get_tests(testdoc),
            setup=self.get_abnormal_keywords(testdoc, kw_type="setup"),
            teardown=self.get_abnormal_keywords(testdoc, kw_type="teardown"),
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
                keywords=self.get_normal_keywords(test),
                setup=self.get_abnormal_keywords(test, kw_type="setup"),
                teardown=self.get_abnormal_keywords(test, kw_type="teardown"),
            )
            for test in testdoc.tests
        ]

    def get_abnormal_keywords(self, testdoc: TestSuite, kw_type) -> List[Keyword]:
        """
        Returns list of setup or teardown keywords.
        """
        if getattr(testdoc.keywords, kw_type):
            if isinstance(getattr(testdoc.keywords, kw_type), list):
                return [
                    Keyword(
                        name=keyword.name,
                        args=list(getattr(testdoc.keywords, kw_type).args),
                    )
                    for keyword in getattr(testdoc.keywords, kw_type)
                ]
            else:
                return [
                    Keyword(
                        name=getattr(testdoc.keywords, kw_type).name,
                        args=list(getattr(testdoc.keywords, kw_type).args),
                    )
                ]
        else:
            return []

    def get_normal_keywords(self, testdoc: TestSuite) -> List[Keyword]:
        """
        Returns list of keywords.
        """
        return [
            Keyword(name=keyword.name, args=list(keyword.args))
            for keyword in testdoc.keywords.normal._items
        ]
