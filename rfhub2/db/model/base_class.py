from collections import OrderedDict
from sqlalchemy import Column
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from typing import List

from rfhub2.db.repository.ordering import OrderingItem


class CustomBase(object):
    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    @classmethod
    def column_mapping(cls):
        return {col.name: col for col in cls.columns()}

    @classmethod
    def columns(cls):
        return cls.__table__._columns

    @classmethod
    def default_ordering(cls) -> List[OrderingItem]:
        return []

    @classmethod
    def ordering_criteria(cls, items: List[OrderingItem]):
        def criterion(col: Column, ordering_item: OrderingItem) -> Column:
            return col if ordering_item.asc else col.desc()

        if not items:
            items = cls.default_ordering()
        mapping = cls.column_mapping()
        return OrderedDict(
            (item.field, criterion(mapping[item.field], item))
            for item in items
            if item.field in mapping
        ).values()


Base = declarative_base(cls=CustomBase)
