import unittest

from minos.common.model.fields import ModelField
from minos.common.exceptions import MinosModelAttributeException


class TestModelField(unittest.TestCase):

    def test_name(self):
        field = ModelField("test", int, 3)
        self.assertEqual("test", field.name)

    def test_type(self):
        field = ModelField("test", int, 3)
        self.assertEqual({"origin": int}, field.type)

    def test_value_not_set(self):
        field = ModelField("test", int)
        self.assertEqual(None, field.value)

    def test_value(self):
        field = ModelField("test", int, 3)
        self.assertEqual(3, field.value)

    def test_value_setter(self):
        field = ModelField("test", int)
        field.value = 3
        self.assertEqual(3, field.value)

    def test_value_setter_raises(self):
        field = ModelField("test", int)
        with self.assertRaises(MinosModelAttributeException):
            field.value = None


if __name__ == '__main__':
    unittest.main()
