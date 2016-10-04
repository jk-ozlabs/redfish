

import collections
import json

def join_ids(a, b):
    c = ''
    if not a.endswith('/'):
        c = '/'
    return a + c + b

idregistry = {}

class ODataProperty(object):
    def __init__(self, name, nav=False):
        self.name = name
        self.python_name = name.lower()
        self.nav = nav

    def __repr__(self):
        return '<Property %s>' % self.name

    def json_repr(self, obj):
        if self.nav:
            return { '@odata.id': join_ids(obj._odata_id, self.name) }
        return getattr(obj, self.python_name, None)

class ODataCollectionProperty(ODataProperty):

    def __init__(self, name, nav=False, type=None):
        self.name = name
        self.python_name = name.lower()
        self.nav = nav
        self.collection_type = type

    def __repr__(self):
        return '<CollectionProperty %s>' % self.name

class ODataObject(object):

    def __init__(self):
        self._odata_init()

    def _odata_init(self):
        self._meta = getattr(self, 'Meta')()
        self._meta.properties = collections.OrderedDict()
        for name in dir(self.ODataProperties):
            val = getattr(self.ODataProperties, name)

            if not isinstance(val, ODataProperty):
                continue

            # add to our properties collection
            self._meta.properties[name] = val

            # set a default value if None exists
            if name in dir(self):
                continue
            if isinstance(val, ODataCollectionProperty):
                collection = ODataCollection()
                collection._meta.type = val.collection_type
                setattr(self, name, collection)
            else:
                setattr(self, name, None)

    def assign_ids(self, parent, ctx):
        global idregistry
        if getattr(self, '_odata_id', None) is None:
            self._odata_id = join_ids(parent._odata_id, ctx)
            self.id = ctx
            idregistry[self._odata_id] = self
        for prop in self._meta.properties.values():
            value = getattr(self, prop.python_name, None)
            if isinstance(value, ODataObject):
                value.assign_ids(self, prop.name)

    def to_json_dict(self):
        d = {}
        for prop in self._meta.properties.values():
            val = prop.json_repr(self)
            if val is None:
                continue
            d[prop.name] = val
        return d

class ODataCollection(ODataObject, list):

    def assign_ids(self, parent, ctx):
        global idregistry
        self._odata_id = join_ids(parent._odata_id, ctx)
        idregistry[self._odata_id] = self
        for key, value in enumerate(self):
            if isinstance(value, ODataObject):
                value.assign_ids(self, str(key))

    def to_json_dict(self):
        return {
            'Members@odata.count': self.__len__(),
            'Members': [
                { '@odata.id': v._odata_id for v in self }
             ]
        }

    class Meta:
        pass

    class ODataProperties:
        pass

class ODataAction(object):
    pass

def odata_json_encode(obj, context=None):
    def json_handler(obj):
        if isinstance(obj, ODataObject):
            return obj.to_json_dict()
        raise TypeError(repr(obj) + " is not JSON serialisable")
    d = {
        '@odata.type': '#' + obj._meta.type,
    }
    if context is not None:
        d.update({'@odata.context': '/redfish/v1/$metadata#' + context})
    d.update(obj.to_json_dict())
    return json.dumps(d, indent=2, default=json_handler) + '\n'

def action(action_class):
    def wrapper(fn):
        print 'fn', fn, fn.func_closure
        return fn
    return wrapper
