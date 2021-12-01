from robot.api.deco import keyword


class PyLibrary(object):
    __version__ = "1.0.0"

    @keyword(tags=["❤️", "💀"])
    def keyword_heart_skull(self):
        pass

    @keyword(tags=["❤️", "🚂"])
    def keyword_heart_engine(self):
        pass

    def keyword_no_tag(self):
        pass
