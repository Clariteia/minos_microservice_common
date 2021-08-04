"""
Copyright (C) 2021 Clariteia SL

This file is part of minos framework.

Minos framework can not be copied and/or distributed without the express permission of Clariteia SL.
"""

import unittest
from typing import (
    TypedDict,
)

from minos.common import (
    DataTransferObject,
    Field,
    MinosReqAttributeException,
    ModelType,
)
from tests.model_classes import (
    Foo,
)


class TestModelType(unittest.TestCase):
    def test_build(self):
        model_type = ModelType.build("Foo", {"text": int}, "bar")
        self.assertEqual("Foo", model_type.name)
        self.assertEqual({"text": int}, model_type.type_hints)
        self.assertEqual("bar", model_type.namespace)

    def test_classname(self):
        model_type = ModelType.build("Foo", {"text": int}, "bar")
        self.assertEqual("bar.Foo", model_type.classname)

    def test_hash(self):
        model_type = ModelType.build("Foo", {"text": int}, "bar")
        self.assertIsInstance(hash(model_type), int)

    def test_equal(self):
        one = ModelType.build("Foo", {"text": int}, "bar")
        two = ModelType.build("Foo", {"text": int}, "bar")
        self.assertEqual(one, two)

    def test_equal_declarative(self):
        one = ModelType.build("tests.model_classes.Foo", {"text": str})
        self.assertEqual(one, Foo)

    def test_not_equal(self):
        base = ModelType.build("Foo", {"text": int}, "bar")
        self.assertNotEqual(ModelType.build("aaa", {"text": int}, "bar"), base)
        self.assertNotEqual(ModelType.build("Foo", {"aaa": float}, "bar"), base)
        self.assertNotEqual(ModelType.build("Foo", {"text": int}, "aaa"), base)

    def test_from_typed_dict(self):
        expected = ModelType.build("Foo", {"text": int}, "bar")
        observed = ModelType.from_typed_dict(TypedDict("bar.Foo", {"text": int}))
        self.assertEqual(expected, observed)

    def test_from_typed_dict_without_namespace(self):
        expected = ModelType.build("Foo", {"text": int})
        observed = ModelType.from_typed_dict(TypedDict("Foo", {"text": int}))
        self.assertEqual(expected, observed)

    def test_call_declarative_model(self):
        model_type = ModelType.build("tests.model_classes.Foo", {"text": str})
        dto = model_type(text="test")
        self.assertEqual(Foo("test"), dto)

    def test_call_declarative_model_raises(self):
        model_type = ModelType.build("tests.model_classes.Foo", {"bar": str})
        with self.assertRaises(MinosReqAttributeException):
            model_type(bar="test")

    def test_call_dto_model(self):
        model_type = ModelType.build("Foo", {"text": str})
        dto = model_type(text="test")
        self.assertEqual(DataTransferObject("Foo", [Field("text", str, "test")]), dto)


if __name__ == "__main__":
    unittest.main()