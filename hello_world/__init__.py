#
# The content of this dict shows up as values that can be configured for
# whatever application is using this lib.
#
# These values can be retrieved with:
#
#   lime_config.config.mysection.myparam
#
DEFAULT_CONFIG = {
    'mysection': {
        'myparam':  'my default value'
    }
}


def register_blueprint(app, config=None):
    from .endpoints import bp
    app.register_blueprint(bp)
