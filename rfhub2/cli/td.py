from robot.testdoc import TestSuiteFactory
from pathlib import Path

dir = Path.cwd() / ".." / ".." / "tests" / "acceptance"

suite = TestSuiteFactory(str(dir)).suites
a = 1
