from bson.objectid import ObjectId
from flask import abort, jsonify, request
from flask.views import MethodView
from pymongo.errors import InvalidId


class ResourceView(MethodView):

    def get_resource_by_id(self, id):
        """
            @returns: The resource associated with the id, else None
        """
        raise NotImplementedError

    def dispatch_request(self, *args, **kwargs):
        if request.method in ('POST', 'PUT'):
            data = request.get_json() #use request.get_data(as_text=True), then do json.loads()
            if data is None:
                abort(400)

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
        
    def get(self, doc=None):
        if doc:
            return jsonify(doc)
        else:
            return jsonify(list(self.__class__.collection.find(request.args)))

    def post(self):
        data = request.get_json()
        self.__class__.collection.insert_one(data)
        return jsonify(data), 201

    def put(self, doc):
        data = request.get_json()
        doc.update(**data)
        self.__class__.update_one(
            {'_id': doc.get('_id')},
            {'$set': doc}
        )
        return jsonify(doc)

    def delete(self, doc):
        self.__class__.collection.delete_one({'_id': doc.get('_id')})
        return jsonify(doc)


class ModelView(ResourceView):
    model = None

    @property
    def _model(self):
        self.__class__.model

    def get_resource_by_id(self, id):
        return self._model.get(id)

    def get(self, instance=None):
        if instance:
            return jsonify(instance.to_dict())
        else:
            results = self._model.objects.find(request.args)
            return jsonify(results)

    def post(self):
        data = request.get_json()
        instance = self._model(**data)
        instance.save()
        return jsonify(instance.to_dict()), 201

    def put(self, instance):
        data = request.get_json()
        instance.update(data)
        instance.save()
        return jsonify(instance.to_dict())

    def delete(self, instance):
        instance.delete()
        return jsonify(instance.to_dict())