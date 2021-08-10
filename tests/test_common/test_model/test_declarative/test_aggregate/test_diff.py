"""
Copyright (C) 2021 Clariteia SL

This file is part of minos framework.

Minos framework can not be copied and/or distributed without the express permission of Clariteia SL.
"""
import unittest
from uuid import (
    uuid4,
)

from minos.common import (
    Action,
    AggregateDiff,
)
from tests.aggregate_classes import (
    Car,
)
from tests.utils import (
    FakeBroker,
    FakeRepository,
    FakeSnapshot,
)


class TestAggregateDiff(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.uuid = uuid4()
        self.uuid_another = uuid4()

        async with FakeBroker() as b, FakeRepository() as r, FakeSnapshot() as s:
            self.initial = Car(3, "blue", uuid=self.uuid, version=1, _broker=b, _repository=r, _snapshot=s)
            self.final = Car(5, "yellow", uuid=self.uuid, version=3, _broker=b, _repository=r, _snapshot=s)
            self.another = Car(3, "blue", uuid=self.uuid_another, version=1, _broker=b, _repository=r, _snapshot=s)

    def test_from_aggregate(self):
        expected = AggregateDiff(
            uuid=self.uuid,
            name=Car.classname,
            version=1,
            action=Action.CREATE,
            differences={"doors": 3, "color": "blue", "owner": None,},
        )
        observed = AggregateDiff.from_aggregate(self.initial)
        self.assertEqual(expected, observed)

    def test_from_deleted_aggregate(self):
        expected = AggregateDiff(uuid=self.uuid, name=Car.classname, version=1, action=Action.DELETE, differences={},)
        observed = AggregateDiff.from_deleted_aggregate(self.initial)
        self.assertEqual(expected, observed)

    def test_from_difference(self):
        expected = AggregateDiff(
            uuid=self.uuid,
            name=Car.classname,
            version=3,
            action=Action.UPDATE,
            differences={"doors": 5, "color": "yellow"},
        )
        observed = AggregateDiff.from_difference(self.final, self.initial)
        self.assertEqual(expected, observed)

    def test_from_difference_raises(self):
        with self.assertRaises(ValueError):
            AggregateDiff.from_difference(self.initial, self.another)

    def test_simplify(self):
        expected = AggregateDiff(
            uuid=self.uuid,
            name=Car.classname,
            version=3,
            action=Action.UPDATE,
            differences={"doors": 5, "color": "red"},
        )

        one = AggregateDiff(self.uuid, Car.classname, 1, Action.UPDATE, {"color": "yellow"})
        two = AggregateDiff(
            uuid=self.uuid,
            name=Car.classname,
            version=2,
            action=Action.UPDATE,
            differences={"doors": 1, "color": "red"},
        )
        three = AggregateDiff(self.uuid, Car.classname, 3, Action.UPDATE, {"doors": 5})
        observed = AggregateDiff.simplify(one, two, three)
        self.assertEqual(expected, observed)

    def test_avro_serialization(self):
        initial = AggregateDiff(
            uuid=self.uuid,
            name=Car.classname,
            version=1,
            action=Action.CREATE,
            differences={"doors": 3, "color": "blue", "owner": None,},
        )

        serialized = initial.avro_bytes
        self.assertIsInstance(serialized, bytes)

        deserialized = AggregateDiff.from_avro_bytes(serialized)
        self.assertEqual(initial, deserialized)

    def test_decompose(self):
        expected = [
            AggregateDiff(
                uuid=self.uuid, name=Car.classname, version=3, action=Action.UPDATE, differences={"doors": 5},
            ),
            AggregateDiff(
                uuid=self.uuid, name=Car.classname, version=3, action=Action.UPDATE, differences={"color": "yellow"},
            ),
        ]

        aggr = AggregateDiff(
            uuid=self.uuid,
            name=Car.classname,
            version=3,
            action=Action.UPDATE,
            differences={"doors": 5, "color": "yellow"},
        )
        observed = aggr.decompose()
        self.assertEqual(expected, observed)


if __name__ == "__main__":
    unittest.main()
