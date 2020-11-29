import json

try:
    from robot.libdocpkg.htmlutils import DocToHtml
except ImportError:
    from robot.libdocpkg.htmlwriter import DocToHtml


class DocMixin:
    @property
    def synopsis(self) -> str:
        return self.doc.splitlines()[0] if self.doc else ""

    @property
    def html_doc(self) -> str:
        return DocToHtml("ROBOT")(self.doc) if self.doc else ""


class KeywordMixin(DocMixin):
    @property
    def arg_string(self) -> str:
        """
        Old implementation saves args list as JSON in text field, this is more readable representation for UI
        """
        return ", ".join(json.loads(self.args)) if self.args else ""
