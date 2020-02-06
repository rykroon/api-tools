import json
import orjson
import pickle
import uuid

from managers import CollectionManager, MongoManager, RedisManager
from json_util import JSONEncoder, JSONDecoder, MongoJSONEncoder, MongoJSONDecoder


class SerializableObject:

    json_encoder = JSONEncoder
    json_decoder = JSONDecoder

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def to_dict(self):
        return vars(self)

    def to_json(self):
        return orjson.dumps(self.to_dict(), default=str)
        #return json.dumps(self.to_dict(), cls=self.__class__.json_encoder)

    def to_pickle(self):
        return pickle.dumps(self)

    @classmethod
    def from_dict(cls, d):
        return cls(**d)

    @classmethod
    def from_json(cls, j):
        d = orjson.loads(j, cls=cls.json_decoder)
        #d = json.loads(j, cls=cls.json_decoder)
        return cls.from_dict(d)

    @classmethod
    def from_pickle(cls, p):
        instance = pickle.loads(p)
        if type(instance) != cls:
            raise TypeError
        return instance


class Model(SerializableObject):

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


class MongoModel(Model):

    database = None
    collection = CollectionManager()
    objects = MongoManager()

    #json_encoder = MongoJSONEncoder
    #json_decoder = MongoJSONDecoder

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

    def delete(self, hash_=True):
        if hash_:
            self.__class__.connection.hdel(self.__class__.__name__.lower(), self.pk)
        else:
            self.__class__.connection.delete(self.pk)

    def save(self, hash_=True):
        if hash_:
            self.__class__.connection.hset(self.__class__.__name__.lower(), self.pk, self.to_pickle())
        else:
            self.__class__.connection.set(self.pk, self.to_pickle())

