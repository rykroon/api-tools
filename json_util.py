from bson.decimal128 import Decimal128 
from bson.objectid import ObjectId
from bson.errors import InvalidId
from datetime import datetime, date, time
from decimal import Decimal
import json 
    

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if type(o) in (datetime, date, time):
            return o.isoformat()
        elif type(o) in (Decimal, Decimal128):
            return float(str(o))
        return str(o)


def default(o):
    if type(o) in (datetime, date, time):
        return o.isoformat()
    elif type(o) in (Decimal, Decimal128):
        return float(str(o))
    return str(o)


def to_decimal(s):
    return Decimal(s)


def to_decimal128(s):
    return Decimal128(s)


# might want a default object_hook for converting ISO dates into datetime objects
def iso_object_hook(obj):
    for k, v in obj.items():
        if type(v) == dict:
            return obj[k] = iso_object_hook(v)

        if type(v) == list:
            pass
            
        if type(v) == str:
            if v.count('-') == 2:
                try:
                    obj[k] = datetime.fromisoformat(v)
                except ValueError:
                    pass

            elif v.count(':') == 2:
                try:
                    obj[k] = time.fromisoformat(v)
                except ValueError:
                    pass


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