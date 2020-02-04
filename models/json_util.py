from bson.decimal128 import Decimal128 
from bson.objectid import ObjectId
from datetime import datetime, date, time, timedelta
from decimal import Decimal
import json 


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if type(obj) in (datetime, date, time):
            return obj.isoformat()

        if type(obj) in (Decimal, Decimal128, ObjectId):
            return str(obj)

        return json.JSONEncoder.default(self, obj)


class JSONDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.object_hook)

    def object_hook(self, dct):
        for k, v in dct.items():
            if type(v) == str:
                try:
                    dct[k] = datetime.fromisoformat(v)
                except ValueError:
                    pass
        
        return dct

