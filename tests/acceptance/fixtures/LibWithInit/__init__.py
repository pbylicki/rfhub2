from LibWithInit.LibWithInit1 import LibWithInit1
from LibWithInit.LibWithInit2 import LibWithInit2


class LibWithInit(LibWithInit1, LibWithInit2):
    """This is a docstring that should be imported as overview"""

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
