from bson.decimal128 import Decimal128 
from bson.objectid import ObjectId
from bson.errors import InvalidId
from datetime import datetime, date, time, timedelta
from decimal import Decimal
import json 
from strings import hexdigits
from uuid import UUID


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if type(o) in (datetime, date, time):
            return o.isoformat()
        if type(o) in (Decimal, UUID):
            return str(o)
        return super().default(o)


class JSONDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.object_hook, parse_float=self.parse_float)

    def object_hook(self, obj):
        for k, v in obj.items():
            if type(v) == dict:
                obj[k] = self.object_hook(v)
            elif type(v) == str:
                obj[k] = self.parse_str(v)
        return obj

    def parse_float(self, f):
        return Decimal(f)

    def parse_str(self, s):
        try:
            temp_string = s.replace('-','')
            if len(temp_string) == 32:
                if all(c in hexdigits for c in temp_string)
                    return UUID(s)

            if s.count('-') == 2:
                if s.count('T') == 1:
                    return datetime.fromisoformat(s)
                elif s.count('T') == 0:
                    return date.fromisoformat(s)

            if s.count(':') == 2:
                return time.fromisoformat(s)

        except ValueError:
            pass

        return s


class MongoJSONEncoder(JSONEncoder):
    def default(self, o):
        if type(o) in (Decimal128, ObjectId):
            return str(o)
        return super().default(o)


class MongoJSONDecoder(JSONDecoder):
    def parse_float(self, f):
        return Decimal128(f)

    def parse_str(self, s):
        temp_string = s.replace('-','')
        if len(temp_string) == 24:
            if all(c in hexdigits for c in temp_string):
                try:
                    return ObjectId(s)
                except InvalidId:
                    pass 
        return super().parse_str(s)

