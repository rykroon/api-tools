from datetime import datetime, date, time
import json
import pickle
from types import BuiltinFunctionType, FunctionType
import uuid

from managers import CollectionDescriptor, MongoManager, RedisManager
from json_util import JSONEncoder, JSONDecoder, MongoJSONEncoder, MongoJSONDecoder
from exceptions import ObjectDoesNotExist

class SerializableObject:

    json_encoder = JSONEncoder
    json_decoder = JSONDecoder

    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls)

        if hasattr(cls, '__annotations__'):
            for attr, typ in cls.__annotations__.items():
                try:
                    value = getattr(cls, attr)
                except AttributeError:
                    value = None 

                if type(value) in (BuiltinFunctionType, FunctionType):
                    value = value()

                setattr(obj,attr, value)
        return obj

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def to_dict(self):
        return vars(self)

    def to_json(self, **kwargs):
        encoder = kwargs.pop('cls', self.__class__.json_encoder)
        return json.dumps(self.to_dict(), cls=encoder, **kwargs)

    def to_pickle(self):
        return pickle.dumps(self)

    @classmethod
    def from_dict(cls, d):
        return cls(**d)

    @classmethod
    def from_json(cls, j, **kwargs):
        decoder = kwargs.pop('cls', cls.json_decoder)
        d = json.loads(j, cls=decoder, **kwargs)
        return cls.from_dict(d)

    @classmethod
    def from_pickle(cls, p):
        instance = pickle.loads(p)
        if type(instance) != cls:
            raise TypeError
        return instance


class Model(SerializableObject):

    class DoesNotExist(ObjectDoesNotExist):
        pass

    def __eq__(self, other):
        if not isinstance(other, Model):
            return NotImplemented

        if type(self) != type(other):
            return False

        if self.pk is None:
            return self is other

        return self.pk == other.pk

    def __hash__(self):
        if self.pk is None:
            raise TypeError("Model instances without a primary key value are unhashable")
        return hash(self.pk)

    def __repr__(self):
        return "<{}: {}>".format(self.__class__.__name__, self)

    def __str__(self):
        return "{} object ({})".format(self.__class__.__name__, self.pk)

    @property
    def pk(self):
        raise NotImplementedError

    def delete(self):
        raise NotImplementedError

    def save(self):
        raise NotImplementedError

    def full_clean(self, exclude=None):
        """
            calls type_check_fields() and clean()
            raises a TypeError if there are errors 
        """
        self.clean()
        self.type_check_fields(exclude=exclude)

    def clean(self):
        pass

    def type_check_fields(self, exclude=None):
        if exclude is None:
            exclude = []

        errors = {} 
        if hasattr(self, '__annotations__'):
            for attr, typ in self.__annotations__.items():
                if attr in exclude:
                    continue

                value = getattr(self, attr)
                if value is None:
                    #maybe add logic so that if an attribute has a default value
                    # then the value cannot be None??
                    continue

                if type(value) != typ:
                    errors[attr] = "field '{}' must be of type '{}'".format(attr, typ)

        if errors:
            raise TypeError(errors)

    def update(self, data):
        self.__dict__.update(data)


class MongoModel(Model):

    database = None
    collection = CollectionDescriptor()
    objects = MongoManager()

    json_encoder = MongoJSONEncoder
    json_decoder = MongoJSONDecoder

    @property
    def pk(self):
        try:
            return self._id 
        except AttributeError:
            return None

    def delete(self):
        self.__class__.collection.delete_one({'_id': self.pk})

    def save(self):
        if self.pk is None:
            self.__class__.collection.insert_one(self.to_dict())
        else:
            self.__class__.collection.update_one(
                {'_id': self.pk}, 
                {'$set': self.to_dict()}
            )


class RedisModel(Model):

    connection = None
    objects = RedisManager()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._key = uuid.uuid4()

    @property
    def pk(self):
        return str(self._key)

    def delete(self):
        self.__class__.connection.hdel(self.__class__.__name__.lower(), self.pk)

    def save(self):
        self.__class__.connection.hset(self.__class__.__name__.lower(), self.pk, self.to_pickle())

