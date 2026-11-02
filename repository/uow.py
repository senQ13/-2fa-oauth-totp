from types import TracebackType
from typing import Self

from app.models.usermodel import User
from core.database import session_maker
from repository.repo import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession


class UnitOfWork:
    def __init__(self) -> None:
        self._session: AsyncSession | None = None
        self.users: BaseRepository[User] | None = None

    async def __aenter__(self) -> Self:
        self._session = session_maker()
        self.users = BaseRepository(self._session, User)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if exc_type is not None:
            await self._session.rollback()
        else:
            await self._session.commit()
        await self._session.close()

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()
