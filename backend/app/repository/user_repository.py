from app.db.models import UserORM
from app.domain.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user: User) -> User:
        orm_user = UserORM(**user.dict())
        self.session.add(orm_user)
        await self.session.commit()
        await self.session.refresh(orm_user)
        return User.from_orm(orm_user)

    async def get(self, user_id: int) -> User | None:
        orm_user = await self.session.execute(
            select(UserORM).where(UserORM.id == user_id)
        )
        return User.from_orm(orm_user.scalars().one_or_none())
