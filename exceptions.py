class ObjectDoesNotExist(Exception):
    pass 

class MultipleObjectReturned(Exception):
    pass

class ValidationError(Exception):
    def __init__(self, errors):
        self.errors=errors