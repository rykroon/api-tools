from bson.objectid import ObjectId
from flask import abort, jsonify, request
from flask.views import MethodView
from pymongo.errors import InvalidId


class ResourceView(MethodView):

    def get_resource_by_id(self, id):
        """
            @returns: The resource associated with the id, else None
        """
        raise NotImplementedError()

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
        
    def get(self, doc=None):
        if doc:
            return jsonify(doc)
        else:
            return jsonify(list(self.__class__.collection.find(request.args)))

    def post(self):
        doc = request.get_json()
        self.__class__.collection.insert_one(doc)
        return jsonify(doc), 201

    def put(self, doc):
        doc.update(**request.get_json())
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

    def get_resource_by_id(self, id):
        pass

    def get(self, id=None):
        pass

    def post(self):
        pass

    def put(self, id):
        pass

    def delete(self, id):
        pass