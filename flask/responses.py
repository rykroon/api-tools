from flask import Response
import orjson

class JsonResponse(Response):
    default_mimetype = 'application/json'

    def __init__(self, response=None, *args, **kwargs):
        if type(response) in (dict, list, tuple):
            response = orjson.dumps(response)
        super().__init__(response=response, *args, **kwargs)


class ModelResponse(JsonResponse):
    def __init__(self, response=None, *args, **kwargs):
        if hasattr(response, 'to_json'):
            response = response.to_json()
        super().__init__(response=response, *args, **kwargs)