from bson.decimal128 import Decimal128 
from bson.objectid import ObjectId
from bson.errors import InvalidId
from datetime import datetime, date, time
from decimal import Decimal
import json 
import re
from uuid import UUID


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, (datetime, date, time)) :
            return o.isoformat()
        if isinstance(o, Decimal):
            return float(o)
        if isinstance(o, UUID):
            return str(o)
        return super().default(o)


class MongoJSONEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal128):
            return float(str(o))
        if isinstance(o, ObjectId):
            return str(o)
        return super().default(o)


class JSONDecoder(json.JSONDecoder):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.regex_list = [
            (re.compile(r'\d{4}-([0][0-9]|1[0-2])-([0-2][0-9]|3[01])'), datetime.fromisoformat),
            (re.compile(r'([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]'), time.fromisoformat),
            (re.compile(r'[\da-fA-F]{8}-?[\da-fA-F]{4}-?[\da-fA-F]{4}-?[\da-fA-F]{4}-?[\da-fA-F]{12}'), UUID)
        ]
        self.parse_string = self.new_scanstring
        self.scan_once = json.scanner.py_make_scanner(self)

    def new_scanstring(self, s, end, strict=True):
        (s, end) = json.decoder.scanstring(s, end, strict)

        for regex, func in self.regex_list:
            if regex.match(s):
                try:
                    return (func(s), end)
                except:
                    pass 
        return (s, end)


class MongoJSONDecoder(JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.regex_list.append(
            (re.compile(r'[\da-fA-F]{24}'), ObjectId)
        )


def to_decimal(s):
    return Decimal(s)


def to_decimal128(s):
    return Decimal128(s)
