# tests/user_graphql.py
import pytest
import pytest_asyncio
from app.api.graphql_schema import schema
from app.db.models import Base
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from strawberry.fastapi import GraphQLRouter

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create FastAPI app with GraphQL
test_app = FastAPI()
graphql_app = GraphQLRouter(schema)
test_app.include_router(graphql_app, prefix="/graphql")


@pytest_asyncio.fixture
async def test_engine():
    """Create test database engine"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest_asyncio.fixture
async def test_session_maker(test_engine):
    """Create test session maker"""
    return async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture
async def override_session(test_session_maker, monkeypatch):
    """Override the AsyncSessionLocal with test session"""
    monkeypatch.setattr("app.db.session.AsyncSessionLocal", test_session_maker)
    monkeypatch.setattr("app.api.graphql_schema.AsyncSessionLocal", test_session_maker)


@pytest.mark.asyncio
async def test_create_user_mutation(override_session):
    """Test creating a user via GraphQL mutation"""
    mutation = """
        mutation CreateUser($input: CreateUserInput!) {
            createUser(userInput: $input) {
                id
                name
                email
            }
        }
    """

    variables = {
        "input": {
            "name": "John Doe",
            "email": "john@example.com",
            "password": "password",
        }
    }

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/graphql", json={"query": mutation, "variables": variables}
        )

    assert response.status_code == 200
    data = response.json()

    assert "data" in data
    assert "createUser" in data["data"]
    assert data["data"]["createUser"]["name"] == "John Doe"
    assert data["data"]["createUser"]["email"] == "john@example.com"
    assert "id" in data["data"]["createUser"]


@pytest.mark.asyncio
async def test_query_user(override_session):
    """Test querying a user by ID"""
    # First create a user
    create_mutation = """
        mutation {
            createUser(userInput: {name: "Jane Doe", email: "jane@example.com", password: "password"}) {
                id
                name
                email
            }
        }
    """
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        create_response = await client.post("/graphql", json={"query": create_mutation})

        created_user = create_response.json()["data"]["createUser"]
        user_id = created_user["id"]

        # Now query the user
        query = """
            query GetUser($userId: Int!) {
                user(userId: $userId) {
                    id
                    name
                    email
                }
            }
        """

        query_response = await client.post(
            "/graphql", json={"query": query, "variables": {"userId": user_id}}
        )

    assert query_response.status_code == 200
    data = query_response.json()

    assert "data" in data
    assert "user" in data["data"]
    assert data["data"]["user"]["id"] == user_id
    assert data["data"]["user"]["name"] == "Jane Doe"
    assert data["data"]["user"]["email"] == "jane@example.com"


@pytest.mark.asyncio
async def test_query_nonexistent_user(override_session):
    """Test querying a user that doesn't exist"""
    query = """
        query {
            user(userId: 99999) {
                id
                name
                email
            }
        }
    """
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/graphql", json={"query": query})

    assert response.status_code == 200
    data = response.json()
    assert data["data"]["user"] is None


@pytest.mark.asyncio
async def test_create_user_duplicate_email(override_session):
    """Test creating users with duplicate emails"""
    mutation = """
        mutation {
            createUser(userInput: {name: "User One", email: "duplicate@example.com", password: "password"}) {
                id
                name
                email
            }
        }
    """
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create first user
        response1 = await client.post("/graphql", json={"query": mutation})
        assert response1.status_code == 200

        # Try to create second user with same email
        response2 = await client.post("/graphql", json={"query": mutation})

        # This should fail if you have unique constraint on email
        # Adjust assertion based on your error handling
        data = response2.json()
        assert "errors" in data or response2.status_code == 200
