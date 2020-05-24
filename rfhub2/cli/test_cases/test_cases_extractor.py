from dataclasses import dataclass
from pathlib import Path
from robot.running.model import TestSuite
from robot.testdoc import TestSuiteFactory
from typing import List, Tuple


@dataclass
class Keyword:
    name: str


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
    setup: List[Keyword]
    teardown: List[Keyword]


@dataclass
class Suite:
    doc: str
    id: str
    has_tests: bool
    longname: str
    name: str
    parent: str
    source: str
    test_count: int
    tests: List[Test]
    setup: List[Keyword]
    teardown: List[Keyword]


class TestCasesExtractor:
    def __init__(self, paths: Tuple[Path, ...]) -> None:
        self.paths = paths

    def create_testdoc_from_paths(self):
        """
        Creates TestDoc objects based on robot.testdoc.TestSuiteFactory method.
        """
        return [suite for path in self.paths for suite in self.create_testdoc_from_path(path)]

    def create_testdoc_from_path(self, path: Path):
        """
        Creates TestDoc object based on robot.testdoc.TestSuiteFactory method.
        """
        testdoc = TestSuiteFactory(str(path))
        return [self.serialize_testdoc(testdoc)] + self._traverse_suites(testdoc)

    def _traverse_suites(self, testdoc: TestSuite) -> List[Suite]:
        """
        Traverses all suites in top level suites and returns suites list.
        """
        suites = []
        for suite in testdoc.suites:
            suites.append(self.serialize_testdoc(suite))
            sub_suites = self._traverse_suites(suite)
            suites += sub_suites
        return suites

    def serialize_testdoc(self, testdoc: TestSuite) -> Suite:
        """
        Serializes testdoc object into Suite dataclass object.
        """
        return Suite(doc=testdoc.doc, id=testdoc.id, has_tests=testdoc.has_tests, longname=testdoc.longname,
                     name=testdoc.name, parent=testdoc.parent, source=testdoc.source,  # suites=testdoc.name,
                     test_count=testdoc.test_count, tests=self.get_tests(testdoc),
                     setup=self.get_setup_keywords(testdoc), teardown=self.get_teardown_keywords(testdoc))

    def get_tests(self, testdoc: TestSuite) -> List[Test]:
        """
        Returns list of tests.
        """
        return [Test(doc=test.doc, id=test.id, longname=test.longname, name=test.name, parent=test.parent,
                     source=test.source, tags=list(test.tags), template=test.template, timeout=test.timeout,
                     keywords=self.get_normal_keywords(testdoc), setup=self.get_setup_keywords(testdoc),
                     teardown=self.get_teardown_keywords(testdoc)) for test in testdoc.tests]

    def get_setup_keywords(self, testdoc: TestSuite) -> List[Keyword]:
        """
        Returns list of setup keywords.
        """
        if testdoc.keywords.setup:
            if isinstance(testdoc.keywords.setup, list):
                return [Keyword(name=keyword.name) for keyword in testdoc.keywords.setup]
            else:
                return [Keyword(name=testdoc.keywords.setup.name)]
        else:
            return []

    def get_teardown_keywords(self, testdoc: TestSuite) -> List[Keyword]:
        """
        Returns list of teardown keywords.
        """
        if testdoc.keywords.teardown:
            if isinstance(testdoc.keywords.teardown, list):
                return [Keyword(name=keyword.name) for keyword in testdoc.keywords.teardown]
            else:
                return [Keyword(name=testdoc.keywords.teardown.name)]
        else:
            return []

    def get_normal_keywords(self, testdoc: TestSuite) -> List[Keyword]:
        """
        Returns list of keywords.
        """
        if testdoc.keywords.normal._items:
            return [Keyword(name=keyword.name) for keyword in testdoc.keywords.normal._items]
        else:
            return []
