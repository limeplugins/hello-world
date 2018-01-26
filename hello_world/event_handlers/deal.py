import logging
# import requests

logger = logging.getLogger(__name__)


def deal(worker, body, message):
    """Summarize your event handlers's functionality here"""
    logger.info('Received message: {}'.format(body))

    # requests.post('https://some.api/deals', json=body)

    message.ack()


def register_event_handlers(worker, config):
    worker.register_event_handler(
        handler_func=deal,
        key='hello-world.deal.created',
        queue_name='deal')
