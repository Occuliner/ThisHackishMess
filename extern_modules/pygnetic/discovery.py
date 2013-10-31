import logging
import socket
import select
import threading
import SocketServer
from collections import OrderedDict
from itertools import islice
import message

_logger = logging.getLogger(__name__)

message_factory = message.MessageFactory()

register = message_factory.register('register', (
    'oid', 'name', 'port'
))
get_servers = message_factory.register('get_servers', (
    'oid', 'current', 'part_size'
))
ping = message_factory.register('ping', (
    'oid', 'sid'
))
response = message_factory.register('response', (
    'oid', 'mid', 'value', 'error'
))


class Errors(object):
    NO_ERROR = 0
    TIMEOUT = 1


class ServerHandler(SocketServer.BaseRequestHandler, object):
    def handle(self):
        data, socket = self.request
        _logger.debug('Received data: %r', data)
        message = message_factory.unpack(data)
        if message is None:
            return
        name = message.__class__.__name__
        _logger.info('Received %s message from %s', name, self.client_address)
        ret_val, err = getattr(self, 'net_' + name)(message)
        mid = message_factory.get_type_id(message.__class__)
        ack_data = message_factory.pack(response(message.oid, mid, ret_val, err))
        cnt = socket.sendto(ack_data, self.client_address)
        _logger.info('Sent response to %s', self.client_address)
        _logger.debug('Sent %d bytes: %r', cnt, ack_data)

    def unknown_msg(self, message):
        name = message.__class__.__name__
        _logger.warning('Received unknown %s message from %s',
                        name, self.client_address)

    def net_register(self, message):
        sid = self.server.id_cnt = self.server.id_cnt + 1
        self.server.servers[sid] = [(message.name, self.client_address[0], message.port), 0]
        return sid, Errors.NO_ERROR

    def net_get_servers(self, message):
        s = message.current * message.part_size
        e = s + message.part_size
        servers = self.server.servers
        d = {k: servers[k][0] for k in islice(servers.iterkeys(), s, e)}
        return d, Errors.NO_ERROR

    def net_ping(self, message):
        s = self.server.servers.get(message.sid)
        if s is not None:
            s[1] = 0
            return None, Errors.NO_ERROR
        else:
            return None, Errors.TIMEOUT


class DiscoveryServer(SocketServer.UDPServer, object):
    allow_reuse_address = True
    max_packet_size = 8192
    cleaner_period = 10
    ping_timeout = 6

    def __init__(self, host='', port=5000):
        super(DiscoveryServer, self).__init__((host, port), ServerHandler)
        self.servers = OrderedDict()
        self.id_cnt = 0
        self.c_stop = threading.Event()
        self.c_thread = threading.Thread(target=self.cleaner)
        self.c_thread.daemon = True
        self.c_thread.start()

    def __del__(self):
        self.c_stop.set()

    def cleaner(self):
        while not self.c_stop.is_set():
            keys = []
            for k, v in self.servers.iteritems():
                v[1] += 1
                if v[1] > self.ping_timeout:
                    keys.append(k)
            for k in keys:
                del self.servers[k]
            self.c_stop.wait(self.cleaner_period)


class DiscoveryClient(object):
    max_packet_size = 8192

    def __init__(self, host, port=5000):
        self.address = socket.gethostbyname(host), port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.response = None
        self.callbacks = {}
        self.default_callback = lambda r: None
        self.oid = 0

    def _send_msg(self, message_cls, *args):
        oid = self.oid = self.oid + 1
        data = message_factory.pack(message_cls(oid, *args))
        cnt = self.socket.sendto(data, self.address)
        self.response = None
        _logger.info('Sent %s message to %s', message_cls.__name__, self.address)
        _logger.debug('Sent %d bytes: %r', cnt, data)
        return oid

    def update(self, timeout=0):
        r = select.select([self.socket], [], [], timeout / 1000.0)[0]
        # sending to closed socket puts some data in receive buffer causing
        # error while calling recvfrom
        if len(r) > 0:
            try:
                data, address = self.socket.recvfrom(self.max_packet_size)
            except Exception as e:
                _logger.debug('Error: %s', e)
                return
            if address == self.address:
                _logger.debug('Received data: %r', data)
                r = self.response = message_factory.unpack(data)
                if r.__class__ != response:
                    return
                _logger.info('Received response from %s', address)
                self.callbacks.pop(r.oid, self.default_callback)(r)
            else:
                _logger.info('Unexpected data from %s', address)

    def close(self):
        self.socket.close()

    def add_callback(self, oid, callback):
        if callback is not None and callable(callback):
            self.callbacks[oid] = callback
        if len(self.callbacks) > 10:
            keep = sorted(self.callbacks.iterkeys())[:-10]
            self.callbacks = {k: v for k, v in self.callbacks.iter(keep)}

    def register(self, name, port):
        return self._send_msg(register, name, port)

    def ping(self, sid):
        return self._send_msg(ping, sid)

    def get_servers(self, current=0, part_size=10):
        return self._send_msg(get_servers, current, part_size)
