import logging
import pkgutil
import importlib

logger = logging.getLogger(__name__)


def register_event_handlers(worker, config):
    for loader, module_name, is_pkg in pkgutil.walk_packages(__path__):
        if module_name.endswith('_test'):
            continue
        module_fullname = '{}.{}'.format(__name__, module_name)
        logger.info('Loading {}'.format(module_fullname))
        module = importlib.import_module(module_fullname)

        if hasattr(module, 'register_event_handlers'):
            module.register_event_handlers(worker, config)
