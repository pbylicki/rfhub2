from datetime import datetime
from enum import Enum
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
    tags: Optional[List[str]]

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
    tags: List[str]


class Collection(NestedCollection, CollectionUpdate):
    keywords: List[NestedKeyword]
    synopsis: Optional[str]
    html_doc: Optional[str]


class CollectionWithStats(Collection):
    times_used: Optional[int]


class Keyword(NestedKeyword):
    collection: NestedCollection


class KeywordWithStats(Keyword):
    times_used: Optional[int]
    avg_elapsed: Optional[float]


class KeywordStatistics(BaseModel):
    collection: str
    keyword: str
    execution_time: datetime
    times_used: int
    total_elapsed: int
    min_elapsed: int
    max_elapsed: int

    class Config:
        orm_mode = True


class KeywordStatisticsList(BaseModel):
    __root__: List[KeywordStatistics]

    @staticmethod
    def of(items: List[KeywordStatistics]) -> "KeywordStatisticsList":
        return KeywordStatisticsList(__root__=items)


class StatisticsDeleted(BaseModel):
    deleted: int


class StatisticsInserted(BaseModel):
    inserted: int


class KeywordType(str, Enum):
    SETUP = "SETUP"
    NORMAL = "NORMAL"
    TEARDOWN = "TEARDOWN"


class KeywordRef(BaseModel):
    name: str
    args: List[str]
    kw_type: KeywordType


class KeywordRefList(BaseModel):
    __root__: List[KeywordRef]

    @staticmethod
    def of(items: List[KeywordRef]) -> "KeywordRefList":
        return KeywordRefList(__root__=items)


class MetadataItem(BaseModel):
    key: str
    value: str


class SuiteMetadata(BaseModel):
    __root__: List[MetadataItem]

    @staticmethod
    def of(items: List[MetadataItem]) -> "SuiteMetadata":
        return SuiteMetadata(__root__=items)


class Suite(BaseModel):
    id: int
    name: str
    longname: str
    doc: Optional[str]
    source: Optional[str]
    is_root: bool
    parent_id: Optional[int]
    test_count: int
    keywords: KeywordRefList
    metadata: SuiteMetadata
    rpa: bool = False


class SuiteHierarchy(BaseModel):
    name: str
    longname: str
    doc: Optional[str]
    source: Optional[str]
    keywords: KeywordRefList
    suites: List["SuiteHierarchy"]
    metadata: SuiteMetadata
    rpa: bool = False


SuiteHierarchy.update_forward_refs()


class SuiteHierarchyWithId(BaseModel):
    id: int
    name: str
    longname: str
    doc: Optional[str]
    source: Optional[str]
    is_root: bool
    keywords: KeywordRefList
    suites: List["SuiteHierarchyWithId"]
    metadata: SuiteMetadata
    rpa: bool = False

    def with_suites(
        self, suites: List["SuiteHierarchyWithId"]
    ) -> "SuiteHierarchyWithId":
        self.suites = suites
        return self


SuiteHierarchyWithId.update_forward_refs()
