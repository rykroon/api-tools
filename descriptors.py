
class CollectionDescriptor:
    def __get__(self, instance, owner):
        if instance is not None:
            raise AttributeError("Collection isn't accessible via {} instances".format(owner.__name__))
        collection_name = owner.collection_name or owner.__name__.lower()
        return owner.database[collection_name]

    def __set__(self, instance, value):
        raise AttributeError("can't set attribute")


class HashNameDescriptor:
    def __init__(self):
        self.name = None

    def __get__(self, instance, owner):
        if self.name is None:
            return owner.__name__.lower()
        return self.name

    def __set__(self, instance, value):
        self.name = value
