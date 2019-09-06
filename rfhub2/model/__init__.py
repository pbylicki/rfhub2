from pydantic import BaseModel
from typing import List, Optional


class VersionInfo(BaseModel):
    title: str
    version: str


class Healthcheck(BaseModel):
    db: str


class NestedCollection(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class KeywordUpdate(BaseModel):
    name: str
    doc: Optional[str]
    args: Optional[str]

    class Config:
        orm_mode = True


class KeywordCreate(KeywordUpdate):
    collection_id: int


class CollectionUpdate(BaseModel):
    name: str
    type: Optional[str]
    version: Optional[str]
    scope: Optional[str]
    named_args: Optional[str]
    path: Optional[str]
    doc: Optional[str]
    doc_format: Optional[str]


class NestedKeyword(KeywordUpdate):
    id: int
    synopsis: Optional[str]
    html_doc: Optional[str]
    arg_string: Optional[str]


class Collection(NestedCollection, CollectionUpdate):
    keywords: List[NestedKeyword]
    synopsis: Optional[str]
    html_doc: Optional[str]


class Keyword(NestedKeyword):
    collection: NestedCollection
