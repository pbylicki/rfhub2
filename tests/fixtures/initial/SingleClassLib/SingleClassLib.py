from robot.api.deco import keyword


class SingleClassLib(object):
    """
    Overview that should be imported for SingleClassLib.
    """

    __version__ = "1.2.3"

    def __init__(self):
        self.b = None

    @keyword(tags=["tag_1", "tag_2"])
    def single_class_lib_method_1(self):
        """Docstring for single_class_lib_method_1"""
        pass

    def single_class_lib_method_2(self):
        """Docstring for single_class_lib_method_2"""
        pass

    def single_class_lib_method_3(self, param_1, param_2):
        """Docstring for single_class_lib_method_3 with two params"""
        pass


class SingleClassLibThatShouldNotBeImported(object):
    """
        Overview that should not be imported for SingleClassLibThatShouldNotBeImported.
    """

    def __init__(self):
        self.b = None

    def single_class_lib_that_should_not_be_imported_method_1(self):
        """Docstring for single_class_lib_that_should_not_be_imported_method_1"""
        pass

    def single_class_lib_that_should_not_be_imported_method_2(self):
        """Docstring for single_class_lib_that_should_not_be_imported_method_2"""
        pass
