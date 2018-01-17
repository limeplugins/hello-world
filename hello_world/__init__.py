import logging

logger = logging.getLogger(__name__)


try:
    from .endpoints import register_blueprint  # noqa
except ImportError:
    logger.info('hello_world doesn\'t implement any custom endpoints')

try:
    from .event_handlers import register_event_handlers  # noqa
except ImportError:
    logger.info('hello_world doesn\'t implement any event handlers')
