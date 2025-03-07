from typing import Generic, Optional, TypeVar

from sqlalchemy import desc
from sqlalchemy.orm import Query

from db import DbModel
from db.base_repo import BaseRepo

T = TypeVar("T", bound=DbModel)


class Pagination(Generic[T]):
    def __init__(self, page: int, page_size: int, total: int, items: list[T]):
        self.page = page
        self.page_size = page_size
        self.total = total
        self.items = items


class DataRepo(BaseRepo, Generic[T]):
    _type: type[T]
    _order_by_map: dict
    _base_order_by_map: dict

    def __init__(self, db_session):
        super().__init__(db_session)
        self._base_order_by_map = dict(
            id=self._type.id,
            created_date=self._type.created_date,
            updated_date=self._type.updated_date,
        )

    def query(self, disable_filters: bool = False) -> Query:
        query = self._session.query(self._type)
        return query

    def save_or_update(self, entity: T) -> T:
        self._session.add(entity)
        self._session.flush()
        return entity

    def get_by_db_id(self, db_id: int, query=None) -> T:
        query = query or self.query()
        return query.filter(self._type.id == db_id).one()

    def single(self, query=None) -> T:
        query = query or self.query()
        return query.one()

    def first(self, query=None) -> Optional[T]:
        query = query or self.query()
        return query.first()

    def list_all(self, query=None) -> list[T]:
        query = query or self.query()
        return query.all()

    def count(self, query=None) -> int:
        query = query or self.query()
        return query.count()

    def list_paged(self, page=1, page_size=10, query=None) -> Pagination[T]:
        query = query or self.query()
        total = query.order_by(None).count()
        items = query.limit(page_size).offset((page - 1) * page_size).all()
        return Pagination(page, page_size, total, items)

    def delete(self, entity: T) -> T:
        self._session.delete(entity)
        self._session.flush()
        return entity

    def with_for_update(self, query=None) -> Query:
        query = query or self.query()
        return query.with_for_update()

    def order_by(self, order_by="id", asc=True, query=None) -> Query:
        query = query or self.query()

        if self._order_by_map is not None and order_by in self._order_by_map:
            order_by_col = self._order_by_map.get(order_by)
        else:
            order_by_col = self._base_order_by_map.get(order_by, self._type.id)
        return query.order_by(order_by_col if asc else desc(order_by_col))
