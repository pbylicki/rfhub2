from typing import Generic, Optional, TypeVar

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm.query import Query
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.elements import BinaryExpression

T = TypeVar("T")


class BaseRepository(Generic[T]):
    def __init__(self, db_session: Session):
        self.session = db_session

    @property
    def _items(self) -> Query:  # pragma: no cover
        raise NotImplementedError

    def _id_filter(self, item_id: int) -> BinaryExpression:  # pragma: no cover
        raise NotImplementedError

    def add(self, item: T) -> T:
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def delete(self, item_id: int) -> int:
        row_count = self._items.filter(self._id_filter(item_id)).delete()
        self.session.commit()
        return row_count

    def get(self, item_id: int) -> Optional[T]:
        return self._items.get(item_id)

    def update(self, item: T, update_data: dict):
        item_data = jsonable_encoder(item)
        for field in item_data:
            if field in update_data:
                setattr(item, field, update_data[field])
        return self.add(item)
