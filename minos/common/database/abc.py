"""
Copyright (C) 2021 Clariteia SL

This file is part of minos framework.

Minos framework can not be copied and/or distributed without the express permission of Clariteia SL.
"""
from abc import (
    ABC,
)
from typing import (
    AsyncContextManager,
    AsyncIterator,
    NoReturn,
    Optional,
)

from aiopg import (
    Cursor,
)

from ..setup import (
    MinosSetup,
)
from .pool import (
    PostgreSqlPool,
)


class PostgreSqlMinosDatabase(ABC, MinosSetup):
    """PostgreSql Minos Database base class."""

    def __init__(self, host: str, port: int, database: str, user: str, password: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self._pool = None

    async def _destroy(self) -> NoReturn:
        if self._pool is not None:
            await self._pool.destroy()
            self._pool = None

    async def submit_query_and_fetchone(self, *args, **kwargs) -> tuple:
        """Submit a SQL query and gets the first response.

        :param args: Additional positional arguments.
        :param kwargs: Additional named arguments.
        :return: This method does not return anything.
        """
        return await self.submit_query_and_iter(*args, **kwargs).__anext__()

    async def submit_query_and_iter(self, *args, **kwargs) -> AsyncIterator[tuple]:
        """Submit a SQL query and return an asynchronous iterator.

        :param args: Additional positional arguments.
        :param kwargs: Additional named arguments.
        :return: This method does not return anything.
        """
        async with self.cursor() as cursor:
            await cursor.execute(*args, **kwargs)
            async for row in cursor:
                yield row

    async def submit_query(self, *args, lock: Optional[int] = None, **kwargs) -> NoReturn:
        """Submit a SQL query.

        :param args: Additional positional arguments.
        :param lock: Optional key to perform the query with locking. If not set, the query is performed without any
            lock.
        :param kwargs: Additional named arguments.
        :return: This method does not return anything.
        """
        async with self.cursor() as cursor:
            if lock is not None:
                await cursor.execute("select pg_advisory_lock(%s)", (lock,))
            try:
                await cursor.execute(*args, **kwargs)
            finally:
                if lock is not None:
                    await cursor.execute("select pg_advisory_unlock(%s)", (lock,))

    def cursor(self, *args, **kwargs) -> AsyncContextManager[Cursor]:
        """Get a connection cursor from the pool.

        :param args: Additional positional arguments.
        :param kwargs: Additional named arguments.
        :return: A ``Cursor`` instance wrapped inside a context manager.
        """
        return self.pool.cursor(*args, **kwargs)

    @property
    def pool(self) -> PostgreSqlPool:
        """Get the connections pool.

        :return: A ``Pool`` object.
        """
        if self._pool is None:
            self._pool = PostgreSqlPool(
                host=self.host, port=self.port, database=self.database, user=self.user, password=self.password,
            )
        return self._pool