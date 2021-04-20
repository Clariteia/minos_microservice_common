"""
Copyright (C) 2021 Clariteia SL

This file is part of minos framework.

Minos framework can not be copied and/or distributed without the express permission of Clariteia SL.
"""
import typing as t
from itertools import (
    zip_longest,
)

from ...exceptions import (
    EmptyMinosModelSequenceException,
    MinosModelException,
    MultiTypeMinosModelSequenceException,
)
from ...logs import (
    log,
)
from ...protocol import (
    MinosAvroValuesDatabase,
)
from .fields import (
    ModelField,
)
from .types import (
    MissingSentinel,
)

# def _process_aggregate(cls):
#     """
#     Get the list of the class arguments and define it as an AggregateField class
#     """
#     cls_annotations = cls.__dict__.get('__annotations__', {})
#     aggregate_fields = []
#     for name, type in cls_annotations.items():
#         attribute = getattr(cls, name, None)
#         aggregate_fields.append(
#             AggregateField(name=name, type=type, value=attribute)
#         )
#     setattr(cls, "_FIELDS", aggregate_fields)
#
#     # g get metaclass
#     meta_class = getattr(cls, "Meta", None)
#     if meta_class:
#         # meta class exist so get the information related
#         ...
#     return cls
#
#
# def aggregate(cls=None):
#     def wrap(cls):
#         return _process_aggregate(cls)
#
#     if cls is None:
#         return wrap
#
#     return wrap(cls)


class MinosModel(object):
    """Base class for ``minos`` model entities."""

    _fields: dict[str, ModelField] = {}

    def __init__(self, *args, **kwargs):
        """Class constructor.

        :param kwargs: Named arguments to be set as model attributes.
        """
        self._fields = dict()
        self._list_fields(*args, **kwargs)

    @classmethod
    def from_avro_bytes(cls, raw: bytes) -> t.Union["MinosModel", list["MinosModel"]]:
        """Build a single instance or a sequence of instances from bytes

        :param raw: A bytes data.
        :return: A single instance or a sequence of instances.
        """

        decoded = MinosAvroValuesDatabase().decode(raw, content_root=False)
        if isinstance(decoded, list):
            return [cls.from_dict(d) for d in decoded]
        return cls.from_dict(decoded)

    @classmethod
    def from_dict(cls, d: dict[str, t.Any]) -> "MinosModel":
        """Build a new instance from a dictionary.

        :param d: A dictionary object.
        :return: A new ``MinosModel`` instance.
        """
        return cls(**d)

    @classmethod
    def to_avro_bytes(cls, models: list["MinosModel"]) -> bytes:
        """Create a bytes representation of the given object instances.

        :param models: A sequence of minos models.
        :return: A bytes object.
        """
        if len(models) == 0:
            raise EmptyMinosModelSequenceException("'models' parameter cannot be empty.")

        model_type = type(models[0])
        if not all(model_type == type(model) for model in models):
            raise MultiTypeMinosModelSequenceException(
                f"Every model must have type {model_type} to be valid. Found types: {[type(model) for model in models]}"
            )

        avro_schema = models[0].avro_schema
        return MinosAvroValuesDatabase().encode([model.avro_data for model in models], avro_schema)

    @property
    def fields(self) -> dict[str, ModelField]:
        """Fields getter"""
        return self._fields

    def __setattr__(self, key: str, value: t.Any) -> t.NoReturn:
        if self._fields is not None and key in self._fields:
            field_class: ModelField = self._fields[key]
            field_class.value = value
            self._fields[key] = field_class
        elif key.startswith("_"):
            super().__setattr__(key, value)
        else:
            raise MinosModelException(f"model attribute {key} doesn't exist")

    def __getattr__(self, item: str) -> t.Any:
        if self._fields is not None and item in self._fields:
            return self._fields[item].value
        else:
            raise AttributeError

    def _list_fields(self, *args, **kwargs) -> t.NoReturn:
        fields: dict[str, t.Any] = t.get_type_hints(self)
        fields = self._update_from_inherited_class(fields)

        empty = MissingSentinel  # artificial value to discriminate between None and empty.
        for (name, type_val), value in zip_longest(fields.items(), args, fillvalue=empty):
            if name in kwargs and value is not empty:
                raise TypeError(f"got multiple values for argument {repr(name)}")

            if value is empty:
                value = kwargs.get(name, MissingSentinel)

            self._fields[name] = ModelField(
                name, type_val, value, getattr(self, f"parse_{name}", None), getattr(self, f"validate_{name}", None)
            )

    def _update_from_inherited_class(self, fields: dict[str, t.Any]) -> dict[str, t.Any]:
        """
        get all the child class __annotations__ and update the FIELD base attribute
        """
        ans = dict()
        for b in self.__class__.__mro__[-1:0:-1]:
            base_fields = getattr(b, "_fields", None)
            if base_fields is not None:
                list_fields = t.get_type_hints(b)
                list_fields.pop("_fields")
                log.debug(f"Fields Derivative {list_fields}")
                if "_fields" not in list_fields:
                    # the class is a derivative of MinosModel class
                    ans |= list_fields
        ans |= fields
        return ans

    @property
    def avro_schema(self) -> dict[str, t.Any]:
        """Compute the avro schema of the model.

        :return: A dictionary object.
        """
        fields = [field.avro_schema for field in self.fields.values()]
        return {"name": type(self).__name__, "namespace": type(self).__module__, "type": "record", "fields": fields}

    @property
    def avro_data(self) -> t.Any:
        """Compute the avro data of the model.

        :return: A dictionary object.
        """
        return {name: field.avro_data for name, field in self.fields.items()}

    @property
    def avro_bytes(self) -> bytes:
        """Generate bytes representation of the current instance.

        :return: A bytes object.
        """
        return MinosAvroValuesDatabase().encode(self.avro_data, self.avro_schema)

    def __eq__(self, other: "MinosModel") -> bool:
        return type(self) == type(other) and tuple(self) == tuple(other)

    def __hash__(self) -> int:
        return hash(tuple(self))

    def __iter__(self) -> t.Iterable:
        # noinspection PyRedundantParentheses
        yield from self.fields.items()

    def __repr__(self):
        fields_repr = ", ".join(repr(field) for field in self.fields.values())
        return f"{type(self).__name__}(fields=[{fields_repr}])"