from collections.abc import Sequence
from typing import TypeVar
from uuid import UUID

from app.core.database import Base
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T", bound=Base)


class SQLAlchemyRepository:
    model: type[T]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, obj: T) -> T:
        self.session.add(obj)
        await self.session.flush()
        return obj

    async def get(self, obj_id: UUID | int) -> T | None:
        return await self.session.get(self.model, obj_id)

    async def list(
        self,
        offset: int = 0,
        limit: int = 100,
    ) -> Sequence[T]:
        stmt = select(self.model).offset(offset).limit(limit)
        res = await self.session.execute(stmt)
        return res.scalars().all()
