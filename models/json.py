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

