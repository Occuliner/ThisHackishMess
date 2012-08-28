# -*- coding: utf-8 -*-
"""Serialization adapters."""

from .. import _utils

selected_adapter = None
pack = unpack = unpacker = None


def select_adapter(names):
    global selected_adapter, pack, unpack, unpacker
    selected_adapter = _utils.find_adapter(__name__, names)
    if selected_adapter is not None:
        pack = selected_adapter.pack
        unpack = selected_adapter.unpack
        unpacker = selected_adapter.unpacker


def get_adapter(name):
    return _utils.find_adapter(__name__, name)
