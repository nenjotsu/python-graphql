from typing import Optional

from app.db.models import UserORM
from app.domain.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_input: User) -> User:
        orm_user = UserORM(
            name=user_input.name, email=user_input.email, password=user_input.password
        )
        self.session.add(orm_user)
        await self.session.flush()
        await self.session.refresh(orm_user)
        await self.session.commit()
        return User.model_validate(orm_user)

    async def get(self, user_id: int) -> Optional[User]:
        result = await self.session.execute(
            select(UserORM).where(UserORM.id == user_id)
        )
        orm_user = result.scalar_one_or_none()
        return User.model_validate(orm_user) if orm_user else None
