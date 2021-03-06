from unittest import (
    TestCase,
)

from minos.common import (
    Action,
    MinosImmutableClassException,
    ValueObject,
    ValueObjectSet,
    ValueObjectSetDiff,
    ValueObjectSetDiffEntry,
)
from tests.value_objects import (
    Address,
    Location,
)


class FakeValueObject(ValueObject):
    """Fake Value Object"""


class TestValueObject(TestCase):
    def setUp(self) -> None:
        self.address = Address(street="street name", number=42, zip_code=42042)

    def test_instantiate(self):
        self.assertEqual("street name", self.address.street)
        self.assertEqual(42, self.address.number)
        self.assertEqual(42042, self.address.zip_code)

    def test_raise_when_accessed(self):
        with self.assertRaises(MinosImmutableClassException):
            self.address.street = "this assignment must raise"


class TestValueObjectSet(TestCase):
    def setUp(self) -> None:
        self.location_1 = Location(street="street name")
        self.location_2 = Location(street="another street name")
        self.fake_value_obj = {str(hash(self.location_1)): self.location_1, str(hash(self.location_2)): self.location_2}
        self.fake_value_obj_set = (self.location_1, self.location_2)

    def test_data(self):
        value_objects = ValueObjectSet(self.fake_value_obj)
        self.assertEqual(self.fake_value_obj, value_objects)

    def test_from_set(self):
        value_objects = ValueObjectSet(self.fake_value_obj_set)
        self.assertEqual(self.fake_value_obj, value_objects)

    def test_eq_true(self):
        observed = ValueObjectSet(self.fake_value_obj)

        self.assertEqual(self.fake_value_obj, observed)
        self.assertEqual({k: v for k, v in self.fake_value_obj.items()}, observed)

    def test_eq_false(self):
        raw = self.fake_value_obj
        observed = ValueObjectSet(raw)
        loc = Location("Test")
        other = {str(hash(loc)): Location("Test")}

        self.assertNotEqual(ValueObjectSet(other), set(raw))
        self.assertNotEqual(ValueObjectSet(other), observed)
        self.assertNotEqual(other, observed)
        self.assertNotEqual({k: v for k, v in other.items()}, observed)

    def test_len(self):
        value_objects = ValueObjectSet(self.fake_value_obj)
        self.assertEqual(2, len(value_objects))

    def test_iter(self):
        value_objects = ValueObjectSet(self.fake_value_obj)
        self.assertEqual(set(self.fake_value_obj.values()), set(value_objects))

    def test_contains(self):
        str_hash = str(hash(self.location_1))
        raw = {str_hash: self.location_1}

        value_objects = ValueObjectSet(raw)

        self.assertIn(self.location_1, value_objects)
        self.assertNotIn(self.location_2, value_objects)
        self.assertNotIn(1234, value_objects)

    def test_add(self):

        value_objects = ValueObjectSet()
        value_objects.add(self.location_1)

        str_hash = str(hash(self.location_1))
        raw = {str_hash: self.location_1}

        self.assertEqual(raw, value_objects)

    def test_remove(self):

        value_objects = ValueObjectSet(self.fake_value_obj)
        value_objects.discard(self.location_1)

        str_hash = str(hash(self.location_2))
        raw = {str_hash: self.location_2}
        self.assertEqual(raw, value_objects)

    def test_diff(self):
        raw = [Location(street="street name"), Location(street="another street name")]
        entities = ValueObjectSet(raw)

        observed = entities.diff(ValueObjectSet([raw[0]]))
        expected = ValueObjectSetDiff([ValueObjectSetDiffEntry(Action.CREATE, raw[1])])

        self.assertEqual(observed, expected)


class TestValueObjectSetDiff(TestCase):
    def setUp(self) -> None:
        self.raw = [Location(street="street name"), Location(street="another street name")]
        self.old = ValueObjectSet(self.raw)

        self.clone = [Location(street=entity.street) for entity in self.raw]

    def test_from_difference_create(self):
        entities = ValueObjectSet(self.clone)
        new = Location("San Anton, 23")
        entities.add(new)

        observed = ValueObjectSetDiff.from_difference(entities, self.old)
        expected = ValueObjectSetDiff([ValueObjectSetDiffEntry(Action.CREATE, new)])
        self.assertEqual(expected, observed)

    def test_from_difference_delete(self):
        entities = ValueObjectSet(self.clone)
        removed = self.clone[1]
        entities.remove(removed)

        observed = ValueObjectSetDiff.from_difference(entities, self.old)
        expected = ValueObjectSetDiff([ValueObjectSetDiffEntry(Action.DELETE, removed)])
        self.assertEqual(expected, observed)

    def test_from_difference_combined(self):
        entities = ValueObjectSet(self.clone)
        new = Location("Europa, 12")
        entities.add(new)

        removed = self.clone[1]
        entities.remove(removed)

        observed = ValueObjectSetDiff.from_difference(entities, self.old)

        expected = ValueObjectSetDiff(
            [ValueObjectSetDiffEntry(Action.CREATE, new), ValueObjectSetDiffEntry(Action.DELETE, removed)]
        )
        self.assertEqual(expected, observed)
