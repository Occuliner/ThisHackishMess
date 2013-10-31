# -*- coding: utf-8 -*-
"""Module containing base class for adapters representing network servers."""

import logging
from weakref import proxy
import message
import event
from handler import Handler

_logger = logging.getLogger(__name__)


class Server(object):
    """Class representing network server.

    :param string host: IP address or name of host (default: "" - any)
    :param int port: port of host (default: 0 - any)
    :param int con_limit: maximum amount of created connections (default: 4)
    :param handler: custom :class:`~.handler.Handler` derived class
       (default: :attr:`.Server.handler`)
    :param message_factory: custom instance of :class:`~.message.MessageFactory`
       (default: :attr:`.Server.message_factory`)
    :param args: additional arguments for :term:`network adapter`
    :param kwargs: additional keyword arguments for :term:`network adapter`
    """
    address = ('', '')
    message_factory = message.message_factory
    handler = None

    def __init__(self, host='', port=0, conn_limit=4, handler=None,
                 message_factory=None, *args, **kwargs):
        super(Server, self).__init__(*args, **kwargs)
        _logger.info('Server created %s:%d, connections limit: %d',
                     host, port, conn_limit)
        self.message_factory.set_frozen()
        self.conn_map = {}
        self.conn_limit = conn_limit
        if handler is not None:
            self.handler = handler
            _logger.debug("Using %s handler", handler.__name__)
        if message_factory is not None:
            self.message_factory = message_factory

    def update(self, timeout=0):
        """Process network traffic and update connections.

        :param int timeout:
            waiting time for network events in milliseconds
            (default: 0 - no waiting)
        """
        raise NotImplementedError('Should be implemented by adapter class')

    def _create_connection(self, socket, message_factory):
        raise NotImplementedError('Should be implemented by adapter class')

    def _accept(self, socket, address, mf_hash):
        if mf_hash == self.message_factory.get_hash():
            _logger.info('Connection with %s accepted', address)
            connection, c_key = self._create_connection(socket,
                    self.message_factory)
            if self.handler is not None and issubclass(self.handler, Handler):
                handler = self.handler()
                handler.server = proxy(self)
                connection.add_handler(handler)
            else:
                _logger.error('xxx') # TODO
            self.conn_map[c_key] = connection
            connection._key = c_key
            event.accepted(self)
            connection._connect()
            return True
        else:
            _logger.info('Connection with %s refused, MessageFactory'
                            ' hash incorrect', address)
            return False

    def _get(self, c_key):
        return self.conn_map[c_key]

    def _remove(self, c_key):
        del self.conn_map[c_key]

    def connections(self, exclude=None):
        """Returns iterator over connections.

        :param exclude: list of connections to exclude
        :return:
            iterator over
            :class:`connections <.connection.Connection>`
        """
        if exclude is None:
            return self.conn_map.itervalues()
        else:
            return (c for c in self.conn_map.itervalues() if c not in exclude)

    def handlers(self, exclude=None):
        """Returns iterator over handlers.

        :param exclude: list of connections to exclude
        :return:
            iterator over
            :class:`handlers <.handler.Handler>`
        """
        if exclude is None:
            return (c.handlers[0] for c in self.conn_map.itervalues())
        else:
            return (c.handlers[0] for c in self.conn_map.itervalues()
                    if c not in exclude)
