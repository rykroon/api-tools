from bson.objectid import ObjectId


class CollectionDescriptor:
    def __get__(self, instance, owner):
        return owner.database[owner.__name__.lower()]

    def __set__(self, instance, value):
        raise AttributeError


class Manager:
    def __get__(self, instance, owner):
        if not hasattr(self, 'owner'):
            self.owner = owner
        return self

    def __set__(self, instance, value):
        raise AttributeError


class MongoObjectManager(Manager):
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


class RedisObjectManager(Manager):
    def get(self, id):
        pass

    def get_many(self, ids):
        pass
