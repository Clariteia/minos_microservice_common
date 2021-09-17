from __future__ import (
    annotations,
)

from enum import (
    IntEnum,
)
from typing import (
    Any,
    Optional,
)
from uuid import (
    UUID,
)

from .abc import (
    DeclarativeModel,
)
from .aggregate import (
    AggregateDiff,
)


class Command(DeclarativeModel):
    """Base Command class."""

    topic: str
    data: Any
    saga: UUID
    reply_topic: str
    user: Optional[UUID]


class CommandReply(DeclarativeModel):
    """Base Command class."""

    topic: str
    data: Any
    saga: UUID
    status: CommandStatus


class CommandStatus(IntEnum):
    """Command Status class."""

    SUCCESS = 200
    ERROR = 400
    SYSTEM_ERROR = 500


class Event(DeclarativeModel):
    """Base Event class."""

    topic: str
    data: AggregateDiff
