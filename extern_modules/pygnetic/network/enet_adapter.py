# -*- coding: utf-8 -*-
"""Module containing network adapter for enet."""

import logging
import enet
from .. import connection, server, client

_logger = logging.getLogger(__name__)


class Connection(connection.Connection):
    def __init__(self, parent, peer, message_factory, *args, **kwargs):
        super(Connection, self).__init__(parent, peer, message_factory,
                                         *args, **kwargs)
        self.peer = peer

    def __del__(self):
        self.peer.disconnect_now()

    def _send_data(self, data, channel=0, flags=enet.PACKET_FLAG_RELIABLE,
                   **kwargs):
        self.peer.send(channel, enet.Packet(data, flags))

    def disconnect(self, when=0):
        """Request a disconnection.

        when - type of disconnection
               0  - disconnect with acknowledge
               1  - disconnect after sending all messages
               -1 - disconnect without acknowledge
        """
        if when == 0:
            self.peer.disconnect()
        elif when == 1:
            self.peer.disconnect_later()
        else:
            self.peer.disconnect_now()

    @property
    def connected(self):
        """Connection state."""
        return self.peer.state == enet.PEER_STATE_CONNECTED

    @property
    def address(self):
        """Connection address."""
        address = self.peer.address
        return address.host, address.port


class Server(server.Server):
    def __init__(self, host='', port=0, con_limit=4, *args, **kwargs):
        super(Server, self).__init__(host, port, con_limit, *args, **kwargs)
        host = enet.Address(host, port)
        self.host = enet.Host(host, con_limit, *args, **kwargs)
        self._peer_cnt = 0

    def update(self, timeout=0):
        host = self.host
        event = host.service(timeout)
        while event is not None:
            if event.type == enet.EVENT_TYPE_CONNECT:
                peer_id = str(self._peer_cnt + 1)
                if self._accept(Connection, event.peer, event.peer.address,
                                peer_id, event.data):
                    event.peer.data = peer_id
                    self._peer_cnt += 1
                else:
                    event.peer.disconnect_now()
            elif event.type == enet.EVENT_TYPE_DISCONNECT:
                self._disconnect(event.peer.data)
            elif event.type == enet.EVENT_TYPE_RECEIVE:
                self._receive(event.peer.data, event.packet.data,
                    channel=event.channelID)
            event = host.check_events()

    @property
    def address(self):
        """Server address."""
        address = self.host.address
        return address.host, address.port


class Client(client.Client):
    def __init__(self, conn_limit=1, *args, **kwargs):
        super(Client, self).__init__(*args, **kwargs)
        self.host = enet.Host(None, conn_limit)
        self._peer_cnt = 0

    def _create_connection(self, host, port, message_factory, channels=1,
                           **kwargs):
        host = enet.Address(host, port)
        peer_id = self._peer_cnt = self._peer_cnt + 1
        peer_id = str(peer_id)
        peer = self.host.connect(host, channels, message_factory.get_hash())
        peer.data = peer_id
        connection = Connection(self, peer, message_factory)
        return connection, peer_id

    def update(self, timeout=0):
        if len(self.conn_map) == 0:
            return
        host = self.host
        event = host.service(timeout)
        while event is not None:
            if event.type == enet.EVENT_TYPE_CONNECT:
                self._connect(event.peer.data)
            elif event.type == enet.EVENT_TYPE_DISCONNECT:
                self._disconnect(event.peer.data)
            elif event.type == enet.EVENT_TYPE_RECEIVE:
                self._receive(event.peer.data, event.packet.data,
                              channel=event.channelID)
            event = host.check_events()
