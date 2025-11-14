from typing import Optional

import strawberry

from app.db.session import AsyncSessionLocal
from app.domain.models import User as DomainUser
from app.repository.user_repository import UserRepository


@strawberry.type
class User:
    id: int
    name: str
    email: str


@strawberry.input
class CreateUserInput:
    name: str
    email: str
    password: str


def to_graphql_user(domain_user: DomainUser) -> User:
    return User(id=domain_user.id, name=domain_user.name, email=domain_user.email)


@strawberry.type
class Query:
    @strawberry.field
    async def user(
        self,
        user_id: int,
    ) -> Optional[User]:
        async with AsyncSessionLocal() as session:
            domain_user = await UserRepository(session).get(user_id)
            return to_graphql_user(domain_user) if domain_user else None


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_user(self, user_input: CreateUserInput) -> User:
        async with AsyncSessionLocal() as session:
            domain_user = DomainUser(
                name=user_input.name,
                email=user_input.email,
                password=user_input.password,
            )
            created = await UserRepository(session).create(domain_user)
            return to_graphql_user(created)


schema = strawberry.Schema(query=Query, mutation=Mutation)
