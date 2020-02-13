from copy import deepcopy

class Queryset:

    def __init__(self, model=None):
        self.model = model
        self._filter = {}
        self._projection = {}
        self._result_cache = None
        

    def __getitem__(self, item):
        pass 

    def __iter__(self):
        pass 

    def __len__(self):
        pass

    def __next__(self):
        pass

    def _copy(self):
        c = deepcopy(self)
        c._result_cache = None 
        return c

    def _evaluate(self):
        if self._result_cache is None:
            cursor = self.model.collection.find(filter=self._filter, projection=self._projection)
            self.result_cache = list(cursor)

    def all(self):
        qs = self._copy()
        qs._evaluate()
        return qs

    def count(self):
        return self.model.collection.count_documents(filter=self._filter)

    def defer(self, *fields):
        qs = self._copy()
        d = dict.fromkeys(field, False)
        qs._projection.update(d)
        return qs

    def delete(self):
        self.model.collection.delete_many(filter=self._filter)

    def filter(self, **kwargs):
        qs = self._copy()
        qs._filter.update(kwargs)
        return qs

    def get(self, **kwargs):
        pass

    def only(self, *fields):
        qs = self._copy()
        qs._projection = dict.fromkeys(fields, True)
        return qs

    def update(self, **kwargs):
        return self.model.collection.update_many(filter=self._filter, update=kwargs)