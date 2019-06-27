import unittest

from rfhub2.utils import abs_path


class PathOpsTest(unittest.TestCase):

    def test_should_build_absolute_path_from_relative_path_inside_the_package(self):
        path = abs_path("tests", "utils", "path_ops_tests.py")
        self.assertEqual(path, __file__)
