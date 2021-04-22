"""
Copyright (C) 2021 Clariteia SL

This file is part of minos framework.

Minos framework can not be copied and/or distributed without the express permission of Clariteia SL.
"""
import unittest

from minos.common import (
    MinosConfig,
    MinosConfigException,
)
from tests.utils import BASE_PATH


class TestMinosConfig(unittest.TestCase):

    def setUp(self) -> None:
        self.config_file_path = BASE_PATH / "test_config.yaml"

    def test_config_ini_fail(self):
        with self.assertRaises(MinosConfigException):
            MinosConfig(path=BASE_PATH / "test_fail_config.yaml")

    def test_config_service(self):
        config = MinosConfig(path=self.config_file_path)
        service = config.service
        assert service.name == "Order"

    def test_config_rest(self):
        config = MinosConfig(path=self.config_file_path)
        rest = config.rest

        broker = rest.broker
        assert broker.host == "localhost"
        assert broker.port == 8900

        endpoints = rest.endpoints
        assert endpoints[0].name == "AddOrder"

    def test_config_events(self):
        config = MinosConfig(path=self.config_file_path)
        events = config.events
        broker = events.broker
        assert broker.host == "localhost"
        assert broker.port == 9092

    def test_config_events_database(self):
        config = MinosConfig(path=self.config_file_path)
        events = config.events
        database = events.database
        assert database.path == "./tests/local_db.lmdb"
        assert database.name == "database_events_test"

    def test_config_events_queue_database(self):
        config = MinosConfig(path=self.config_file_path)
        events = config.events
        queue = events.queue
        assert queue.database == "broker_db"
        assert queue.user == "broker"
        assert queue.password == "br0k3r"
        assert queue.host == "localhost"
        assert queue.port == 5432
        assert queue.records == 10

    def test_config_commands_database(self):
        config = MinosConfig(path=self.config_file_path)
        commands = config.commands
        database = commands.database
        assert database.path == "./tests/local_db.lmdb"
        assert database.name == "database_commands_test"

    def test_config_commands_queue_database(self):
        config = MinosConfig(path=self.config_file_path)
        commands = config.commands
        queue = commands.queue
        assert queue.database == "broker_db"
        assert queue.user == "broker"
        assert queue.password == "br0k3r"
        assert queue.host == "localhost"
        assert queue.port == 5432
        assert queue.records == 10


if __name__ == "__main__":
    unittest.main()
