from bson.errors import InvalidId
from bson.objectid import ObjectId
import json
import pickle
import uuid

from descriptors import CollectionDescriptor, KeyPrefixDescriptor
from json_util import JSONEncoder, JSONDecoder, MongoJSONEncoder, MongoJSONDecoder


class SerializableObject:

    json_encoder = JSONEncoder
    json_decoder = JSONDecoder

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    @property
    def _cls(self):
        return self.__class__

    def to_dict(self):
        return dict(vars(self))

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
    collection_name = None
    collection = CollectionDescriptor()

    @property
    def pk(self):
        try:
            return self._id 
        except AttributeError:
            return None

    def delete(self):
        self._cls.collection.delete_one({'_id': self.pk})

    def save(self):
        if self.pk is None:
            result = self._cls.collection.insert_one(self.to_dict())
            self._id = result.inserted_id
        else:
            self._cls.collection.update_one(
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
    expiration = None
    key_prefix = KeyPrefixDescriptor()

    @property
    def pk(self):
        try:
            return self._id
        except AttributeError:
            return None

    @property
    def _key(self):
        return "{}:{}".format(self._cls.key_prefix, str(self.pk))

    def delete(self):
        self._RedisModel__delete()

    def save(self):
        self._RedisModel__save()

    def __delete(self):
        self._cls.connection.delete(self._key)

    def __save(self, ex=None):
        if self.pk is None:
            self._id = uuid.uuid4()

        ttl = self._cls.connection.ttl(self._key)
        ttl = 0 if ttl < 0 else ttl
        ex = ttl or ex or self._cls.expiration
        self._cls.connection.set(self._key, self.to_pickle(), ex=ex)

    @classmethod
    def get_by_id(cls, id):
        return cls._RedisModel__get_by_id(id)

    @classmethod
    def __get_by_id(cls, id):
        key = "{}:{}".format(cls.key_prefix, str(id))
        p = cls.connection.get(key)
        if p is not None:
            return cls.from_pickle(p)
        return None


class HybridModel(MongoModel, RedisModel):
    
    def delete(self):
        super().delete()
        super()._RedisModel__delete()

    def save(self, ex=None):
        super().save()
        super()._RedisModel__save(ex=ex)

    @classmethod 
    def get_by_id(cls, id):
        instance = cls._RedisModel__get_by_id(id)
        if instance is None:
            instance = super().get_by_id(id)
        return instance

