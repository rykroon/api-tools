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
    def __init__(self, *, object_hook=None, parse_float=None, parse_int=None, 
        parse_constant=None, strict=True, object_pairs_hook=None):
        
        if object_hook is None and hasattr(self, 'object_hook'):
            object_hook = self.object_hook 
        
        if parse_float is None and hasattr(self, 'parse_float'):
            parse_float = self.parse_float 

        if parse_int is None and hasattr(self, 'parse_int'):
            parse_int = self.parse_int 

        if parse_constant is None and hasattr(self, 'parse_constant'):
            parse_constant = self.parse_constant 

        if object_pairs_hook is None and hasattr(self, 'object_pairs_hook'):
            object_pairs_hook = self.object_pairs_hook

        super().__init__(object_hook=object_hook, parse_float=parse_float, parse_int=parse_int, 
            parse_constant=parse_constant, strict=strict, object_pairs_hook=object_pairs_hook)

    def object_hook(self, obj):
        if type(obj) == dict:
            iterator = obj.items()
        elif type(obj) == list:
            iterator = enumerate(obj)

        for k, v in iterator:
            if type(v) in (dict, list):
                obj[k] = self.object_hook(v)
            if type(v) == str:
                obj[k] = self.parse_str(v) 

        return obj

    def parse_str(self, s):
        try:
            if s.count('-') == 2:
                return datetime.fromisoformat(s)
            if s.count(':') == 2:
                return time.fromisoformat(s)
            #add logic for UUIDs
        except ValueError:
            pass
        return s


class MongoJSONDecoder(JSONDecoder):
    def object_hook(self, obj):
        if '_id' in obj:
            try:
                obj['_id'] = ObjectId(obj['_id'])
            except InvalidId:
                pass
        return super().object_hook(obj)


def to_decimal(s):
    return Decimal(s)


def to_decimal128(s):
    return Decimal128(s)
