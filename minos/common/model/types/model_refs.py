"""
Copyright (C) 2021 Clariteia SL

This file is part of minos framework.

Minos framework can not be copied and/or distributed without the express permission of Clariteia SL.
"""
from __future__ import annotations

from collections import defaultdict
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    Iterable,
    NoReturn,
    Optional,
    Type,
    TypeVar,
    get_args,
    get_origin,
)
from uuid import UUID

T = TypeVar("T")


class ModelRef(Generic[T]):
    """Model Reference."""


if TYPE_CHECKING:
    from ..abc import Model


class ModelRefExtractor:
    """Model Reference Extractor class."""

    def __init__(self, value: Any, kind: Optional[Type] = None):
        if kind is None:
            from .builders import TypeHintBuilder

            kind = TypeHintBuilder(value).build()
        self.value = value
        self.kind = kind

    def build(self) -> dict[str, set[UUID]]:
        """Run the model reference extractor.

        :return: A dictionary in which the keys are the class names and the values are the identifiers.
        """
        ans = defaultdict(set)
        self._build(self.value, self.kind, ans)
        return ans

    def _build(self, value: Any, kind: Type, ans: dict[str, set[UUID]]) -> NoReturn:
        from ..abc import Model

        if isinstance(value, (tuple, list, set)):
            self._build_iterable(value, get_args(kind)[0], ans)

        elif isinstance(value, dict):
            self._build_iterable(value.keys(), get_args(kind)[0], ans)
            self._build_iterable(value.values(), get_args(kind)[1], ans)

        elif isinstance(value, Model):
            for field in value.fields.values():
                self._build(field.value, field.type, ans)

        elif get_origin(kind) is ModelRef and isinstance(value, UUID):
            cls = get_args(kind)[0]
            name = cls.__name__
            ans[name].add(value)

    def _build_iterable(self, value: Iterable, kind: Type, ans: dict[str, set[UUID]]) -> NoReturn:
        for sub_value in value:
            self._build(sub_value, kind, ans)


class ModelRefInjector:
    """TODO"""

    def __init__(self, value: Any, mapper: dict[UUID, Model]):
        self.value = value
        self.mapper = mapper

    def build(self) -> Any:
        """TODO

        :return: TODO
        """
        return self._build(self.value)

    def _build(self, value: Any) -> NoReturn:
        from ..abc import Model

        if isinstance(value, (tuple, list, set)):
            return type(value)(self._build(v) for v in value)

        elif isinstance(value, dict):
            return type(value)((self._build(k), self._build(v)) for k, v in value.items())

        elif isinstance(value, Model):
            for field in value.fields.values():
                field.value = self._build(field.value)
            return value

        elif isinstance(value, UUID) and value in self.mapper:
            return self.mapper[value]

        else:
            return value
