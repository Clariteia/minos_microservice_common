"""
Copyright (C) 2021 Clariteia SL

This file is part of minos framework.

Minos framework can not be copied and/or distributed without the express permission of Clariteia SL.
"""
from __future__ import (
    annotations,
)

from typing import (
    TYPE_CHECKING,
    AsyncIterator,
)

from ..exceptions import (
    MinosRepositoryAggregateNotFoundException,
    MinosRepositoryDeletedAggregateException,
)
from ..repository import (
    MinosRepository,
    RepositoryAction,
)
from .abc import (
    MinosSnapshot,
)

if TYPE_CHECKING:
    from ..model import (
        Aggregate,
    )


class InMemorySnapshot(MinosSnapshot):
    """In Memory Snapshot class."""

    async def get(self, aggregate_name: str, ids: list[int], **kwargs) -> AsyncIterator[Aggregate]:
        """Retrieve an asynchronous iterator that provides the requested ``Aggregate`` instances.

        :param aggregate_name: Class name of the ``Aggregate`` to be retrieved.
        :param ids: List of identifiers to be retrieved.
        :param kwargs: Additional named arguments.
        :return: An asynchronous iterator that provides the requested ``Aggregate`` instances.
        """
        iterable = map(lambda aggregate_id: self._get_one(aggregate_name, aggregate_id, **kwargs), ids)

        for item in iterable:
            yield await item

    # noinspection PyShadowingBuiltins
    @staticmethod
    async def _get_one(aggregate_name: str, id: int, _repository: MinosRepository, **kwargs) -> Aggregate:
        from operator import (
            attrgetter,
        )

        # noinspection PyTypeChecker
        entries = [v async for v in _repository.select(aggregate_name=aggregate_name, aggregate_id=id)]
        if not len(entries):
            raise MinosRepositoryAggregateNotFoundException(f"Not found any entries for the {id!r} id.")

        entry = max(entries, key=attrgetter("version"))
        if entry.action == RepositoryAction.DELETE:
            raise MinosRepositoryDeletedAggregateException(f"The {id!r} id points to an already deleted aggregate.")
        cls = entry.aggregate_cls
        instance = cls.from_avro_bytes(
            entry.data, id=entry.aggregate_id, version=entry.version, _repository=_repository, **kwargs
        )
        return instance