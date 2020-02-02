from pymongo import MongoClient
from bson.objectid import ObjectId
#from bson.decimal128 import Decimal128


class CollectionDescriptor:
    def __init__(self):
        self.collection_name = None # maybe?

    def __get__(self, instance, owner):
        return owner.database[owner.__name__.lower()]


class ObjectDescriptor:
    def __init__(self):
        self.owner = None

    def __get__(self, instance, owner):
        if self.owner is None:
            self.owner = owner
        return self

    def find(self, **kwargs):
        cursor = self.owner.collection.find(kwargs)
        return [self.owner(**document) for document in cursor]

    def find_one(self, **kwargs):
        document = self.owner.collection.find_one(kwargs)
        if document is None:
            return None
        return self.owner(**document)

    def get(self, id):
        object_id = ObjectId(id)
        return self.find_one(_id=object_id)


class Model:

    database = None
    collection = CollectionDescriptor()
    objects = ObjectDescriptor()

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __eq__(self, value):
        if not isinstance(value, Model):
            return False

        if self.pk is None or value.pk is None:
            return False

        return hash(self) == hash(other)

    def __hash__(self):
        return hash((self.__class__.__name__), str(self.pk))

    def __repr__(self):
        return "{}(_id='{}')".format(self.__class__.__name__, self.pk)

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
            self.__class__.collection.insert_one(vars(self))
        else:
            self.__class__.collection.update_one(
                {'_id': self.pk}, 
                {'$set': vars(self)}
            )

