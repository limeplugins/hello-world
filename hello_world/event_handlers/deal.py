import logging
import requests
import lime_config

logger = logging.getLogger(__name__)


def deal(worker, body, message):
    """Summarize your event handlers's functionality here"""
    logger.info('Received message: {}'.format(body))

    if lime_config.config.plugins.hello_world.events.call_api:
        requests.post(lime_config.config.plugins.hello_world.events.api_url,
                      json=body)
    else:
        logger.info('Calling external api is disabled in config')

    message.ack()


def register_event_handlers(worker, config):
    worker.register_event_handler(
        handler_func=deal,
        key='hello-world.deal.created',
        queue_name='deal')
