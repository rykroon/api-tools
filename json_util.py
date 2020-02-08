from bson.decimal128 import Decimal128 
from bson.objectid import ObjectId
from bson.errors import InvalidId
from datetime import datetime, date, time
from decimal import Decimal
import json 
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
    pass


def to_decimal(s):
    return Decimal(s)


def to_decimal128(s):
    return Decimal128(s)


def iso_object_hook(obj):
    for k, v in obj.items():
        if type(v) == dict:
            return obj[k] = iso_object_hook(v)
        if type(v) == list:
            pass
        if type(v) == str:
            try:
                if v.count('-') == 2:
                    obj[k] = datetime.fromisoformat(v)
                elif v.count(':') == 2:
                    obj[k] = time.fromisoformat(v)
            except ValueError:
                pass
    return obj


def mongo_object_hook(obj):
    """
        An object_hook function for decoding JSON
        Converts the '_id' key into an instance of ObjectId 
    """
    if '_id' in obj:
        try:
            obj['_id'] = ObjectId(obj['_id'])
        except InvalidId:
            pass
    return obj