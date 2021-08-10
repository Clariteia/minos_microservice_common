"""
Copyright (C) 2021 Clariteia SL

This file is part of minos framework.

Minos framework can not be copied and/or distributed without the express permission of Clariteia SL.
"""

__version__ = "0.1.8"

from .configuration import (
    BROKER,
    COMMANDS,
    CONTROLLER,
    DISCOVERY,
    EVENTS,
    QUEUE,
    REPOSITORY,
    REST,
    SAGA,
    SERVICE,
    SNAPSHOT,
    STORAGE,
    MinosConfig,
    MinosConfigAbstract,
)
from .constants import (
    NULL_UUID,
    UUID_REGEX,
)
from .database import (
    PostgreSqlMinosDatabase,
    PostgreSqlPool,
)
from .exceptions import (
    EmptyMinosModelSequenceException,
    MinosAttributeValidationException,
    MinosBrokerException,
    MinosBrokerNotProvidedException,
    MinosConfigException,
    MinosConfigNotProvidedException,
    MinosException,
    MinosHandlerException,
    MinosHandlerNotProvidedException,
    MinosImmutableClassException,
    MinosImportException,
    MinosMalformedAttributeException,
    MinosMessageException,
    MinosModelAttributeException,
    MinosModelException,
    MinosParseAttributeException,
    MinosPreviousVersionSnapshotException,
    MinosProtocolException,
    MinosRepositoryException,
    MinosRepositoryManuallySetAggregateIdentifierException,
    MinosRepositoryManuallySetAggregateVersionException,
    MinosRepositoryNotProvidedException,
    MinosReqAttributeException,
    MinosSagaManagerException,
    MinosSagaManagerNotProvidedException,
    MinosSnapshotAggregateNotFoundException,
    MinosSnapshotDeletedAggregateException,
    MinosSnapshotException,
    MinosSnapshotNotProvidedException,
    MinosTypeAttributeException,
    MultiTypeMinosModelSequenceException,
)
from .importlib import (
    classname,
    import_module,
)
from .injectors import (
    DependencyInjector,
)
from .launchers import (
    EntrypointLauncher,
)
from .meta import (
    classproperty,
    property_or_classproperty,
    self_or_classmethod,
)
from .model import (
    Action,
    Aggregate,
    AggregateDiff,
    AggregateRef,
    AvroDataDecoder,
    AvroDataEncoder,
    AvroSchemaDecoder,
    AvroSchemaEncoder,
    BucketModel,
    Command,
    CommandReply,
    CommandStatus,
    DataTransferObject,
    Decimal,
    DeclarativeModel,
    DynamicModel,
    Entity,
    EntitySet,
    Enum,
    Event,
    Field,
    FieldsDiff,
    Fixed,
    MinosModel,
    MissingSentinel,
    Model,
    ModelField,
    ModelRef,
    ModelRefExtractor,
    ModelRefInjector,
    ModelType,
    NoneType,
    TypeHintBuilder,
    TypeHintComparator,
    ValueObject,
)
from .networks import (
    MinosBroker,
    MinosHandler,
)
from .pools import (
    MinosPool,
)
from .protocol import (
    MinosAvroDatabaseProtocol,
    MinosAvroMessageProtocol,
    MinosAvroProtocol,
    MinosBinaryProtocol,
    MinosJsonBinaryProtocol,
)
from .repository import (
    InMemoryRepository,
    MinosRepository,
    PostgreSqlRepository,
    RepositoryEntry,
)
from .saga import (
    MinosSagaManager,
)
from .setup import (
    MinosSetup,
)
from .snapshot import (
    InMemorySnapshot,
    MinosSnapshot,
    PostgreSqlSnapshot,
    PostgreSqlSnapshotBuilder,
    PostgreSqlSnapshotSetup,
    SnapshotEntry,
)
from .storage import (
    MinosStorage,
    MinosStorageLmdb,
)
