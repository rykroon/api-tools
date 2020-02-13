import json
import pickle
import uuid

from descriptors import CollectionDescriptor
from json_util import JSONEncoder, JSONDecoder, MongoJSONEncoder, MongoJSONDecoder


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

    @classmethod
    def get_by_id(cls, id):
        raise NotImplementedError

    @classmethod
    def get_many(cls, **kwargs):
        raise NotImplementedError


class MongoModel(Model):

    json_encoder = MongoJSONEncoder
    json_decoder = MongoJSONDecoder

    database = None
    collection = CollectionDescriptor()

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

    @classmethod
    def get_by_id(cls, id):
        try:
            object_id = ObjectId(id)
        except InvalidId:
            object_id = id

        document = cls.collection.find_one({'_id': object_id})
        if document is not None:
            return cls.from_dict(document)
        return None

    @classmethod
    def get_many(cls, **kwargs):
        cursor = cls.collection.find(kwargs)
        return [cls.from_dict(document) for document in cursor]


class RedisModel(Model):

    connection = None
    hash_name = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._key = uuid.uuid4()

    @property
    def pk(self):
        return self._key

    @property
    def _hash_name(self):
        return self.__class__.hash_name or self.__class__.__name__.lower()

    def delete(self):
        pk = str(self.pk)
        self.__class__.connection.hdel(self._hash_name, pk)

    def save(self):
        pk = str(self.pk)
        self.__class__.connection.hset(self._hash_name, pk, self.to_pickle())

    @classmethod
    def get_by_id(cls, id):
        hash_name = cls.hash_name or cls.__name__.lower()
        p = cls.connection.hget(hash_name, id)
        if p is not None:
            return cls.from_pickle(p)
        return None


class HybridModel(MongoModel, RedisModel):
    
    def delete(self):
        super().delete()
        RedisModel.delete(self)

    def save(self):
        super().save()
        RedisModel.save(self)

    @classmethod 
    def get_by_id(cls, id):
        instance = RedisModel.get_by_id(id)
        if instance is None:
            instance = super().get_by_id(id)
        return instance

