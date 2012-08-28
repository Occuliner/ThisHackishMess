# -*- coding: utf-8 -*-
"""Network library for Pygame."""

import logging
import message
import network
import serialization
from handler import Handler
from network import Server, Client

__version__ = '1.0'
_logger = logging.getLogger(__name__)
register = message.message_factory.register


def init(events=False, event_val=1, logging_lvl=logging.INFO,
         n_module=('enet', 'socket'), s_module=('msgpack', 'json')):
    """Initialize network library.

    :param events: allow sending Pygame events (default False)
    :param event_val:
        set :const:`event.NETWORK` as
        :const:`pygame.USEREVENT` + :attr:`event_val` (default: 1)
    :param logging_lvl:
        level of logging messages (default :const:`logging.INFO`
        (see: :ref:`logging-basic-tutorial`), None to skip initializing
        logging module)
    :param n_module:
        name(s) of network library, first available will be used
        (default: ['enet', 'socket'])
    :type n_module: string or list of strings
    :param s_module:
        name(s) of serialization library, first available will be used
        (default: ['msgpack', 'json'])
    :type s_module: string or list of strings
    :return: True if initialization ended with success

    .. note::
        Because of the dynamic loading of network library adapter,
        :class:`Client` and :class:`Server` classes will only be
        available after initialization.
    """
    global _network_module, _serialization_module
    if logging_lvl is not None:
        logging.basicConfig(level=logging_lvl,
                            format='%(asctime)-8s %(levelname)-8s %(message)s',
                            datefmt='%H:%M:%S')
    network.select_adapter(n_module)
    if network.selected_adapter is not None:
        _logger.info("Using %s",
            network.selected_adapter.__name__.split('.')[-1])
    else:
        _logger.critical("Can't find any network module")
        return False
    serialization.select_adapter(s_module)
    if serialization.selected_adapter is not None:
        _logger.info("Using %s",
            serialization.selected_adapter.__name__.split('.')[-1])
    else:
        _logger.critical("Can't find any serialization module")
        return False
    if events:
        _logger.info("Enabling pygame events")
        import event
        event.init(event_val)
    return True
