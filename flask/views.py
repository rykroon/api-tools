import json 
from bson.objectid import ObjectId
from flask import abort, jsonify, request
from flask.views import MethodView
from pymongo.errors import InvalidId

from aux import jsonify_model


class ResourceView(MethodView):

    fields_kw = 'fields'
    sort_kw = 'sort'
    limit_kw = 'limit'
    default_limit = 10
    max_limit = 50
    offset_kw = 'offset'
    key_delimiter = ':'

    @property
    def _cls(self):
        return self.__class__

    def get_resource_by_id(self, id):
        """
            @returns: The resource associated with the id, else None
        """
        raise NotImplementedError

    def parse_query_args(self):
        request_args = request.args.to_dict()
        
        fields = request_args.pop(self._cls.fields_kw, None)
        if fields is not None:
            fields = fields.split(',')

        limit = request_args.pop(self._cls.limit_kw, self._cls.default_limit)
        limit = min(limit, self._cls.max_limit)

        offset = request_args.pop(self._cls.offset_kw, 0)

        sort = request_args.pop(self._cls.sort_kw, None)
        if sort is not None:
            sort = sort.split(',')

        qargs = {}

        for key, val in request_args.items():
            if self._cls.key_delimiter in key:
                key = tuple(key.split(self._cls.key_delimiter))

            qargs[key] = val

        return {
            self._cls.fields_kw: fields,
            self._cls.sort_kw: sort,
            self._cls.limit_kw: limit,
            self._cls.offset_kw: offset,
            'query_args': qargs
        }
        
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
            
        except InvalidId:
            return None 

        return self._cls.collection.find_one({'_id': object_id})
        
    def get(self, document=None):
        if document:
            return jsonify(document)
        else:
            documents = list(self._cls.collection.find(request.args))
            return jsonify(documents)

    def post(self):
        data = request.get_json()
        self._cls.collection.insert_one(data)
        return jsonify(data), 201

    def put(self, document):
        data = request.get_json()
        document.update(data)
        self._cls.collection.update_one(
            {'_id': document.get('_id')},
            {'$set': document}
        )
        return jsonify(document)

    def delete(self, document):
        self._cls.collection.delete_one({'_id': document.get('_id')})
        return jsonify(document)


class ModelView(ResourceView):
    model = None

    def get_resource_by_id(self, id):
        return self._cls.model.objects.get_by_id(id) 

    def get(self, instance=None):
        if instance:
            return jsonify_model(instance)
        else:
            results = self._cls.model.get_many(request.args)
            return jsonify(results)

    def post(self):
        instance = self._cls.model.from_json(request.data)
        instance.save()
        return jsonify_model(instance), 201

    def put(self, instance):
        data = json.loads(request.data, cls=self._cls.model.json_decoder)
        for k, v in data.items():
            setattr(instance, k, v)

        instance.save()
        return jsonify_model(instance)

    def delete(self, instance):
        instance.delete()
        return jsonify_model(instance)