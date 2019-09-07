from sqlalchemy import Column, Integer, Sequence, Text
from sqlalchemy.orm import relationship

from rfhub2.db.model.base_class import Base
from rfhub2.db.model.doc_mixin import DocMixin


class Collection(Base, DocMixin):
    id = Column(Integer, Sequence("collection_id_seq"), primary_key=True)
    name = Column(Text, index=True)
    type = Column(Text)
    version = Column(Text)
    scope = Column(Text)
    named_args = Column(Text)
    path = Column(Text)
    doc = Column(Text)
    doc_format = Column(Text)
    keywords = relationship(
        "Keyword",
        backref="collection",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="Keyword.name",
    )

    def __str__(self):  # pragma: no cover
        return (
            f"Collection({self.id},{self.name},{self.type},{self.version},"
            + f"{self.scope},{self.named_args},{self.path},{self.doc},{self.doc_format})"
        )

    def __repr__(self):  # pragma: no cover
        return str(self)
