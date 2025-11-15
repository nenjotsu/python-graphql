from typing import Optional

import strawberry

from app.db.session import AsyncSessionLocal
from app.domain.models import User as DomainUser
from app.domain.models import UserUpdate as DomainUserUpdate
from app.repository.user_repository import UserRepository


@strawberry.type
class User:
    id: int
    name: str
    email: str


@strawberry.type
class UserUpdate:
    id: int
    name: str
    password: str


@strawberry.input
class CreateUserInput:
    name: str
    email: str
    password: str


@strawberry.input
class UpdateUserInput:
    """All fields optional for partial updates"""

    name: Optional[str] = strawberry.UNSET
    email: Optional[str] = strawberry.UNSET
    password: Optional[str] = strawberry.UNSET


def to_graphql_user(domain_user: DomainUser) -> User:
    return User(id=domain_user.id, name=domain_user.name, email=domain_user.email)


def to_graphql_user_limited(domain_user: DomainUser) -> UserUpdate:
    return UserUpdate(id=domain_user.id, name=domain_user.name)


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

    @strawberry.field
    async def users(self) -> list[User]:
        async with AsyncSessionLocal() as session:
            domain_users = await UserRepository(session).get_all()
            return [to_graphql_user(domain_user) for domain_user in domain_users]


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

    @strawberry.mutation
    async def update_user(
        self, user_id: int, user_input: UpdateUserInput
    ) -> Optional[User]:
        async with AsyncSessionLocal() as session:
            # Convert Strawberry input to domain model
            update_data = {"id": user_id}

            if user_input.name is not strawberry.UNSET:
                update_data["name"] = user_input.name
            if user_input.email is not strawberry.UNSET:
                update_data["email"] = user_input.email
            if user_input.password is not strawberry.UNSET:
                update_data["password"] = user_input.password

            user_update = DomainUserUpdate(**update_data)
            updated_user = await UserRepository(session).update(user_id, user_update)

            if updated_user is None:
                return None

            return User(
                id=updated_user.id, name=updated_user.name, email=updated_user.email
            )

    @strawberry.mutation
    async def delete_user(self, user_id: int) -> bool:
        async with AsyncSessionLocal() as session:
            return await UserRepository(session).delete(user_id)


schema = strawberry.Schema(query=Query, mutation=Mutation)
