# -*- coding: utf-8 -*-
"""
Module containing base class for adapters representing network connections.
"""

import re
import logging
from weakref import proxy
from functools import partial
import event

_logger = logging.getLogger(__name__)


class Connection(object):
    """Class allowing to send messages

    :param parent: parent :class:`~.client.Client` or :class:`~.server.Server`
    :param conn_obj: connection object
    :param message_factory: :class:`~.message.MessageFactory` object
    """
    address = ('', '') # \
    connected = False  # / default values, should be overridden by adapter class
    __id_cnt = 0

    def __init__(self, parent, conn_obj, message_factory, *args, **kwargs):
        super(Connection, self).__init__(*args, **kwargs)
        self.parent = proxy(parent)
        self.message_factory = message_factory
        self.message_factory.reset_context(self)
        self.handlers = []
        self.data_sent = 0
        self.data_received = 0
        self.messages_sent = 0
        self.messages_received = 0
        self.id = self.__class__.__id_cnt = self.__id_cnt + 1
        self._key = None

    def __getattr__(self, name):
        parts = name.split('_', 1)
        if (len(parts) == 2 and parts[0] == 'net' and
                parts[1] in self.message_factory._message_names):
            p = partial(self._send_message,
                self.message_factory.get_by_name(parts[1]))
            p.__doc__ = "Send %s message to remote host\n\nHost.net_%s" % (
                parts[1],
                self.message_factory._message_names[parts[1]].__doc__)
            # add new method so __getattr__ is no longer needed
            setattr(self, name, p)
            return p
        else:
            raise AttributeError("'%s' object has no attribute '%s'" %
                                 (type(self).__name__, name))

    def send(self, message, *args, **kwargs):
        """Send message to remote host.

        :param message:
            class created by :meth:`~.message.MessageFactory.register`
            or message name
        :param args: parameters used to initialize message object
        :param kwargs: keyword parameters used to initialize message object
        """
        if isinstance(message, basestring):
            message = self.message_factory.get_by_name(message)
        self._send_message(message, *args, **kwargs)

    def _send_message(self, message, *args, **kwargs):
        name = message.__name__
        params = self.message_factory.get_params(message)
        try:
            message_ = message(*args, **kwargs)
        except TypeError, e:
            e, f = re.findall(r'[^_a-z](\d+)', e.message, re.I)
            raise TypeError('%s takes exactly %d arguments (%d given)' %
                (message.__doc__, int(e) - 1, int(f) - 1))
        data = self.message_factory.pack(message_)
        _logger.info('#%s Sent %s message', self.id, name)
        self.data_sent += len(data)
        self.messages_sent += 1
        return self._send_data(data, **params)

    def _send_data(self, data, channel=0, **kwargs):
        raise NotImplementedError('Should be implemented by adapter class')

    def _receive(self, data, **kwargs):
        self.data_received += len(data)
        for message in self.message_factory.unpack_all(data, self):
            self.messages_received += 1
            name = message.__class__.__name__
            _logger.info('#%s Received %s message', self.id, name)
            event.received(self, message)
            for h in self.handlers:
                getattr(h, 'net_' + name, h.on_recive)(message, **kwargs)

    def _connect(self):
        _logger.info('#%s Connected to %s', self.id, self.address)
        event.connected(self)
        for h in self.handlers:
            h.on_connect()

    def _disconnect(self):
        _logger.info('#%s Disconnected from %s', self.id, self.address)
        event.disconnected(self)
        for h in self.handlers:
            h.on_disconnect()
        self.parent._remove(self._key)

    def disconnect(self, *args):
        """Request a disconnection.

        :param args: additional arguments for :term:`network adapter`
        """
        raise NotImplementedError('Should be implemented by adapter class')

    def add_handler(self, handler):
        """Add new Handler to handle messages.

        :param handler: instance of :class:`~.handler.Handler` subclass
        """
        self.handlers.append(handler)
        handler.connection = proxy(self)
