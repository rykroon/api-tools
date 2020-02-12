from bson.objectid import ObjectId
from flask import abort, jsonify, request
from flask.views import MethodView
from pymongo.errors import InvalidId

from aux import jsonify_model


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
            return jsonify(document)
        else:
            documents = list(self.__class__.collection.find(request.args))
            return jsonify(documents)

    def post(self):
        data = request.get_json()
        self.__class__.collection.insert_one(data)
        return jsonify(data), status=201

    def put(self, document):
        data = request.get_json()
        document.update(data)
        self.__class__.update_one(
            {'_id': document.get('_id')},
            {'$set': document}
        )
        return jsonify(document)

    def delete(self, document):
        self.__class__.collection.delete_one({'_id': document.get('_id')})
        return jsonify(document)


class ModelView(ResourceView):
    model = None

    def get_resource_by_id(self, id):
        return self.__class__.model.objects.get_by_id(id) 

    def get(self, instance=None):
        if instance:
            return jsonify_model(instance)
        else:
            results = self.__class__.model.objects.find(request.args)
            return jsonify(results)

    def post(self):
        instance = self.__class__.model.from_json(request.data)
        instance.save()
        return jsonify_model(instance), status=201

    def put(self, instance):
        data = request.get_json()
        instance.update(data)
        instance.save()
        return jsonify_model(instance)

    def delete(self, instance):
        instance.delete()
        return jsonify_model(instance)