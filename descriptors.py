
class CollectionDescriptor:
    def __get__(self, instance, owner):
        if instance is not None:
            raise AttributeError("Collection isn't accessible via {} instances".format(owner.__name__))
        collection_name = owner.collection_name or owner.__name__.lower()
        return owner.database[collection_name]

    def __set__(self, instance, value):
        raise AttributeError("can't set attribute")


class KeyPrefixDescriptor:
    def __init__(self):
        self.prefix = None

    def __get__(self, instance, owner):
        if self.prefix is None:
            return owner.__name__.lower()
        return self.prefix

    def __set__(self, instance, value):
        self.prefix = value
