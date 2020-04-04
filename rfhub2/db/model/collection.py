from sqlalchemy import Column, Integer, Sequence, Text
from sqlalchemy.orm import relationship
from typing import List

from rfhub2.db.model.base_class import Base
from rfhub2.db.model.mixins import DocMixin
from rfhub2.db.repository.ordering import OrderingItem
from rfhub2 import model


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

    @classmethod
    def default_ordering(cls) -> List[OrderingItem]:
        return [OrderingItem("name")]

    @staticmethod
    def create(data: model.CollectionUpdate) -> "Collection":
        return Collection(
            name=data.name,
            type=data.type,
            version=data.version,
            scope=data.scope,
            named_args=data.named_args,
            path=data.path,
            doc=data.doc,
            doc_format=data.doc_format,
        )

    def to_model(self) -> model.Collection:
        keywords = [kw.to_nested_model() for kw in self.keywords]
        return model.Collection(
            id=self.id,
            name=self.name,
            type=self.type,
            version=self.version,
            scope=self.scope,
            named_args=self.named_args,
            path=self.path,
            doc=self.doc,
            doc_format=self.doc_format,
            html_doc=self.html_doc,
            synopsis=self.synopsis,
            keywords=keywords,
        )

    def to_nested_model(self) -> model.NestedCollection:
        return model.NestedCollection(id=self.id, name=self.name)
