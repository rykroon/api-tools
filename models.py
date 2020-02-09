import json
import pickle
import uuid

from managers import CollectionDescriptor, MongoManager, RedisManager
from json_util import JSONEncoder, MongoJSONEncoder, JSONDecoder

class SerializableObject:

    json_encoder = JSONEncoder
    json_decoder = JSONDecoder

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
        d = json.loads(j, **kwargs)
        return cls.from_dict(d)

    @classmethod
    def from_pickle(cls, p):
        instance = pickle.loads(p)
        if type(instance) != cls:
            raise TypeError
        return instance


class Model(SerializableObject):

    class DoesNotExist(Exception):
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

    def update(self, data):
        self.__dict__.update(data)


class MongoModel(Model):

    database = None
    collection = CollectionDescriptor()
    objects = MongoManager()

    json_encoder = MongoJSONEncoder

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

