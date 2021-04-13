import unittest
from typing import Optional, Union, List, Dict

from minos.common import ModelField, MinosModelAttributeException, ModelRef
from tests.modelClasses import User


class TestModelField(unittest.TestCase):

    def test_name(self):
        field = ModelField("test", int, 3)
        self.assertEqual("test", field.name)

    def test_type(self):
        field = ModelField("test", int, 3)
        self.assertEqual(int, field.type)

    def test_value_int(self):
        field = ModelField("test", int, 3)
        self.assertEqual(3, field.value)

    def test_value_list(self):
        field = ModelField("test", list[int], [1, 2, 3])
        self.assertEqual([1, 2, 3], field.value)

    def test_value_dict(self):
        field = ModelField("test", dict[str, bool], {"foo": True, "bar": False})
        self.assertEqual({"foo": True, "bar": False}, field.value)

    def test_value_model_ref(self):
        user = User()
        field = ModelField("test", ModelRef[User], user)
        self.assertEqual(user, field.value)

    def test_value_model_ref_raises(self):
        with self.assertRaises(MinosModelAttributeException):
            ModelField("test", ModelRef[User], "foo")

    def test_value_model_ref_optional(self):
        field = ModelField("test", Optional[ModelRef[User]], None)
        self.assertIsNone(field.value)

        user = User()
        field.value = user
        self.assertEqual(user, field.value)

    def test_value_setter(self):
        field = ModelField("test", int, 3)
        field.value = 3
        self.assertEqual(3, field.value)

    def test_value_setter_raises(self):
        field = ModelField("test", int, 3)
        with self.assertRaises(MinosModelAttributeException):
            field.value = None

    def test_value_setter_dict(self):
        field = ModelField("test", dict[str, bool], {})
        field.value = {"foo": True, "bar": False}
        self.assertEqual({"foo": True, "bar": False}, field.value)

    def test_value_setter_dict_raises(self):
        field = ModelField("test", dict[str, bool], {})
        with self.assertRaises(MinosModelAttributeException):
            field.value = "foo"
        with self.assertRaises(MinosModelAttributeException):
            field.value = {"foo": 1, "bar": 2}
        with self.assertRaises(MinosModelAttributeException):
            field.value = {1: True, 2: False}

    def test_optional_type(self):
        field = ModelField("test", Optional[int], None)
        self.assertEqual(Optional[int], field.type)

    def test_value_setter_optional_int(self):
        field = ModelField("test", Optional[int], 3)
        self.assertEqual(3, field.value)
        field.value = None
        self.assertEqual(None, field.value)
        field.value = 4
        self.assertEqual(4, field.value)

    def test_value_setter_optional_list(self):
        field = ModelField("test", Optional[List[int]], [1, 2, 3])
        self.assertEqual([1, 2, 3], field.value)
        field.value = None
        self.assertEqual(None, field.value)
        field.value = [4]
        self.assertEqual([4], field.value)

    def test_repr(self):
        field = ModelField("test", Optional[int], 1)
        self.assertEqual("ModelField(name='test', type=typing.Optional[int], value=1)", repr(field))


if __name__ == '__main__':
    unittest.main()
