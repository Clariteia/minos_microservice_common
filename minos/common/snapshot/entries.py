from __future__ import (
    annotations,
)

import json
from datetime import (
    datetime,
)
from typing import (
    TYPE_CHECKING,
    Any,
    Iterable,
    Optional,
    Type,
    Union,
)
from uuid import (
    UUID,
)

from ..exceptions import (
    MinosSnapshotDeletedAggregateException,
)
from ..importlib import (
    import_module,
)
from ..protocol import (
    MinosJsonBinaryProtocol,
)
from ..repository import (
    RepositoryEntry,
)

if TYPE_CHECKING:
    from ..model import (
        Aggregate,
    )


class SnapshotEntry:
    """Minos Snapshot Entry class.

    Is the python object representation of a row in the ``snapshot`` storage system.
    """

    __slots__ = "aggregate_uuid", "aggregate_name", "version", "schema", "data", "created_at", "updated_at"

    # noinspection PyShadowingBuiltins
    def __init__(
        self,
        aggregate_uuid: UUID,
        aggregate_name: str,
        version: int,
        schema: Optional[Union[list[dict[str, Any]], dict[str, Any]]] = None,
        data: Optional[dict[str, Any]] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        if isinstance(schema, memoryview):
            schema = schema.tobytes()
        if isinstance(schema, bytes):
            schema = MinosJsonBinaryProtocol.decode(schema)

        self.aggregate_uuid = aggregate_uuid
        self.aggregate_name = aggregate_name
        self.version = version

        self.schema = schema
        self.data = data

        self.created_at = created_at
        self.updated_at = updated_at

    @classmethod
    def from_aggregate(cls, aggregate: Aggregate) -> SnapshotEntry:
        """Build a new instance from an ``Aggregate``.

        :param aggregate: The aggregate instance.
        :return: A new ``MinosSnapshotEntry`` instance.
        """
        data = {
            k: v for k, v in aggregate.avro_data.items() if k not in {"uuid", "version", "created_at", "updated_at"}
        }

        # noinspection PyTypeChecker
        return cls(
            aggregate_uuid=aggregate.uuid,
            aggregate_name=aggregate.classname,
            version=aggregate.version,
            schema=aggregate.avro_schema,
            data=data,
            created_at=aggregate.created_at,
            updated_at=aggregate.updated_at,
        )

    @classmethod
    def from_event_entry(cls, entry: RepositoryEntry) -> SnapshotEntry:
        """Build a new ``SnapshotEntry`` from a deletion event.

        :param entry: The repository entry containing the delete information.
        :return: A new ``SnapshotEntry`` instance.
        """
        return cls(
            aggregate_uuid=entry.aggregate_uuid,
            aggregate_name=entry.aggregate_name,
            version=entry.version,
            created_at=entry.created_at,
            updated_at=entry.created_at,
        )

    def as_raw(self) -> dict[str, Any]:
        """Get a raw representation of the instance.

        :return: A dictionary in which the keys are attribute names and values the attribute contents.
        """
        return {
            "aggregate_uuid": self.aggregate_uuid,
            "aggregate_name": self.aggregate_name,
            "version": self.version,
            "schema": self.encoded_schema,
            "data": self.encoded_data,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @property
    def encoded_schema(self) -> Optional[bytes]:
        """Get the encoded schema if available.

        :return: A ``bytes`` instance or ``None``.
        """
        if self.schema is None:
            return None

        return MinosJsonBinaryProtocol.encode(self.schema)

    @property
    def encoded_data(self) -> Optional[str]:
        """ Get the encoded data if available.

        :return: A ``str`` instance or ``None``.
        """
        if self.data is None:
            return None

        return json.dumps(self.data)

    def build_aggregate(self, **kwargs) -> Aggregate:
        """Rebuild the stored ``Aggregate`` object instance from the internal state.

        :param kwargs: Additional named arguments.
        :return: A ``Aggregate`` instance.
        """
        from ..model import (
            Aggregate,
        )

        if self.data is None:
            raise MinosSnapshotDeletedAggregateException(
                f"The {self.aggregate_uuid!r} id points to an already deleted aggregate."
            )
        data = dict(self.data)
        data |= {
            "uuid": self.aggregate_uuid,
            "version": self.version,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
        data |= kwargs
        instance = Aggregate.from_avro(self.schema, data)
        return instance

    @property
    def aggregate_cls(self) -> Type[Aggregate]:
        """Load the concrete ``Aggregate`` class.

        :return: A ``Type`` object.
        """
        # noinspection PyTypeChecker
        return import_module(self.aggregate_name)

    def __eq__(self, other: SnapshotEntry) -> bool:
        return type(self) == type(other) and tuple(self) == tuple(other)

    def __iter__(self) -> Iterable:
        # noinspection PyRedundantParentheses
        yield from (self.aggregate_name, self.version, self.schema, self.data, self.created_at, self.updated_at)

    def __repr__(self):
        name = type(self).__name__
        return (
            f"{name}(aggregate_uuid={self.aggregate_uuid!r}, aggregate_name={self.aggregate_name!r}, "
            f"version={self.version!r}, schema={self.schema!r}, data={self.data!r}, "
            f"created_at={self.created_at!r}, updated_at={self.updated_at!r})"
        )
