"""
Copyright (C) 2021 Clariteia SL

This file is part of minos framework.

Minos framework can not be copied and/or distributed without the express permission of Clariteia SL.
"""
import unittest

from minos.common import (
    MinosSnapshotDeletedAggregateException,
    PostgreSqlRepository,
    PostgreSqlSnapshot,
)
from minos.common.testing import (
    PostgresAsyncTestCase,
)
from tests.aggregate_classes import (
    Car,
)
from tests.utils import (
    BASE_PATH,
    FakeBroker,
)


class TestAggregateWithPostgreSql(PostgresAsyncTestCase):
    CONFIG_FILE_PATH = BASE_PATH / "test_config.yml"

    async def asyncSetUp(self):
        await super().asyncSetUp()
        self.event_broker = FakeBroker()
        self.repository = PostgreSqlRepository.from_config(config=self.config)
        self.snapshot = PostgreSqlSnapshot.from_config(config=self.config, repository=self.repository)

        self.kwargs = {
            "_broker": self.event_broker,
            "_repository": self.repository,
            "_snapshot": self.snapshot,
        }

    async def test_update(self):
        async with self.event_broker, self.repository, self.snapshot:
            car = await Car.create(doors=3, color="blue", **self.kwargs)
            uuid = car.uuid

            await car.update(color="red")
            self.assertEqual(Car(3, "red", uuid=uuid, version=2, **self.kwargs), car)
            self.assertEqual(car, await Car.get_one(car.uuid, **self.kwargs))

            await car.update(doors=5)
            self.assertEqual(Car(5, "red", uuid=uuid, version=3, **self.kwargs), car)
            self.assertEqual(car, await Car.get_one(car.uuid, **self.kwargs))

            await car.delete()
            with self.assertRaises(MinosSnapshotDeletedAggregateException):
                await Car.get_one(car.uuid, **self.kwargs)

            car = await Car.create(doors=3, color="blue", **self.kwargs)
            uuid = car.uuid

            await car.update(color="red")
            self.assertEqual(
                Car(3, "red", uuid=uuid, version=2, **self.kwargs), await Car.get_one(car.uuid, **self.kwargs)
            )

            await car.delete()
            with self.assertRaises(MinosSnapshotDeletedAggregateException):
                await Car.get_one(car.uuid, **self.kwargs)


if __name__ == "__main__":
    unittest.main()