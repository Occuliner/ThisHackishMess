# -*- coding: utf-8 -*-
"""Module defining Pygame events."""

__all__ = ('NETWORK',
           'NET_DISCONNECTED',
           'NET_CONNECTED',
           'NET_ACCEPTED',
           'NET_RECEIVED')

NETWORK = 30
NET_DISCONNECTED = 0
NET_CONNECTED = 1
NET_ACCEPTED = 2
NET_RECEIVED = 3


def accepted(connection):
    pass


def connected(connection):
    pass


def disconnected(connection):
    pass


def received(connection, message):
    pass


def init(event_val=None):
    global NETWORK, connected, disconnected, received
    import pygame
    from pygame.event import Event
    from pygame.locals import USEREVENT
    if event_val is not None:
        NETWORK = USEREVENT + event_val

    def _accepted(connection):
        pygame.event.post(Event(NETWORK, {
            'net_type': NET_ACCEPTED,
            #'connection': proxy(connection)
            'connection': connection
        }))
    accepted = _accepted

    def _connected(connection):
        pygame.event.post(Event(NETWORK, {
            'net_type': NET_CONNECTED,
            #'connection': proxy(connection)
            'connection': connection
        }))
    connected = _connected

    def _disconnected(connection):
        pygame.event.post(Event(NETWORK, {
            'net_type': NET_DISCONNECTED,
            #'connection': proxy(connection)
            'connection': connection
        }))
    disconnected = _disconnected

    def _received(connection, message, channel=0):
        pygame.event.post(Event(NETWORK, {
            'net_type': NET_RECEIVED,
            #'connection': proxy(connection),
            'connection': connection,
            'message': message,
            'msg_type': message.__class__
        }))
    received = _received
