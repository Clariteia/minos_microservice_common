"""
Copyright (C) 2021 Clariteia SL

This file is part of minos framework.

Minos framework can not be copied and/or distributed without the express permission of Clariteia SL.
"""

from typing import Optional

from minos.common import MinosModel, ModelRef


class Base(MinosModel):
    """
    base class derived directly from MinosModel
    """
    id: int


class User(Base):
    """
    Class for Inheritance Test
    """
    username: Optional[str]

    @staticmethod
    def parse_username(value: str) -> str:
        """Parse username into a cleaner format.

        :param value: username to be parsed.
        :return: An string object.
        """
        return value.lower()


class ShoppingList(MinosModel):
    """Class to test ``MinosModel`` composition."""
    user: Optional[ModelRef[User]]
    cost: float

    @staticmethod
    def parse_cost(value: Optional[str]) -> float:
        """Parse a number encoded as string with a semicolon as decimal separator.

        :param value: cost to be parsed.
        :return: A float value.
        """
        if value is None:
            return 0.0
        return float(value.replace(".", "").replace(",", "."))


class Customer(User):
    """
    Test a Model Class with List
    """
    name: Optional[str]
    surname: Optional[str]
    is_admin: Optional[bool]
    lists: Optional[list[int]]

    @staticmethod
    def parse_name(name: str) -> str:
        """Parse name into a cleaner format.

        :param name: name to be parsed.
        :return: An string object.
        """
        return name.title()


class CustomerDict(User):
    """
    Test a Model Class with Dictionary
    """
    name: str
    surname: str
    friends: dict[str, str]


class CustomerFailList(User):
    """
    Test a Model Class with a List wrong formatted
    """
    name: Optional[str]
    surname: Optional[str]
    listes_failed: Optional[list]


class CustomerFailDict(User):
    """
    Test a Model Class with a Dictionary wrong formatted
    """
    name: Optional[str]
    surname: Optional[str]
    friends: dict
