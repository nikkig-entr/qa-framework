"""Database integration tests."""

from datetime import datetime

import pytest
from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from qa_framework.db.repository import BaseRepository
from qa_framework.db.session import Base


class TestModel(Base):
    """Test model for database tests."""

    __tablename__ = "test_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class TestRepository(BaseRepository[TestModel]):
    """Repository for TestModel."""

    def __init__(self, session):
        super().__init__(session, TestModel)


@pytest.mark.db
class TestDatabase:
    """Database integration tests."""

    @pytest.fixture(autouse=True)
    async def setup_teardown(self, db_manager):
        """Create and drop tables for each test."""
        await db_manager.create_all()
        yield
        await db_manager.drop_all()

    async def test_create_and_read(self, db_session):
        """Test creating and reading an entity."""
        repo = TestRepository(db_session)

        # Create
        entity = await repo.create(name="Test Item", value="Test Value")
        assert entity.id is not None
        assert entity.name == "Test Item"
        assert entity.value == "Test Value"

        # Read
        fetched = await repo.get(entity.id)
        assert fetched is not None
        assert fetched.name == "Test Item"
        assert fetched.value == "Test Value"

    async def test_update(self, db_session):
        """Test updating an entity."""
        repo = TestRepository(db_session)

        entity = await repo.create(name="Original", value="Original Value")
        updated = await repo.update(entity, name="Updated", value="New Value")

        assert updated.name == "Updated"
        assert updated.value == "New Value"

        # Verify persistence
        fetched = await repo.get(entity.id)
        assert fetched.name == "Updated"

    async def test_delete(self, db_session):
        """Test deleting an entity."""
        repo = TestRepository(db_session)

        entity = await repo.create(name="To Delete", value="Delete Me")
        entity_id = entity.id

        deleted = await repo.delete_by_id(entity_id)
        assert deleted is True

        # Verify deletion
        fetched = await repo.get(entity_id)
        assert fetched is None

    async def test_list_with_filters(self, db_session):
        """Test listing with filters."""
        repo = TestRepository(db_session)

        await repo.create(name="Item 1", value="A")
        await repo.create(name="Item 2", value="B")
        await repo.create(name="Item 3", value="A")

        # Filter by value
        items_a = await repo.list(value="A")
        assert len(items_a) == 2
        assert all(item.value == "A" for item in items_a)

        # Pagination
        page1 = await repo.list(limit=2, offset=0, order_by=TestModel.id)
        assert len(page1) == 2

        page2 = await repo.list(limit=2, offset=2, order_by=TestModel.id)
        assert len(page2) == 1

    async def test_count(self, db_session):
        """Test counting entities."""
        repo = TestRepository(db_session)

        assert await repo.count() == 0

        await repo.create(name="Item 1")
        assert await repo.count() == 1

        await repo.create(name="Item 2")
        assert await repo.count() == 2

    async def test_exists(self, db_session):
        """Test existence check."""
        repo = TestRepository(db_session)

        assert await repo.exists(name="NonExistent") is False

        await repo.create(name="Exists")
        assert await repo.exists(name="Exists") is True

    async def test_find_one(self, db_session):
        """Test finding single entity."""
        repo = TestRepository(db_session)

        await repo.create(name="Unique Item", value="Special")

        found = await repo.find_one(name="Unique Item")
        assert found is not None
        assert found.value == "Special"

        not_found = await repo.find_one(name="NonExistent")
        assert not_found is None


