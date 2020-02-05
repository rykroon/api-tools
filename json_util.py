from bson.decimal128 import Decimal128 
from bson.objectid import ObjectId
from bson.errors import InvalidId
from datetime import datetime, date, time, timedelta
from decimal import Decimal
import json 
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

    def parse_float(self, float_str):
        return Decimal(float_str)

    def parse_str(self, str_):
        if len(str_.replace('-','')) == 32:
            try:
                return UUID(str_)
            except:
                pass

        if str_.count('T') == 1:
            try:
                return datetime.fromisoformat(str_)
            except ValueError:
                pass

        if str_.count('-') == 2:
            try:
                return date.fromisoformat(str_)
            except ValueError:
                pass

        if str_count(':') == 2:
            try:
                return time.fromisoformat(str_)
            except ValueError:
                pass 

        return str_


class MongoJSONEncoder(JSONEncoder):
    def default(self, o):
        if type(o) in (Decimal128, ObjectId):
            return str(o)
        return super().default(o)


class MongoJSONDecoder(JSONDecoder):

    def parse_float(self, float_str):
        return Decimal128(float_str)

    def parse_str(self, str_):
        if len(str_) == 24:
            try:
                return ObjectId(str_)
            except InvalidId:
                pass 
        return super().parse_str(str_)

