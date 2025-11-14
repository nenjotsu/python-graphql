import strawberry
from app.db.session import get_db
from app.domain.models import User
from app.repository.user_repository import UserRepository


@strawberry.type
class Query:
    @strawberry.field
    async def user(self, info, user_id: int) -> User | None:
        async with get_db() as session:
            return await UserRepository(session).get(user_id)


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_user(self, info, user: User) -> User:
        async with get_db() as session:
            return await UserRepository(session).create(user)
