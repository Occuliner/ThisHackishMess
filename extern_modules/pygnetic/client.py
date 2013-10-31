# -*- coding: utf-8 -*-
"""Module containing base class for adapters representing network clients."""

import logging
import message
import network

_logger = logging.getLogger(__name__)


class Client(object):
    """Base class representing network client.

    :param int con_limit: maximum amount of created connections (default: 1)
    :param message_factory: custom instance of :class:`~.message.MessageFactory`
       (default: :attr:`.Client.message_factory`)
    :param args: additional arguments for :term:`network adapter`
    :param kwargs: additional keyword arguments for :term:`network adapter`
    """
    message_factory = message.message_factory

    def __init__(self, conn_limit=1, message_factory=None, *args, **kwargs):
        super(Client, self).__init__(*args, **kwargs)
        self.conn_map = {}
        if message_factory is not None:
            self.message_factory = message_factory
        _logger.info('Client created, connections limit: %d', conn_limit)

    def connect(self, host, port, message_factory=None, **kwargs):
        """Connects to specified address.

        :param string host: IP address or name of host
        :param int port: port of host
        :param message_factory:
            :class:`~message.MessageFactory` used for new connection
            (default: :attr:`message_factory`)
        :param kwargs: additional keyword arguments for :term:`network adapter`
        :return: new :class:`~.connection.Connection`
        """
        if message_factory is None:
            message_factory = self.message_factory
        _logger.info('Connecting to %s:%d', host, port)
        message_factory.set_frozen()
        connection, c_key = self._create_connection(host, port,
            message_factory, **kwargs)
        self.conn_map[c_key] = connection
        connection._key = c_key
        return connection

    def update(self, timeout=0):
        """Process network traffic and update connections.

        :param int timeout:
            waiting time for network events in milliseconds
            (default: 0 - no waiting)
        """
        raise NotImplementedError('Should be implemented by adapter class')

    def _get(self, c_key):
        return self.conn_map[c_key]

    def _remove(self, c_key):
        del self.conn_map[c_key]

    def _create_connection(self, host, port, message_factory, **kwargs):
        raise NotImplementedError('Should be implemented by adapter class')
