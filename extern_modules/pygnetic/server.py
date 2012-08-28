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
    :param args: additional arguments for :term:`network adapter`
    :param kwargs: additional keyword arguments for :term:`network adapter`
    """
    message_factory = message.message_factory
    handler = None

    def __init__(self, host='', port=0, conn_limit=4, *args, **kwargs):
        super(Server, self).__init__(*args, **kwargs)
        _logger.info('Server created %s:%d, connections limit: %d',
                     host, port, conn_limit)
        self.message_factory.set_frozen()
        self.conn_map = {}
        self.conn_limit = conn_limit

    def update(self, timeout=0):
        """Process network traffic and update connections.

        :param int timeout:
            waiting time for network events in milliseconds
            (default: 0 - no waiting)
        """
        pass

    def _accept(self, connection, socket, address, c_id, mf_hash):
        if mf_hash == self.message_factory.get_hash():
            _logger.info('Connection with %s accepted', address)
            conn = connection(self, socket, self.message_factory)
            if self.handler is not None and issubclass(self.handler, Handler):
                handler = self.handler()
                handler.server = proxy(self)
                conn.add_handler(handler)
            self.conn_map[c_id] = conn
            event.accepted(self)
            conn._connect()
            return True
        else:
            _logger.info('Connection with %s refused, MessageFactory'\
                            ' hash incorrect', address)
            return False

    def _disconnect(self, c_id):
        conn = self.conn_map.get(c_id)
        if conn is not None:
            conn._disconnect()
            del self.conn_map[c_id]

    def _receive(self, c_id, data, **kwargs):
        self.conn_map[c_id]._receive(data, **kwargs)

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

    @property
    def address(self):
        """Server address."""
        return None, None
