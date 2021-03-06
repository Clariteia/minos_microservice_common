"""
Copyright (C) 2021 Clariteia SL

This file is part of minos framework.

Minos framework can not be copied and/or distributed without the express permission of Clariteia SL.
"""
import sys
import unittest
from datetime import (
    datetime,
)
from uuid import (
    uuid4,
)

from dependency_injector import (
    containers,
    providers,
)

from minos.common import (
    FieldDiff,
    FieldDiffContainer,
    MinosConfigException,
    MinosSnapshotAggregateNotFoundException,
    MinosSnapshotDeletedAggregateException,
    PostgreSqlRepository,
    PostgreSqlSnapshot,
    PostgreSqlSnapshotBuilder,
    PostgreSqlSnapshotSetup,
    RepositoryEntry,
    SnapshotEntry,
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
    FakeRepository,
    FakeSnapshot,
)


class TestPostgreSqlSnapshot(PostgresAsyncTestCase):
    CONFIG_FILE_PATH = BASE_PATH / "test_config.yml"

    def setUp(self) -> None:
        super().setUp()

        self.uuid_1 = uuid4()
        self.uuid_2 = uuid4()
        self.uuid_3 = uuid4()

        self.container = containers.DynamicContainer()
        self.container.event_broker = providers.Singleton(FakeBroker)
        self.container.repository = providers.Singleton(FakeRepository)
        self.container.snapshot = providers.Singleton(FakeSnapshot)
        self.container.wire(modules=[sys.modules[__name__]])

    def tearDown(self) -> None:
        self.container.unwire()
        super().tearDown()

    def test_type(self):
        self.assertTrue(issubclass(PostgreSqlSnapshot, PostgreSqlSnapshotSetup))

    def test_from_config(self):
        reader = PostgreSqlSnapshot.from_config(config=self.config)
        self.assertEqual(self.config.snapshot.host, reader.host)
        self.assertEqual(self.config.snapshot.port, reader.port)
        self.assertEqual(self.config.snapshot.database, reader.database)
        self.assertEqual(self.config.snapshot.user, reader.user)
        self.assertEqual(self.config.snapshot.password, reader.password)

    def test_from_config_raises(self):
        with self.assertRaises(MinosConfigException):
            PostgreSqlSnapshot.from_config()

    async def test_get(self):
        async with await self._populate() as repository:
            async with PostgreSqlSnapshot.from_config(config=self.config, repository=repository) as snapshot:
                iterable = snapshot.get("tests.aggregate_classes.Car", {self.uuid_2, self.uuid_3})
                observed = [v async for v in iterable]

        expected = [
            Car(
                3,
                "blue",
                uuid=self.uuid_2,
                version=2,
                created_at=observed[0].created_at,
                updated_at=observed[0].updated_at,
            ),
            Car(
                3,
                "blue",
                uuid=self.uuid_3,
                version=1,
                created_at=observed[1].created_at,
                updated_at=observed[1].updated_at,
            ),
        ]
        self.assertEqual(expected, observed)

    async def test_get_streaming_true(self):
        async with await self._populate() as repository:
            async with PostgreSqlSnapshot.from_config(config=self.config, repository=repository) as snapshot:
                iterable = snapshot.get("tests.aggregate_classes.Car", {self.uuid_2, self.uuid_3}, streaming_mode=True)
                observed = [v async for v in iterable]

        expected = [
            Car(
                3,
                "blue",
                uuid=self.uuid_2,
                version=2,
                created_at=observed[0].created_at,
                updated_at=observed[0].updated_at,
            ),
            Car(
                3,
                "blue",
                uuid=self.uuid_3,
                version=1,
                created_at=observed[1].created_at,
                updated_at=observed[1].updated_at,
            ),
        ]
        self.assertEqual(expected, observed)

    async def test_get_with_duplicates(self):
        uuids = [self.uuid_2, self.uuid_2, self.uuid_3]
        async with await self._populate() as repository:
            async with PostgreSqlSnapshot.from_config(config=self.config, repository=repository) as snapshot:
                iterable = snapshot.get("tests.aggregate_classes.Car", uuids)
                observed = [v async for v in iterable]

            expected = [
                Car(
                    3,
                    "blue",
                    uuid=self.uuid_2,
                    version=2,
                    created_at=observed[0].created_at,
                    updated_at=observed[0].updated_at,
                ),
                Car(
                    3,
                    "blue",
                    uuid=self.uuid_3,
                    version=1,
                    created_at=observed[1].created_at,
                    updated_at=observed[1].updated_at,
                ),
            ]
            self.assertEqual(expected, observed)

    async def test_get_empty(self):
        async with await self._populate() as repository:
            async with PostgreSqlSnapshot.from_config(config=self.config, repository=repository) as snapshot:
                observed = {v async for v in snapshot.get("tests.aggregate_classes.Car", set())}

        expected = set()
        self.assertEqual(expected, observed)

    async def test_get_raises(self):
        async with await self._populate() as repository:
            async with PostgreSqlSnapshot.from_config(config=self.config, repository=repository) as snapshot:
                with self.assertRaises(MinosSnapshotDeletedAggregateException):
                    # noinspection PyStatementEffect
                    {v async for v in snapshot.get("tests.aggregate_classes.Car", {self.uuid_1})}
                with self.assertRaises(MinosSnapshotAggregateNotFoundException):
                    # noinspection PyStatementEffect
                    {v async for v in snapshot.get("tests.aggregate_classes.Car", {uuid4()})}

    async def test_select(self):
        await self._populate()

        async with PostgreSqlSnapshot.from_config(config=self.config) as snapshot:
            observed = [v async for v in snapshot.select()]

        # noinspection PyTypeChecker
        expected = [
            SnapshotEntry(self.uuid_1, Car.classname, 4),
            SnapshotEntry.from_aggregate(
                Car(
                    3,
                    "blue",
                    uuid=self.uuid_2,
                    version=2,
                    created_at=observed[1].created_at,
                    updated_at=observed[1].updated_at,
                )
            ),
            SnapshotEntry.from_aggregate(
                Car(
                    3,
                    "blue",
                    uuid=self.uuid_3,
                    version=1,
                    created_at=observed[2].created_at,
                    updated_at=observed[2].updated_at,
                )
            ),
        ]
        self._assert_equal_snapshot_entries(expected, observed)

    def _assert_equal_snapshot_entries(self, expected: list[SnapshotEntry], observed: list[SnapshotEntry]):
        self.assertEqual(len(expected), len(observed))
        for exp, obs in zip(expected, observed):
            if exp.data is None:
                with self.assertRaises(MinosSnapshotDeletedAggregateException):
                    # noinspection PyStatementEffect
                    obs.build_aggregate()
            else:
                self.assertEqual(exp.build_aggregate(), obs.build_aggregate())
            self.assertIsInstance(obs.created_at, datetime)
            self.assertIsInstance(obs.updated_at, datetime)

    async def _populate(self):
        diff = FieldDiffContainer([FieldDiff("doors", int, 3), FieldDiff("color", str, "blue")])
        # noinspection PyTypeChecker
        aggregate_name: str = Car.classname
        async with PostgreSqlRepository.from_config(config=self.config) as repository:
            await repository.create(RepositoryEntry(self.uuid_1, aggregate_name, 1, diff.avro_bytes))
            await repository.update(RepositoryEntry(self.uuid_1, aggregate_name, 2, diff.avro_bytes))
            await repository.create(RepositoryEntry(self.uuid_2, aggregate_name, 1, diff.avro_bytes))
            await repository.update(RepositoryEntry(self.uuid_1, aggregate_name, 3, diff.avro_bytes))
            await repository.delete(RepositoryEntry(self.uuid_1, aggregate_name, 4))
            await repository.update(RepositoryEntry(self.uuid_2, aggregate_name, 2, diff.avro_bytes))
            await repository.create(RepositoryEntry(self.uuid_3, aggregate_name, 1, diff.avro_bytes))
            async with PostgreSqlSnapshotBuilder.from_config(config=self.config, repository=repository) as dispatcher:
                await dispatcher.dispatch()
            return repository


if __name__ == "__main__":
    unittest.main()
