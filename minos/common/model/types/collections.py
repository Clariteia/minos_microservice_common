"""
Copyright (C) 2021 Clariteia SL

This file is part of minos framework.

Minos framework can not be copied and/or distributed without the express permission of Clariteia SL.
"""
from collections.abc import (
    MutableMapping,
    MutableSequence,
)
from typing import (
    Generic,
    Iterable,
    Iterator,
    NoReturn,
    TypeVar,
)

T = TypeVar("T")


class ObservableList(MutableSequence, Generic[T]):
    """TODO"""

    def __init__(self, values: Iterable[T] = None):
        if values is None:
            values = tuple()
        self._events = [("add", i, value) for i, value in enumerate(values)]
        self._data = list(values)

    def insert(self, index: int, value: T) -> NoReturn:
        """TODO

        :param index: TODO
        :param value: TODO
        :return: TODO
        """
        self._events.append(("add", index, value))
        self._data.insert(index, value)

    def __getitem__(self, item: int) -> T:
        return self._data[item]

    def __setitem__(self, key: int, value: T):
        self._events.append(("update", key, value))
        self._data[key] = value

    def __delitem__(self, key: int) -> NoReturn:
        self._events.append(("delete", key % len(self), None))
        del self._data[key]

    def __len__(self) -> int:
        return len(self._data)

    def get_modifications(self):
        return self._events

    def __repr__(self):
        return f"{type(self).__name__}({self._data!r})"

    def __eq__(self, other):
        return self._data == other


K = TypeVar("K")
V = TypeVar("V")


class ObservableDict(MutableMapping, Generic[K, V]):
    """TODO"""

    def __init__(self, values: Iterable = None):
        if values is None:
            values = tuple()
        self._data = dict(values)

    def __setitem__(self, k: K, v: V) -> NoReturn:
        self._data[k] = v

    def __delitem__(self, key: K) -> NoReturn:
        del self._data[key]

    def __getitem__(self, key: K) -> V:
        return self._data[key]

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[K]:
        yield from self._data
