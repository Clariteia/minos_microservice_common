"""
Copyright (C) 2021 Clariteia SL

This file is part of minos framework.

Minos framework can not be copied and/or distributed without the express permission of Clariteia SL.
"""

import io
from typing import (
    Any,
    Union,
)

from fastavro import (
    parse_schema,
    reader,
    writer,
)

from ...exceptions import (
    MinosProtocolException,
)
from ...logs import (
    log,
)
from ..abc import (
    MinosBinaryProtocol,
)
from .schemas import (
    DATABASE_AVRO_SCHEMA,
    MESSAGE_AVRO_SCHEMA,
)


class MinosAvroProtocol(MinosBinaryProtocol):
    @classmethod
    def encode(cls, headers: dict, body: dict = None) -> bytes:
        """
        encoder in avro
        all the headers are converted in fields with doble underscore name
        the body is a set fields coming from the data type.
        """

        # prepare the headers
        schema = MESSAGE_AVRO_SCHEMA
        final_data = {}
        final_data["headers"] = headers
        if body:
            final_data["body"] = body

        if not isinstance(final_data, list):
            final_data = [final_data]

        return cls._encode(schema, final_data)

    @classmethod
    def _encode(cls, schema_val: dict[str, Any], final_data: list[dict[str, Any]]) -> bytes:
        try:
            schema_bytes = parse_schema(schema_val)
            with io.BytesIO() as file:
                writer(file, schema_bytes, final_data)
                file.seek(0)
                content_bytes = file.getvalue()
                return content_bytes
        except Exception:
            raise MinosProtocolException(
                "Error encoding data, check if is a correct Avro Schema and Datum is provided."
            )

    @classmethod
    def decode(cls, data: bytes) -> dict:
        data_return: dict = {}
        try:
            data_return["headers"] = {}
            for schema_dict in cls._decode(data):
                log.debug("Avro: get the request/response in dict format")
                data_return["headers"] = schema_dict["headers"]
                # check wich type is body
                if "body" in schema_dict:
                    if isinstance(schema_dict["body"], dict):
                        data_return["body"] = {}
                    elif isinstance(schema_dict["body"], list):
                        data_return["body"] = []
                    data_return["body"] = schema_dict["body"]
            return data_return
        except Exception:
            raise MinosProtocolException("Error decoding string, check if is a correct Avro Binary data")

    @classmethod
    def _decode(cls, data: bytes) -> list[dict[str, Any]]:
        with io.BytesIO(data) as file:
            return list(reader(file))


class MinosAvroValuesDatabase(MinosAvroProtocol):
    """Encoder/Decoder class for values to be stored on the database with avro format."""

    @classmethod
    def encode(cls, value: Any, schema: dict = None) -> bytes:
        """Encoder in avro for database Values
        all the headers are converted in fields with double underscore name
        the body is a set fields coming from the data type.

        :param value: The data to be stored.
        :param schema: The schema relative to the data.
        :return: A bytes object.
        """

        # prepare the headers
        if not schema:
            schema_val = DATABASE_AVRO_SCHEMA
            final_data = {}
            final_data["content"] = value
        else:
            schema_val = schema
            final_data = value

        if not isinstance(final_data, list):
            final_data = [final_data]

        return cls._encode(schema_val, final_data)

    @classmethod
    def decode(
        cls, data: bytes, content_root: bool = True, flatten: bool = True
    ) -> Union[dict[str, Any], list[dict[str, Any]]]:
        """Decode the given bytes of data into a single dictionary or a sequence of dictionaries.

        :param data: A bytes object.
        :param content_root: If ``True``
        :param flatten: If ``True`` tries to return the values as flat as possible.
        :return: A dictionary or a list of dictionaries.
        """
        try:
            ans = list()
            for schema_dict in cls._decode(data):
                log.debug("Avro Database: get the values data")
                if content_root:
                    schema_dict = schema_dict["content"]
                ans.append(schema_dict)
            if flatten and len(ans) == 1:
                return ans[0]
            return ans
        except Exception:
            raise MinosProtocolException("Error decoding string, check if is a correct Avro Binary data")