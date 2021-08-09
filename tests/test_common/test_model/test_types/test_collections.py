"""
Copyright (C) 2021 Clariteia SL

This file is part of minos framework.

Minos framework can not be copied and/or distributed without the express permission of Clariteia SL.
"""
from __future__ import (
    annotations,
)

import unittest

from minos.common import (
    ModelType,
    ObservableList,
)

Foo = ModelType.build("Product", {"number": int})


class TestObservableList(unittest.TestCase):
    def test_append(self):
        data = ObservableList([Foo(1), Foo(2), Foo(3), Foo(4)])
        data.flush_modifications()

        data.append(Foo(32))
        data.append(Foo(12))

        observed = data.get_modifications()

        expected = {
            4: ("add", Foo(32)),
            5: ("add", Foo(12)),
        }

        self.assertEqual(expected, observed)

    def test_updated(self):
        data = ObservableList([Foo(1), Foo(2), Foo(3), Foo(4)])
        data.flush_modifications()

        data[0] = Foo(32)

        observed = data.get_modifications()

        expected = {0: ("update", Foo(32))}

        self.assertEqual(expected, observed)

    def test_inserted(self):
        data = ObservableList([Foo(1), Foo(2), Foo(3), Foo(4)])
        data.flush_modifications()

        data.insert(1, Foo(5))

        observed = data.get_modifications()

        expected = {
            1: ("update", Foo(5)),
            2: ("update", Foo(2)),
            3: ("update", Foo(3)),
            4: ("add", Foo(4)),
        }

        self.assertEqual(expected, observed)

    def test_deleted(self):
        data = ObservableList([Foo(1), Foo(2), Foo(3), Foo(4)])
        data.flush_modifications()

        del data[0]

        observed = data.get_modifications()

        expected = {
            0: ("update", Foo(2)),
            1: ("update", Foo(3)),
            2: ("update", Foo(4)),
            3: ("delete", None),
        }

        self.assertEqual(expected, observed)


class TestObservableDict(unittest.TestCase):
    def test_insert(self):
        pass


if __name__ == "__main__":
    unittest.main()
