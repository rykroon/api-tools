from bson.objectid import ObjectId
from flask import abort, jsonify, request
from flask.views import MethodView
import orjson
from pymongo.errors import InvalidId

from .responses import JsonResponse, ModelResponse


class ResourceView(MethodView):

    def get_resource_by_id(self, id):
        """
            @returns: The resource associated with the id, else None
        """
        raise NotImplementedError

    def dispatch_request(self, *args, **kwargs):
        id = kwargs.pop('id', None)
        if id is not None:
            resource = self.get_resource_by_id(id)
            if resource is None:
                abort(404)
            return super().dispatch_request(resource, *args, **kwargs)
        return super().dispatch_request(*args, **kwargs)


class DocumentView(ResourceView):
    collection = None 

    def get_resource_by_id(self, id):
        try:
            object_id = ObjectId(id)
            
        except InvalidId as e:
            return None 

        return self.__class__.collection.find_one({'_id': object_id})
        
    def get(self, document=None):
        if document:
            return JsonResponse(document)
        else:
            documents = list(self.__class__.collection.find(request.args))
            return JsonResponse(documents)

    def post(self):
        data = orjson.loads(request.get_data())
        self.__class__.collection.insert_one(data)
        return JsonResponse(data, status=201)

    def put(self, document):
        data = orjson.loads(request.get_data())
        document.update(**data)
        self.__class__.update_one(
            {'_id': document.get('_id')},
            {'$set': document}
        )
        return JsonResponse(document)

    def delete(self, document):
        self.__class__.collection.delete_one({'_id': document.get('_id')})
        return JsonResponse(document)


class ModelView(ResourceView):
    model = None

    def get_resource_by_id(self, id):
        return self.__class__.model.get(id) #???

    def get(self, instance=None):
        if instance:
            return ModelResponse(instance)
        else:
            results = self.__class__.model.objects.find(request.args)
            return JsonResponse(results)

    def post(self):
        data = orjson.loads(request.get_data())
        instance = self.__class__.model(**data)
        instance.save()
        return ModelResponse(instance, status=201)

    def put(self, instance):
        data = orjson.loads(request.get_data())
        instance.update(data) #??
        instance.save()
        return ModelResponse(instance)

    def delete(self, instance):
        instance.delete()
        return ModelResponse(instance)