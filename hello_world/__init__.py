import logging

logger = logging.getLogger(__name__)


def default_config():
    return {
        'todo_note_text': ('Follow up {deal.properties.name.value} with '
                           '{company.properties.name.value}'),
        'events': {
            'call_api': False,
            'api_url': 'https://example.com/foo'
        }
    }


try:
    from .endpoints import register_blueprint  # noqa
except ImportError:
    logger.info('hello_world doesn\'t implement any custom endpoints')

try:
    from .event_handlers import register_event_handlers  # noqa
except ImportError:
    logger.info('hello_world doesn\'t implement any event handlers')
