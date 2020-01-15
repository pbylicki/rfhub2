from dataclasses import dataclass


@dataclass
class OrderingItem:
    field: str
    asc: bool = True
