from bson.objectid import ObjectId


class Manager:
    def __get__(self, instance, owner):
        if not hasattr(self, 'owner'):
            self.owner = owner
        return self

    def __set__(self, instance, value):
        raise AttributeError

    def create(self, **kwargs):
        return self.owner(**kwargs)


class CollectionManager(Manager):
    def __get__(self, instance, owner):
        return owner.database[owner.__name__.lower()]


class MongoManager(Manager):
    def find(self, *args, **kwargs):
        query = kwargs
        projection = None
        if args:
            projection = dict.fromkeys(args, True)
        cursor = self.owner.collection.find(query, projection)
        return [self.owner(**document) for document in cursor]

    def find_one(self, *args, **kwargs):
        query = kwargs
        projection = None
        if args:
            projection = dict.fromkeys(args, True)

        pk = query.pop('pk', None)
        if pk:
            if type(pk) != ObjectId:
                pk = ObjectId(pk)
            query['_id'] = pk

        document = self.owner.collection.find_one(query, projection)
        if document:
            return self.owner(**document)
        return None


class RedisManager(Manager):
    def get(self, key):
        value = self.owner.connection.get(key)
        if value:
            return self.owner.from_pickle(value)
        return None

    def mget(self, keys):
        values = self.owner.connection.mget(keys)
        return [self.owner.from_pickle(value) for value in values]

    def hget(self, key):
        value = self.owner.connection.hget(self.owner.__name__.lower(), key)
        if value:
            return self.owner.from_pickle(value)
        return None

    def hmget(self, keys):
        values = self.owner.connection.hmget(self.owner.__name__.lower(), keys)
        return [self.owner.from_pickle(value) for value in values]

