import json
from sqlalchemy import Column, ForeignKey, Integer, Sequence, Text

from rfhub2.db.model.base_class import Base
from rfhub2.db.model.doc_mixin import DocMixin


class Keyword(Base, DocMixin):
    id = Column(Integer, Sequence("keyword_id_seq"), primary_key=True)
    name = Column(Text, index=True)
    doc = Column(Text)
    args = Column(Text)
    collection_id = Column(
        Integer, ForeignKey("collection.id", ondelete="CASCADE"), nullable=False
    )

    def __str__(self):  # pragma: no cover
        return f"Keyword({self.id},{self.name},{self.doc},{self.args},{self.collection_id})"

    def __repr__(self):  # pragma: no cover
        return str(self)

    @property
    def arg_string(self) -> str:
        """
        Old implementation saves args list as JSON in text field, this is more readable representation for UI
        """
        return ", ".join(json.loads(self.args)) if self.args else ""
