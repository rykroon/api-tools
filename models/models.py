import json
import pickle
import uuid

from .managers import CollectionDescriptor, MongoManager, RedisManager
from .json_util import JSONEncoder, JSONDecoder


class SerializableObject:

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def to_dict(self):
        return vars(self)

    def to_json(self):
        return json.dumps(self.to_dict(), cls=JSONEncoder)

    def to_pickle(self):
        return pickle.dumps(self)

    @classmethod
    def from_dict(cls, d):
        return cls(**d)

    @classmethod
    def from_json(cls, j):
        d = json.loads(j, cls=JSONDecoder)
        return cls.from_dict(d)

    @classmethod
    def from_pickle(cls, p):
        instance = pickle.loads(p)
        if type(instance) != cls:
            raise TypeError
        return instance


class Model(SerializableObject):

    def __eq__(self, value):
        if type(self) != type(value):
            return False

        if self is value:
            return True

        if self.pk is None or value.pk is None:
            return False

        return self.pk == value.pk

    def __hash__(self):
        return hash((self.__class__.__name__), str(self.pk))

    def __repr__(self):
        return "{}(pk={})".format(self.__class__.__name__, self.pk)

    def __str__(self):
        return repr(self)

    @property
    def pk(self):
        raise NotImplementedError

    def clean(self):
        raise NotImplementedError

    def delete(self):
        raise NotImplementedError

    def refresh(self):
        raise NotImplementedError

    def save(self):
        raise NotImplementedError


class MongoModel(Model):

    database = None
    collection = CollectionManager()
    objects = MongoManager()

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
        self._key = str(uuid.uuid4())

    @property
    def pk(self):
        return self._key

    def delete(self):
        self.__class__.connection.delete(self.pk)

    def save(self):
        self.__class__.connection.set(self.pk, self.to_pickle())

