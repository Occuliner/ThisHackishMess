# -*- coding: utf-8 -*-
"""Module containing MessageFactory and predefined messages"""

import logging
from collections import namedtuple
from weakref import WeakKeyDictionary, WeakValueDictionary
import serialization

_logger = logging.getLogger(__name__)


class MessageFactory(object):
    """Class allowing to register new message types and pack/unpack them.

    :param s_adapter:
        :term:`serialization adapter`
        (default: None - module selected with :func:`.init`)
    """
    def __init__(self, s_adapter=None):
        self._message_names = {}  # name -> message
        self._message_types = WeakValueDictionary()  # type_id -> message
        self._message_params = WeakKeyDictionary()  # message -> type_id, send kwargs
        if s_adapter is None:
            self.s_adapter = serialization
        else:
            self.s_adapter = s_adapter
        self._type_id_cnt = 0
        self._frozen = False
        self._hash = None

    def register(self, name, field_names=tuple(), **kwargs):
        """Register new message type.

        :param name: name of message class
        :param field_names: list of names of message fields
        :param kwargs: additional keyword arguments for send method
        :return: message class (namedtuple)
        """
        if self._frozen == True:
            _logger.warning("Can't register new messages after connection "
                            "establishment")
            return
        type_id = self._type_id_cnt = self._type_id_cnt + 1
        packet = namedtuple(name, field_names)
        self._message_names[name] = packet
        self._message_types[type_id] = packet
        self._message_params[packet] = (type_id, kwargs)
        return packet

    def pack(self, message):
        """Pack data to string.

        :param message: object of class created by register
        :return: string
        """
        type_id = self.get_type_id(message.__class__)
        message = (type_id,) + message
        data = self.s_adapter.pack(message)
        _logger.debug("Packing message (length: %d)", len(data))
        return data

    def set_frozen(self):
        """Disable ability to register new messages to allow generation
        of hash.
        """
        self._frozen = True

    def reset_context(self, context):
        """Prepares object to behave as context for stream unpacking.

        :param context: object which will be prepared
        """
        context._unpacker = self.s_adapter.unpacker()

    def _process_message(self, message):
        try:
            type_id = message[0]
            return self._message_types[type_id](*message[1:])
        except KeyError:
            _logger.error('Unknown message type_id: %s', type_id)
        except:
            _logger.error('Message unpacking error: %s', message)

    def unpack(self, data):
        """Unpack message from string.

        :param data: packed message data as a string
        :return: message
        """
        _logger.debug("Unpacking message (length: %d)", len(data))
        message = self.s_adapter.unpack(data)
        if message is not None:
            return self._process_message(message)
        else:
            _logger.error('Data corrupted')
            _logger.debug('Data: %r', data)

    def unpack_all(self, data, context):
        """Feed unpacker with data from stream and unpack all messages.

        :param data: packed message(s) data as a string
        :param context: object previously prepared with :meth:`reset_context`
        :return: iterator over messages
        """
        _logger.debug("Unpacking data (length: %d)", len(data))
        context._unpacker.feed(data)
        try:
            for message in context._unpacker:
                yield self._process_message(message)
        except:
            _logger.error('Data corrupted')
            self._reset_unpacker()  # prevent from corrupting next data
            return

    def get_by_name(self, name):
        """Returns message class with given name.

        :param name: name of message
        :return: message class (namedtuple)
        """
        try:
            return self._message_names[name]
        except KeyError:
            raise ValueError('Unknown message name')


    def get_by_type(self, type_id):
        """Returns message class with given type_id.

        :param type_id: type identifier of message
        :return: message class (namedtuple)
        """
        try:
            return self._message_types[type_id]
        except KeyError:
            raise ValueError('Unknown message type_id')

    def get_params(self, message_cls):
        """Return dict containing sending keyword arguments

        :param message_cls: message class created by register
        :return: dict
        """
        try:
            return self._message_params[message_cls][1]
        except KeyError:
            raise ValueError('Unregistered message')

    def get_type_id(self, message_cls):
        """Return message class type_id

        :param message_cls: message class created by register
        :return: int
        """
        try:
            return self._message_params[message_cls][0]
        except KeyError:
            raise ValueError('Unregistered message')

    def get_hash(self):
        """Calculate and return hash.

        Hash depends on registered messages and used serializing library.

        :return: int
        """
        if self._frozen:
            if self._hash is None:
                ids = self._message_types.keys()
                ids.sort()
                l = list()
                a = getattr(self.s_adapter, 'selected_adapter', self.s_adapter)
                l.append(a.__name__)
                for i in ids:
                    p = self._message_types[i]
                    l.append((i, p.__name__, p._fields))
                # should be the same on 32 & 64 platforms
                self._hash = hash(tuple(l)) & 0xffffffff
            return self._hash
        else:
            _logger.warning('Attempt to get hash of not frozen MessageFactory')


message_factory = MessageFactory()
#update_remoteobject = message_factory.register('update_remoteobject', (
#    'type_id',
#    'obj_id',
#    'variables'
#), channel=1, flags=0)
