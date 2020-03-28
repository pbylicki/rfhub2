from fastapi import Query
from typing import List

from rfhub2.db.repository.ordering import OrderingItem


def get_ordering(order: List[str] = Query([])) -> List[OrderingItem]:
    def to_ordering_item(raw: str) -> OrderingItem:
        if raw.startswith("-"):
            return OrderingItem(raw[1:], False)
        else:
            return OrderingItem(raw)

    return [to_ordering_item(item) for item in order if item and item != "-"]
