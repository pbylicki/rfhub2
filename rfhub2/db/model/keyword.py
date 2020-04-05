import json
from sqlalchemy import Column, ForeignKey, Integer, Sequence, Text
from typing import List, Optional

from rfhub2.db.model.base_class import Base
from rfhub2.db.model.mixins import KeywordMixin
from rfhub2.db.repository.ordering import OrderingItem
from rfhub2 import model


class Keyword(Base, KeywordMixin):
    id = Column(Integer, Sequence("keyword_id_seq"), primary_key=True)
    name = Column(Text, index=True)
    doc = Column(Text)
    args = Column(Text)
    tags = Column(Text)
    collection_id = Column(
        Integer, ForeignKey("collection.id", ondelete="CASCADE"), nullable=False
    )

    def __str__(self):  # pragma: no cover
        return f"Keyword({self.id},{self.name},{self.doc},{self.args},{self.tags},{self.collection_id})"

    def __repr__(self):  # pragma: no cover
        return str(self)

    @classmethod
    def default_ordering(cls) -> List[OrderingItem]:
        return [OrderingItem("name")]

    @staticmethod
    def create(data: model.KeywordCreate) -> "Keyword":
        return Keyword(
            name=data.name,
            doc=data.doc,
            args=data.args,
            tags=Keyword.to_json_list(data.tags),
            collection_id=data.collection_id,
        )

    def to_model(self) -> model.Keyword:
        collection = self.collection
        return model.Keyword(
            id=self.id,
            name=self.name,
            doc=self.doc,
            args=self.args,
            tags=Keyword.from_json_list(self.tags),
            arg_string=self.arg_string,
            html_doc=self.html_doc,
            synopsis=self.synopsis,
            collection=collection.to_nested_model(),
        )

    def to_nested_model(self) -> model.NestedKeyword:
        return model.NestedKeyword(
            id=self.id,
            name=self.name,
            doc=self.doc,
            args=self.args,
            tags=Keyword.from_json_list(self.tags),
            arg_string=self.arg_string,
            html_doc=self.html_doc,
            synopsis=self.synopsis,
        )

    @staticmethod
    def from_json_list(json_list: Optional[str]) -> List[str]:
        return json.loads(json_list) if json_list else []

    @staticmethod
    def to_json_list(items: Optional[List[str]]) -> str:
        item_list = items or []
        return json.dumps(item_list)
