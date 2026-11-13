"""Base repository pattern for database operations."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Generic, TypeVar

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

T = TypeVar("T", bound=DeclarativeBase)


class BaseRepository(Generic[T]):
    """Base repository with common CRUD operations."""

    def __init__(self, session: AsyncSession, model: type[T]) -> None:
        self._session = session
        self._model = model

    @property
    def model(self) -> type[T]:
        return self._model

    @property
    def session(self) -> AsyncSession:
        return self._session

    async def get(self, id: Any) -> T | None:
        """Get entity by primary key."""
        return await self._session.get(self._model, id)

    async def get_or_raise(self, id: Any) -> T:
        """Get entity by primary key or raise."""
        entity = await self.get(id)
        if entity is None:
            raise ValueError(f"{self._model.__name__} with id={id} not found")
        return entity

    async def list(
        self,
        *,
        limit: int | None = None,
        offset: int = 0,
        order_by: Any = None,
        **filters: Any,
    ) -> Sequence[T]:
        """List entities with optional filters."""
        stmt = select(self._model)

        for key, value in filters.items():
            if hasattr(self._model, key):
                stmt = stmt.where(getattr(self._model, key) == value)

        if order_by is not None:
            stmt = stmt.order_by(order_by)

        if limit:
            stmt = stmt.limit(limit)
        if offset:
            stmt = stmt.offset(offset)

        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def count(self, **filters: Any) -> int:
        """Count entities with optional filters."""
        stmt = select(func.count()).select_from(self._model)

        for key, value in filters.items():
            if hasattr(self._model, key):
                stmt = stmt.where(getattr(self._model, key) == value)

        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def create(self, **kwargs: Any) -> T:
        """Create new entity."""
        entity = self._model(**kwargs)
        self._session.add(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def update(self, entity: T, **kwargs: Any) -> T:
        """Update entity."""
        for key, value in kwargs.items():
            if hasattr(entity, key):
                setattr(entity, key, value)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def delete(self, entity: T) -> None:
        """Delete entity."""
        await self._session.delete(entity)
        await self._session.flush()

    async def delete_by_id(self, id: Any) -> bool:
        """Delete entity by ID. Returns True if deleted."""
        entity = await self.get(id)
        if entity:
            await self.delete(entity)
            return True
        return False

    async def exists(self, **filters: Any) -> bool:
        """Check if entity exists."""
        count = await self.count(**filters)
        return count > 0

    async def find_one(self, **filters: Any) -> T | None:
        """Find single entity by filters."""
        stmt = select(self._model)
        for key, value in filters.items():
            if hasattr(self._model, key):
                stmt = stmt.where(getattr(self._model, key) == value)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_one_or_raise(self, **filters: Any) -> T:
        """Find single entity by filters or raise."""
        entity = await self.find_one(**filters)
        if entity is None:
            raise ValueError(f"{self._model.__name__} not found with filters: {filters}")
        return entity