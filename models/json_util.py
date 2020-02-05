from bson.decimal128 import Decimal128 
from bson.objectid import ObjectId
from bson.errors import InvalidId
from datetime import datetime, date, time, timedelta
from decimal import Decimal
import json 


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if type(o) in (datetime, date, time):
            return o.isoformat()

        if type(o) in (Decimal, Decimal128, ObjectId):
            return str(o)

        return super().default(o)


class JSONDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.object_hook, parse_float=self.parse_float)

    def object_hook(self, obj):
        for k, v in obj.items():
            if type(v) == str:
                obj[k] = self.parse_str(v)

        return obj

    def parse_float(self, float_):
        return Decimal(float_)

    def parse_str(self, str_):
        try:
            return datetime.fromisoformat(str_)
        except ValueError:
            pass 

        return str_


class MongoJSONDecoder(JSONEncoder):

    def object_hook(self, obj):
        for k, v in obj.items():
            if type(v) == str:
                obj[k] = self.parse_str(v)

        return obj

    def parse_float(self, float_):
        return Decimal128(float_)

    def parse_str(self, str_):
        if len(str_) == 24:
            try:
                return ObjectId(str_)
            except InvalidId:
                pass 

        return super().parse_str(str_)


    #convert floats to Decimal128
    #if key is '_id', convert to ObjectId

