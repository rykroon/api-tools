from copy import copy

class Queryset:

    def __init__(self, model=None):
        self.model = model
        self.filter = {}
        self.projection = {}
        self.results = None
        

    def __getitem__(self, item):
        pass 

    def __iter__(self):
        pass 

    def __len__(self):
        pass

    def __next__(self):
        pass

    def all(self):
        qs = copy(self)
        cursor = qs.model.collection.find(filter=qs.filter, projection=qs.projection)
        qs.results = list(cursor)
        return qs

    def count(self):
        return self.model.collection.count_documents(filter=self.filter)

    def defer(self, *fields):
        qs = copy(self)
        d = dict.fromkeys(field, False)
        qs.projection.update(d)
        return qs

    def delete(self):
        self.model.collection.delete_many(filter=self.filter)

    def filter(self, **kwargs):
        qs = copy(self)
        qs.filter.update(kwargs)
        return qs

    def get(self, **kwargs):
        pass

    def only(self, *fields):
        qs = copy(self)
        qs.projection = dict.fromkeys(fields, True)
        return qs

    def update(self, **kwargs):
        return self.model.collection.update_many(filter=self.filter, update=kwargs)