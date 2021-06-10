"""
Copyright (C) 2021 Clariteia SL

This file is part of minos framework.

Minos framework can not be copied and/or distributed without the express permission of Clariteia SL.
"""
from __future__ import (
    annotations,
)

import logging
import typing as t
from datetime import (
    date,
    datetime,
    time,
)
from uuid import (
    UUID,
)

from minos.common.exceptions import (
    MinosMalformedAttributeException,
)
from minos.common.model.abc.types import (
    ARRAY,
    BOOLEAN,
    BYTES,
    DATE_TYPE,
    DATETIME_TYPE,
    FLOAT,
    INT,
    MAP,
    NULL,
    STRING,
    TIME_TYPE,
    UUID_TYPE,
)

logger = logging.getLogger(__name__)

T = t.TypeVar("T")


class MinosModelFromAvroBuilder(object):
    def __init__(self, schema: dict):
        self._schema = schema

    def build(self) -> t.Type[T]:
        """Build type from given avro schema item.

        :return: A dictionary object.
        """
        built_type = self._build_type(self._schema)
        return built_type

    def _build_type(self, schema: t.Union[dict, list, str]) -> t.Type[T]:
        if isinstance(schema, dict):
            return self._build_type_from_dict(schema)
        elif isinstance(schema, list):
            return self._build_type_from_list(schema)
        else:
            return self._build_simple_type(schema)

    def _build_type_from_list(self, schema: list[t.Any]) -> t.Type[T]:
        options = tuple(self._build_type(entry) for entry in schema)
        return t.Union[options]

    def _build_type_from_dict(self, schema: dict) -> t.Type[T]:
        if "logicalType" in schema:
            return self._build_logical_type(schema["logicalType"])
        elif schema["type"] == ARRAY:
            return self._build_list_type(schema["items"])
        elif schema["type"] == MAP:
            return self._build_dict_type(schema["values"])
        else:
            return self._build_type(schema["type"])

    @staticmethod
    def _build_logical_type(type_field: str) -> t.Type[T]:
        if type_field == DATE_TYPE["logicalType"]:
            return date
        if type_field == TIME_TYPE["logicalType"]:
            return time
        if type_field == DATETIME_TYPE["logicalType"]:
            return datetime
        if type_field == UUID_TYPE["logicalType"]:
            return UUID
        raise MinosMalformedAttributeException(f"Given logical field type is not supported: {type_field!r}")

    def _build_list_type(self, items: t.Union[dict, str, t.Any] = None) -> t.Type[T]:
        return list[self._build_type(items)]

    def _build_dict_type(self, values: t.Union[dict, str, t.Any] = None) -> t.Type[T]:
        return dict[str, self._build_type(values)]

    @staticmethod
    def _build_simple_type(type_field: str) -> t.Type[T]:
        if type_field == NULL:
            return type(None)
        if type_field == INT:
            return int
        if type_field == BOOLEAN:
            return bool
        if type_field == FLOAT:
            return float
        if type_field == STRING:
            return str
        if type_field == BYTES:
            return bytes

        raise MinosMalformedAttributeException(f"Given field type is not supported: {type_field!r}")