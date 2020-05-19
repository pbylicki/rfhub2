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
    timeout: str    #temp
    keywords: List[Keyword]
    setup: List[Keyword]
    teardown: List[Keyword]


@dataclass
class Suite:
    doc: str
    id: str
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
        return [self.create_testdoc_from_path(path) for path in self.paths]

    def create_testdoc_from_path(self, path: Path):
        """
        Creates TestDoc object based on robot.testdoc.TestSuiteFactory method.
        """
        testdoc = TestSuiteFactory(str(path))
        return self.serialize_testdoc(testdoc)

    def serialize_testdoc(self, testdoc: TestSuite):
        """
        Serializes testdoc object into Suite dataclass object
        """
        setup_kwds = [Keyword(name=str(keyword)) for keyword in testdoc.keywords.setup]
        teardown_kwds = [Keyword(name=str(keyword)) for keyword in testdoc.keywords.teardown]
        tests = [Test(doc=test.doc, id=test.id, longname=test.longname, name=test.name, parent=test.parent,
                      source=test.source, tags=list(test.tags), template=test.template, timeout=test.timeout,
                      keywords=[], setup=[], teardown=[]) for test in testdoc.tests]

        return Suite(doc=testdoc.doc, id=testdoc.id, has_tests=testdoc.has_tests, longname=testdoc.longname,
                     name=testdoc.name, parent=testdoc.parent, source=testdoc.source, suites=testdoc.name,
                     test_count=testdoc.test_count, tests="abc", setup=setup_kwds, teardown=teardown_kwds)
