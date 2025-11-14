from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.models import UserORM
from app.domain.models import User, UserUpdate


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

    async def get_all(self) -> list[User]:
        result = await self.session.execute(select(UserORM))
        orm_users = result.scalars().all()
        return [User.model_validate(orm_user) for orm_user in orm_users]

    async def update(self, user_id: int, user_input: UserUpdate) -> Optional[User]:
        orm_user = await self.get(user_id)
        if not orm_user:
            return None
        orm_user.name = user_input.name
        orm_user.password = user_input.password
        await self.session.commit()
        await self.session.refresh(orm_user)
        return UserUpdate.model_validate(orm_user)

    async def delete(self, user_id: int) -> bool:
        orm_user = await self.get(user_id)
        if not orm_user:
            return False
        await self.session.delete(orm_user)
        await self.session.commit()
        return True
