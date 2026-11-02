from collections.abc import AsyncGenerator

from repository.uow import UnitOfWork


async def get_uow() -> AsyncGenerator[UnitOfWork, None]:
    async with UnitOfWork() as uow:
        yield uow
