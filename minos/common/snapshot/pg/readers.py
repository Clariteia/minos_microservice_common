from __future__ import (
    annotations,
)

import logging
from typing import (
    TYPE_CHECKING,
    AsyncIterator,
    Optional,
)
from uuid import (
    UUID,
)

from ...exceptions import (
    MinosSnapshotAggregateNotFoundException,
)
from ...queries import (
    Condition,
    _Condition,
    _Ordering,
)
from ...uuid import (
    NULL_UUID,
)
from ..entries import (
    SnapshotEntry,
)
from .abc import (
    PostgreSqlSnapshotSetup,
)
from .queries import (
    PostgreSqlSnapshotQueryBuilder,
)

if TYPE_CHECKING:
    from ...model import (
        Aggregate,
    )

logger = logging.getLogger(__name__)


class PostgreSqlSnapshotReader(PostgreSqlSnapshotSetup):
    """PostgreSQL Snapshot class.

   The snapshot provides a direct accessor to the aggregate instances stored as events by the event repository class.
    """

    async def get(self, aggregate_name: str, uuid: UUID, transaction_uuid: UUID = NULL_UUID, **kwargs) -> Aggregate:
        """Get an aggregate instance from its identifier.

        :param aggregate_name: Class name of the ``Aggregate``.
        :param uuid: Identifier of the ``Aggregate``.
        :param transaction_uuid: Optional argument to return the snapshot view within a transaction.
        :param kwargs: Additional named arguments.
        :return: The ``Aggregate`` instance.
        """
        snapshot_entry = await self.get_entry(aggregate_name, uuid, transaction_uuid, **kwargs)
        aggregate = snapshot_entry.build_aggregate(**kwargs)
        return aggregate

    # noinspection PyUnusedLocal
    async def get_entry(
        self, aggregate_name: str, uuid: UUID, transaction_uuid: UUID = NULL_UUID, **kwargs
    ) -> SnapshotEntry:
        """Get an ``SnapshotEntry`` from its identifier.

        :param aggregate_name: Class name of the ``Aggregate``.
        :param uuid: Identifier of the ``Aggregate``.
        :param transaction_uuid: Optional argument to return the snapshot view within a transaction.
        :param kwargs: Additional named arguments.
        :return: The ``Aggregate`` instance.
        """

        try:
            return await self.find_entries(
                aggregate_name, Condition.EQUAL("uuid", uuid), transaction_uuid=transaction_uuid, **kwargs
            ).__anext__()
        except StopAsyncIteration:
            raise MinosSnapshotAggregateNotFoundException(f"Some aggregates could not be found: {uuid!s}")

    async def find(
        self,
        aggregate_name: str,
        condition: _Condition,
        ordering: Optional[_Ordering] = None,
        limit: Optional[int] = None,
        streaming_mode: bool = False,
        transaction_uuid: UUID = NULL_UUID,
        **kwargs,
    ) -> AsyncIterator[Aggregate]:
        """Find a collection of ``Aggregate`` instances based on a ``Condition``.

        :param aggregate_name: Class name of the ``Aggregate``.
        :param condition: The condition that must be satisfied by the ``Aggregate`` instances.
        :param ordering: Optional argument to return the instance with specific ordering strategy. The default behaviour
            is to retrieve them without any order pattern.
        :param limit: Optional argument to return only a subset of instances. The default behaviour is to return all the
            instances that meet the given condition.
        :param streaming_mode: If ``True`` return the values in streaming directly from the database (keep an open
            database connection), otherwise preloads the full set of values on memory and then retrieves them.
        :param transaction_uuid: Optional argument to return the snapshot view within a transaction.
        :param kwargs: Additional named arguments.
        :return: An asynchronous iterator that containing the ``Aggregate`` instances.
        """
        async for snapshot_entry in self.find_entries(
            aggregate_name, condition, ordering, limit, streaming_mode, transaction_uuid, **kwargs,
        ):
            yield snapshot_entry.build_aggregate(**kwargs)

    async def find_entries(
        self,
        aggregate_name: str,
        condition: _Condition,
        ordering: Optional[_Ordering] = None,
        limit: Optional[int] = None,
        streaming_mode: bool = False,
        transaction_uuid: UUID = NULL_UUID,
        exclude_deleted: bool = True,
        **kwargs,
    ) -> AsyncIterator[SnapshotEntry]:
        """Find a collection of ``SnapshotEntry`` instances based on a ``Condition``.

        :param aggregate_name: Class name of the ``Aggregate``.
        :param condition: The condition that must be satisfied by the ``Aggregate`` instances.
        :param ordering: Optional argument to return the instance with specific ordering strategy. The default behaviour
            is to retrieve them without any order pattern.
        :param limit: Optional argument to return only a subset of instances. The default behaviour is to return all the
            instances that meet the given condition.
        :param streaming_mode: If ``True`` return the values in streaming directly from the database (keep an open
            database connection), otherwise preloads the full set of values on memory and then retrieves them.
        :param transaction_uuid: Optional argument to return the snapshot view within a transaction.
        :param exclude_deleted: If ``True``, deleted ``Aggregate`` entries are included, otherwise deleted ``Aggregate``
            entries are filtered.
        :param kwargs: Additional named arguments.
        :return: An asynchronous iterator that containing the ``Aggregate`` instances.
        """
        # FIXME: Extract transaction identifiers.
        if transaction_uuid == NULL_UUID:
            transaction_uuids = (NULL_UUID,)
        else:
            transaction_uuids = (NULL_UUID, transaction_uuid)

        qb = PostgreSqlSnapshotQueryBuilder(
            aggregate_name, condition, ordering, limit, transaction_uuids, exclude_deleted,
        )
        query, parameters = qb.build()

        async with self.cursor() as cursor:
            # noinspection PyTypeChecker
            await cursor.execute(query, parameters)
            if streaming_mode:
                async for row in cursor:
                    # noinspection PyArgumentList
                    yield SnapshotEntry(*row)
                return
            else:
                rows = await cursor.fetchall()
        for row in rows:
            yield SnapshotEntry(*row)
