# -*- coding: utf-8 -*-
"""Module containing serialization adapter for msgpack."""

import msgpack

pack = msgpack.packb
unpack = msgpack.unpackb
unpacker = msgpack.Unpacker
