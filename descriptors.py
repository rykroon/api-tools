
class CollectionDescriptor:
    def __get__(self, instance, owner):
        if instance is not None:
            raise AttributeError("Collection isn't accessible via {} instances".format(owner.__name__))
        return owner.database[owner.__name__.lower()]
