from robot.libdocpkg.htmlwriter import DocToHtml


class DocMixin:
    @property
    def synopsis(self) -> str:
        return self.doc.splitlines()[0] if self.doc else ""

    @property
    def html_doc(self) -> str:
        return DocToHtml("ROBOT")(self.doc) if self.doc else ""
