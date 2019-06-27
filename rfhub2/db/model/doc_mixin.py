from robot.libdocpkg.htmlwriter import DocToHtml


class DocMixin:

    @property
    def synopsis(self) -> str:
        return self.doc.splitlines()[0] if self.doc else ""

    def html_doc(self, doc_format: str = "ROBOT") -> str:
        return DocToHtml(doc_format)(self.doc) if self.doc else ""
