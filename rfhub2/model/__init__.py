from pydantic import BaseModel
from typing import List, Optional


class NestedCollection(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class NestedKeyword(BaseModel):
    id: int
    name: str
    doc: Optional[str]
    args: Optional[str]

    class Config:
        orm_mode = True


class Collection(NestedCollection):
    type: Optional[str]
    version: Optional[str]
    scope: Optional[str]
    named_args: Optional[str]
    path: Optional[str]
    doc: Optional[str]
    doc_format: Optional[str]
    keywords: List[NestedKeyword]


class Keyword(NestedKeyword):
    collection: NestedCollection
