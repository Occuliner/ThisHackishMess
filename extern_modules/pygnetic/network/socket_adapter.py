# -*- coding: utf-8 -*-
"""Module containing network adapter for socket (asyncore.dispacher)."""

import logging
import socket
import struct
import asyncore
from collections import deque
from .. import connection, server, client
from .._utils import lazyproperty

_logger = logging.getLogger(__name__)
_connect_struct = struct.Struct('!I')


class Dispacher(asyncore.dispatcher, object):
    pass


class Connection(connection.Connection, Dispacher):
    # maximum amount of data received / sent at once
    recv_buffer_size = 4096

    def __init__(self, parent, socket, message_factory, *args, **kwargs):
        super(Connection, self).__init__(
            parent, socket, message_factory,
            socket, None,
            * args, **kwargs)
        #self.send_queue = deque()
        self.send_buffer = bytearray()
        #self.recv_buffer = bytearray(b'\0' * self.recv_buffer_size)

    def _send_data(self, data, **kwargs):
        self.send_buffer.extend(data)
        self._send_part()

#    def _send_data2(self, data, **kwargs):
#        if len(self.send_buffer) == 0:
#            self.send_buffer = data
#        else:
#            self.send_queue.append(data)
#        self._send_part()

    def handle_write(self):
        self._send_part()

    def _send_part(self):
        try:
            num_sent = asyncore.dispatcher.send(self, self.send_buffer)
        except socket.error:
            self.handle_error()
            return
        self.send_buffer = self.send_buffer[num_sent:]

    def writable(self):
        return (not self.connected) or len(self.send_buffer)

    def handle_read(self):
        data = self.recv(self.recv_buffer_size)
        if data:
            self._receive(data)

#    def handle_read2(self):
#        # tinkering with dispatcher internal variables,
#        # because it doesn't support socket.recv_into
#        try:
#            num_rcvd = self.socket.recv_into(self.recv_buffer)
#            if not num_rcvd:
#                self.handle_close()
#            else:
#                self._receive(self.recv_buffer[:num_rcvd])
#        except socket.error, why:
#            if why.args[0] in asyncore._DISCONNECTED:
#                self.handle_close()
#            else:
#                self.handle_error()
#            return

    def handle_connect(self):
        self._connect()

    def handle_close(self):
        self._disconnect()
        self.close()

    def log_info(self, message, type='info'):
        return getattr(_logger, type)(message)

    def disconnect(self, *args):
        self._disconnect()
        self.close()

    @lazyproperty
    def address(self):
        return self.socket.getpeername()


class Server(server.Server, Dispacher):
    connection = Connection

    def __init__(self, host='', port=0, conn_limit=4, handler=None, message_factory=None, *args, **kwargs):
        super(Server, self).__init__(
            host, port, conn_limit,  handler, message_factory,
            None, None,
            *args, **kwargs)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        # disable Nagle buffering algorithm
        self.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(conn_limit)

    def _create_connection(self, socket, message_factory):
        connection = Connection(self, socket, message_factory)
        return connection, socket.fileno()

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            # TODO: sth better?
            sock.settimeout(0.5) # enable blocking read with 0.5s timeout
            try:
                data = sock.recv(4) # wait for hash data
                mf_hash = _connect_struct.unpack(data)[0]
                sock.setblocking(0) # disable blocking read
                if self._accept(sock, addr, mf_hash):
                    return # end if hash is correct
            except socket.timeout:
                _logger.info('Connection with %s refused, MessageFactory'
                                ' hash not received', addr)
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()

    def update(self, timeout=0):
        asyncore.loop(timeout / 1000.0, False, None, 1)

    @lazyproperty
    def address(self):
        return self.socket.getsockname()


class Client(client.Client):
    def __init__(self, conn_limit=0, *args, **kwargs):
        super(Client, self).__init__(*args, **kwargs)
        self._sock_cnt = 0

    def _create_connection(self, host, port, message_factory, **kwargs):
        connection = Connection(self, None, message_factory)
        connection.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        # disable Nagle buffering algorithm
        connection.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        connection.connect((host, port))
        connection._send_data(_connect_struct.pack(message_factory.get_hash()))
        return connection, connection.socket.fileno()

    def update(self, timeout=0):
        asyncore.poll(timeout / 1000.0, self.conn_map)
