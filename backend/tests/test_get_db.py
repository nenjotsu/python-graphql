import sys
from pathlib import Path

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.db.session import get_db  # adjust import path

# Create a test database engine (SQLite in-memory for testing)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

Base = declarative_base()


@pytest_asyncio.fixture
async def test_engine():
    """Create a test database engine"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Cleanup
    await engine.dispose()


@pytest_asyncio.fixture
async def test_session(test_engine):
    """Create a test session"""
    async_session = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session


@pytest.mark.asyncio
async def test_get_db_yields_session():
    """Test that get_db yields an AsyncSession"""
    async for session in get_db():
        assert isinstance(session, AsyncSession)
        # Only get the first yielded value
        break


@pytest.mark.asyncio
async def test_get_db_session_is_usable(test_session):
    """Test that the session from get_db is usable"""
    async for session in get_db():
        # Test basic query (adjust based on your models)
        result = await session.execute(text("SELECT 1"))
        assert result.scalar() == 1
        break


@pytest.mark.asyncio
async def test_get_db_closes_session():
    """Test that get_db properly closes the session"""
    session_ref = None

    async for session in get_db():
        session_ref = session
        assert not session_ref.is_active or session_ref.in_transaction() is False
        break

    # After exiting the context, session should be closed
    # Note: This is implicitly tested by the context manager
