"""
Copyright (C) 2021 Clariteia SL

This file is part of minos framework.

Minos framework can not be copied and/or distributed without the express permission of Clariteia SL.
"""
import unittest

from minos.common import (
    ObservableList,
)


class TestObservableList(unittest.TestCase):
    def test_events(self):
        data = ObservableList([1, 2, 3, 4])
        data.insert(3, 5)
        data.pop()
        data[0] = 32
        del data[1]

        observed = data.get_modifications()

        expected = [
            ("add", 0, 1),
            ("add", 1, 2),
            ("add", 2, 3),
            ("add", 3, 4),
            ("add", 3, 5),
            ("delete", 4, None),
            ("update", 0, 32),
            ("delete", 1, None),
        ]
        self.assertEqual(expected, observed)
        self.assertEqual([32, 3, 5], data)


class TestObservableDict(unittest.TestCase):
    def test_insert(self):
        pass


if __name__ == "__main__":
    unittest.main()
