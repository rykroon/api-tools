from bson.objectid import ObjectId


class ManagerDescriptor:
    def __get__(self, instance, model):
        if instance is not None:
            raise AttributeError("Manager isn't accessible via {} instances".format(model.__name__))

        if not hasattr(self, 'model'):
            self.model = model
        return self


class CollectionDescriptor:
    def __get__(self, instance, model):
        if instance is not None:
            raise AttributeError("Manager isn't accessible via {} instances".format(model.__name__))
        return model.database[model.__name__.lower()]


class Manager(ManagerDescriptor):
    def create(self, **kwargs):
        obj = self.model(**kwargs)
        obj.save()
        return obj

    def get_by_id(self, id):
        raise NotImplementedError


class MongoManager(Manager):
    def find(self, *args, **kwargs):
        query = kwargs
        projection = None
        if args:
            projection = dict.fromkeys(args, True)
        cursor = self.model.collection.find(query, projection)
        return [self.model(**document) for document in cursor]

    def find_one(self, *args, **kwargs):
        query = kwargs
        projection = None
        if args:
            projection = dict.fromkeys(args, True)

        document = self.model.collection.find_one(query, projection)
        if document:
            return self.model(**document)
        return None

    def get_by_id(self, id):
        try:
            id = ObjectId(id)
        except InvalidId:
            pass

        instance = self.find_one(_id=id)
        if instance is None:
            raise self.model.DoesNotExist


class RedisManager(Manager):

    def get_by_id(self, id):
        obj = self.hget(id)
        if object is None:
            raise self.__class__.DoesNotExist

    def hget(self, key):
        value = self.model.connection.hget(self.model.__name__.lower(), key)
        if value:
            return self.model.from_pickle(value)
        return None

    def hmget(self, keys):
        values = self.model.connection.hmget(self.model.__name__.lower(), keys)
        return [self.model.from_pickle(value) for value in values]

