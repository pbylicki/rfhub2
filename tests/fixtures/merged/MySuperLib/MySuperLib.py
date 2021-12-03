from robot.api import logger
from robot.api.deco import keyword


class MySuperLib:
    """This is a docstring that should be imported as overview
       MySuperLib"""

    ROBOT_LIBRARY_SCOPE = "GLOBAL"
    __version__ = "6.9.6"

    def __init__(self):
        pass

    @keyword
    def my_awesome_keyword(self, arg1):
        """Docstring for my_awesome_keyword"""
        logger.info(arg1)
        pass
