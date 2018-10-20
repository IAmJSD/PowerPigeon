import abc
import json
import pytz
import datetime as dt
from .exceptions import ConversionError


class BaseAttribute(abc.ABC):
    """
        A base attribute. Attributes are used to convert data from results into
        data for the model and vice versa.
    """

    def __init__(self, required=False, item_id=False, default=None):
        self.model = None
        self.required = required
        self.item_id = item_id
        self.default = default

    @abc.abstractmethod
    async def encode(self, data):
        return data

    @abc.abstractmethod
    async def decode(self, data):
        return data


class TextAttribute(BaseAttribute):
    """The attribute that is used for text."""
    async def encode(self, data):
        try:
            return str(data)
        except ValueError:
            raise ConversionError(
                "Could not convert to a string."
            )

    async def decode(self, data):
        return data


class NumberAttribute(BaseAttribute):
    """Converts numbers based on their size and converts them back."""
    async def encode(self, data):
        if not isinstance(data, int):
            try:
                data = int(data)
            except ValueError:
                raise ConversionError(
                    "Could not convert to a integer."
                )

        if -9007199254740991 < data > 9007199254740991:
            return data
        else:
            return str(data)

    async def decode(self, data):
        return int(data)


class JSONAttribute(BaseAttribute):
    """The attribute that is used for pure JSON."""
    async def encode(self, data):
        try:
            json.dumps(data)
        except json.JSONDecodeError:
            raise ConversionError(
                "Data is not valid JSON."
            )

        return data

    async def decode(self, data):
        return data


class BytesAttribute(BaseAttribute):
    """The attribute that is used for bytes."""
    async def encode(self, data):
        return bytes(data)

    async def decode(self, data):
        return data


class UTCDateTimeAttribute(BaseAttribute):
    """The attribute for UTC date/time."""
    async def encode(self, data):
        if not isinstance(data, dt.datetime):
            raise ConversionError('Not a valid "datetime" object.')

        return data.replace(tzinfo=pytz.utc)

    async def decode(self, data):
        return data


class DateTimeAttribute(BaseAttribute):
    """The attribute for regular timezone date/time."""
    async def encode(self, data):
        if not isinstance(data, dt.datetime):
            raise ConversionError('Not a valid "datetime" object.')

        return data

    async def decode(self, data):
        return data


class BooleanAttribute(BaseAttribute):
    """This attribute handles booleans."""
    async def encode(self, data):
        if not isinstance(data, bool):
            data = bool(data)

        return data

    async def decode(self, data):
        return data
