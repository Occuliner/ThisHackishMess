# -*- coding: utf-8 -*-
"""Module containing base class for adapters representing network clients."""

import logging
import message

_logger = logging.getLogger(__name__)


class Client(object):
    """Class representing network client.

    :param int con_limit: maximum amount of created connections (default: 1)
    :param args: additional arguments for :term:`network adapter`
    :param kwargs: additional keyword arguments for :term:`network adapter`
    """
    message_factory = message.message_factory

    def __init__(self, conn_limit=1, *args, **kwargs):
        super(Client, self).__init__(*args, **kwargs)
        self.conn_map = {}
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
        connection, c_id = self._create_connection(host, port,
            message_factory, **kwargs)
        self.conn_map[c_id] = connection
        return connection

    def update(self, timeout=0):
        """Process network traffic and update connections.

        :param int timeout:
            waiting time for network events in milliseconds
            (default: 0 - no waiting)
        """
        pass

    def _connect(self, c_id):
        self.conn_map[c_id]._connect()

    def _disconnect(self, c_id):
        self.conn_map[c_id]._disconnect()
        del self.conn_map[c_id]

    def _receive(self, c_id, data, **kwargs):
        self.conn_map[c_id]._receive(data, **kwargs)
