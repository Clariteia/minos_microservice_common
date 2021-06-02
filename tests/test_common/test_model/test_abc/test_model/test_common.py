"""
Copyright (C) 2021 Clariteia SL

This file is part of minos framework.

Minos framework can not be copied and/or distributed without the express permission of Clariteia SL.
"""
import unittest
from typing import (
    Optional,
)

from minos.common import (
    MinosAttributeValidationException,
    MinosMalformedAttributeException,
    MinosModelException,
    MinosParseAttributeException,
    MinosReqAttributeException,
    MinosTypeAttributeException,
    ModelField,
)
from tests.model_classes import (
    Analytics,
    Customer,
    CustomerFailDict,
    CustomerFailList,
    ShoppingList,
    User,
)


class TestMinosModel(unittest.TestCase):
    def test_constructor_args(self):
        model = Customer(1234, "johndoe", "John", "Doe")
        self.assertEqual(1234, model.id)
        self.assertEqual("johndoe", model.username)
        self.assertEqual("John", model.name)
        self.assertEqual("Doe", model.surname)

    def test_constructor_multiple_values(self):
        with self.assertRaises(TypeError):
            Customer(1234, id=1234)
        with self.assertRaises(TypeError):
            Customer(None, id=1234)

    def test_constructor_kwargs(self):
        model = Customer(id=1234, username="johndoe", name="John", surname="Doe")
        self.assertEqual(1234, model.id)
        self.assertEqual("johndoe", model.username)
        self.assertEqual("Doe", model.surname)
        self.assertEqual("John", model.name)

    def test_aggregate_setter(self):
        model = Customer(1234)
        model.name = "John"
        model.surname = "Doe"
        self.assertEqual(1234, model.id)
        self.assertEqual("Doe", model.surname)
        self.assertEqual("John", model.name)

    def test_attribute_parser_same_type(self):
        model = Customer(1234, name="john")
        self.assertEqual("John", model.name)

    def test_attribute_parser_different_type(self):
        model = ShoppingList(User(1234), cost="1.234,56")
        self.assertEqual(1234.56, model.cost)

    def test_attribute_parser_attribute(self):
        model = ShoppingList(User(1234, "admin"), cost="1.234,56")
        self.assertEqual(0.0, model.cost)

    def test_aggregate_int_as_string_type_setter(self):
        model = Customer("1234")
        model.name = "John"
        self.assertEqual(1234, model.id)
        self.assertEqual("John", model.name)

    def test_aggregate_wrong_int_type_setter(self):
        with self.assertRaises(MinosTypeAttributeException):
            Customer("1234S")

    def test_aggregate_string_type_setter(self):
        model = Customer(123)
        model.name = "John"
        self.assertEqual("John", model.name)

    def test_aggregate_wrong_string_type_setter_with_parser(self):
        model = Customer(123)
        with self.assertRaises(MinosParseAttributeException):
            model.name = 456

    def test_aggregate_wrong_string_type_setter(self):
        model = Customer(123)
        with self.assertRaises(MinosTypeAttributeException):
            model.surname = 456

    def test_aggregate_bool_type_setter(self):
        model = Customer(123)
        model.name = "John"
        model.is_admin = True
        self.assertTrue(model.is_admin)

    def test_aggregate_wrong_bool_type_setter(self):
        model = Customer(123)
        model.name = "John"
        with self.assertRaises(MinosTypeAttributeException):
            model.is_admin = "True"

    def test_aggregate_empty_mandatory_field(self):
        with self.assertRaises(MinosReqAttributeException):
            Customer()

    def test_model_is_freezed_class(self):
        model = Customer(123)
        with self.assertRaises(MinosModelException):
            model.address = "str kennedy"

    def test_model_list_class_attribute(self):
        model = Customer(123)
        model.lists = [1, 5, 8, 6]

        self.assertEqual([1, 5, 8, 6], model.lists)

    def test_model_list_wrong_attribute_type(self):
        model = Customer(123)
        with self.assertRaises(MinosTypeAttributeException):
            model.lists = [1, "hola", 8, 6]

    def test_model_ref(self):
        shopping_list = ShoppingList(cost=3.14)
        user = User(1234)
        shopping_list.user = user
        self.assertEqual(user, shopping_list.user)

    def test_model_ref_raises(self):
        shopping_list = ShoppingList(cost=3.14)
        with self.assertRaises(MinosTypeAttributeException):
            shopping_list.user = "foo"

    def test_recursive_type_composition(self):
        orders = {
            "foo": [ShoppingList(User(1)), ShoppingList(User(1))],
            "bar": [ShoppingList(User(2)), ShoppingList(User(2))],
        }

        analytics = Analytics(1, orders)
        self.assertEqual(orders, analytics.orders)

    def test_model_fail_list_class_attribute(self):
        with self.assertRaises(MinosMalformedAttributeException):
            CustomerFailList(123)

    def test_model_fail_dict_class_attribute(self):
        with self.assertRaises(MinosMalformedAttributeException):
            CustomerFailDict(123)

    def test_empty_required_value(self):
        with self.assertRaises(MinosReqAttributeException):
            User()

    def test_validate_required_raises(self):
        with self.assertRaises(MinosAttributeValidationException):
            User(-34)

    def test_validate_optional_raises(self):
        with self.assertRaises(MinosAttributeValidationException):
            User(1234, username="user name")

    def test_fields(self):
        user = User(123)
        fields = {
            "id": ModelField("id", int, 123, validator=user.validate_id),
            "username": ModelField(
                "username", Optional[str], parser=user.parse_username, validator=user.validate_username
            ),
        }
        self.assertEqual(fields, user.fields)

    def test_equal(self):
        a, b = User(123), User(123)
        self.assertEqual(a, b)

    def test_complex_equal(self):
        a, b = ShoppingList(User(1234), cost="1.234,56"), ShoppingList(User(1234), cost="1.234,56")
        self.assertEqual(a, b)

    def test_not_equal(self):
        a, b = User(123), User(456)
        self.assertNotEqual(a, b)

    def test_iter(self):
        user = User(123)
        expected = {
            "id": ModelField("id", int, 123, validator=user.validate_id),
            "username": ModelField(
                "username", Optional[str], parser=user.parse_username, validator=user.validate_username
            ),
        }
        self.assertEqual(expected, dict(user))

    def test_hash(self):
        user = User(123)

        expected = hash(
            (
                ("id", ModelField("id", int, 123, validator=user.validate_id)),
                (
                    "username",
                    ModelField("username", Optional[str], parser=user.parse_username, validator=user.validate_username),
                ),
            )
        )
        self.assertEqual(expected, hash(user))

    def test_repr(self):
        shopping_list = ShoppingList(User(1234), cost="1.234,56")
        expected = (
            "ShoppingList(fields=[ModelField(name='user', type=typing.Optional["
            "tests.model_classes.User], value=User(fields=[ModelField(name='id', type=<class 'int'>, value=1234, "
            "parser=None, validator=validate_id), ModelField(name='username', type=typing.Optional[str], value=None, "
            "parser=parse_username, validator=validate_username)]), parser=None, validator=None), ModelField(name="
            "'cost', type=<class 'float'>, value=1234.56, parser=parse_cost, validator=None)])"
        )
        self.assertEqual(expected, repr(shopping_list))

    def test_classname_cls(self):
        self.assertEqual("tests.model_classes.Customer", Customer.classname)

    def test_classname_instance(self):
        model = Customer(1234, "johndoe", "John", "Doe")
        self.assertEqual("tests.model_classes.Customer", model.classname)


if __name__ == "__main__":
    unittest.main()