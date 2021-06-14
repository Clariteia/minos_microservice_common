"""
Copyright (C) 2021 Clariteia SL

This file is part of minos framework.

Minos framework can not be copied and/or distributed without the express permission of Clariteia SL.
"""
from __future__ import (
    annotations,
)

from typing import (
    Any,
    Optional,
    TypedDict,
    Union,
)

from ...exceptions import (
    MinosImportException,
)
from ...importlib import (
    import_module,
)
from .. import (
    Model,
)
from ..fields import (
    ModelField,
)
from .abc import (
    DynamicModel,
)


class DataTransferObject(DynamicModel):
    """Data Transfer Object to build the objects dynamically from bytes """

    def __init__(self, name: str, namespace: Optional[str] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if namespace is None:
            try:
                namespace, name = name.rsplit(".", 1)
            except ValueError:
                pass
        self._name = name
        self._namespace = namespace

    @classmethod
    def from_avro(cls, schema: Union[dict[str, Any], list[dict[str, Any]]], data: dict[str, Any]):
        """Build a new instance from the ``avro`` schema and data.

        :param schema: The avro schema of the model.
        :param data: The avro data of the model.
        :return: A new ``DynamicModel`` instance.
        """
        if isinstance(schema, list):
            schema = schema[-1]

        if "namespace" in schema:
            name = "{namespace:}.{name:}".format(**schema)
        else:
            name = schema["name"]

        try:
            # noinspection PyTypeChecker
            model_cls: Model = import_module(name)
        except MinosImportException:
            return super().from_avro(schema, data)

        return model_cls.from_dict(data)

    @classmethod
    def from_typed_dict(cls, typed_dict: TypedDict, data: dict[str, Any]) -> DataTransferObject:
        """Build Model Fields form TypeDict object

        :param typed_dict: TypeDict object
        :param data: Data
        :return: DataTransferObject
        """

        try:
            # noinspection PyTypeChecker
            model_cls: Model = import_module(typed_dict.__name__)
            return model_cls.from_dict(data)
        except MinosImportException:
            pass

        try:
            namespace, name = typed_dict.__name__.rsplit(".", 1)
        except ValueError:
            namespace, name = None, typed_dict.__name__

        fields = {k: ModelField(k, v, data[k]) for k, v in typed_dict.__annotations__.items()}
        return cls(name, namespace, fields)

    # noinspection PyMethodParameters
    @property
    def _avro_name(self) -> str:
        return self._name

    @property
    def _avro_namespace(self) -> Optional[str]:
        return self._namespace

    @property
    def classname(self) -> str:
        """Compute the current class name.

        :return: An string object.
        """
        name = self._name
        if self._namespace is not None:
            name = f"{self._namespace}.{name}"
        return name

    def __repr__(self) -> str:
        fields_repr = ", ".join(repr(field) for field in self.fields.values())
        s = f"{self._name}[DTO](fields=[{fields_repr}])"
        if self._namespace is not None:
            s = f"{self._namespace}.{s}"
        return s

    def __eq__(self, other: DataTransferObject):
        return (
            super(DynamicModel, self).__eq__(other)
            and self._name == other._name
            and self._namespace == other._namespace
        )
