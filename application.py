
import json
from odata import odata_json_encode
from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple as _run_simple
from werkzeug.routing import Map, Rule, NotFound, RequestRedirect
from werkzeug.exceptions import HTTPException

run_simple = _run_simple

class RedfishApplication(object):
    def __init__(self, registry):
        self.odata_registry = registry
        self.url_map = Map([
            Rule('/redfish/v1/', endpoint=self.odata_root),
            Rule('/redfish/v1/<path:odata_id>', endpoint=self.odata_object),
        ])

    def dispatch_request(self, request):
        adapter = self.url_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
            return endpoint(request, **values)
        except NotFound, e:
            return self.error_404()
        except HTTPException, e:
            return e

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)

    # views
    def error_404(self):
        response = Response("Not found")
        response.status_code = 404
        return response

    def odata_root(self, request):
        return self.odata_object(request, None)

    def odata_object(self, request, odata_id):
        key = '/redfish/v1/'
        if odata_id is not None:
            key += odata_id
        if key not in self.odata_registry.keys():
            return self.error_404()
        obj = self.odata_registry[key]
        response = Response(odata_json_encode(obj), mimetype='application/json')
        return response

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)
