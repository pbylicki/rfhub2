from .LibWithInit1 import LibWithInit1
from .LibWithInit2 import LibWithInit2


class LibWithInit(LibWithInit1, LibWithInit2):
    """This is a docstring that should be imported as overview"""

    ROBOT_LIBRARY_SCOPE = "GLOBAL"
    __version__ = "6.6.6"

    def __init__(self, dummy=None):
        """
        Here goes some docs that should appear on rfhub2 if init is parametrised

        The library import:

        Examples:
        | Library    LibWithInit   dummy=../one               # add one dummy
        | Library    LibWithInit   path=../one,/global        # add two dummies
        """
        pass
