import flask_restful
import flask_marshmallow
import lime_endpoints
import lime_endpoints.endpoints
import lime_webserver.webserver as webserver
import logging

URL_PREFIX = '/hello-world'

logger = logging.getLogger(__name__)

bp = lime_endpoints.endpoints.create_blueprint(
    'hello_world',
    __name__,
    URL_PREFIX)
api = flask_restful.Api(bp)
ma = flask_marshmallow.Marshmallow(bp)


class Greeting(webserver.LimeResource):
    """This is an example resource"""

    def get(self, limetype):
        LimeType = self.application.limetypes.get_limetype(limetype)

        return {
            'message': 'Hello, there are {} {} available'.format(
                LimeType.get_all().count, LimeType.localname.plural.lower()),
            'version': 'v0.0.1'
        }


api.add_resource(Greeting, '/greeting/<limetype>/')
