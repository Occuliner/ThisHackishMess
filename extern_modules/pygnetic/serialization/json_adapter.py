# -*- coding: utf-8 -*-
"""Module containing serialization adapter for json."""

import json


class JSONDecoder(json.JSONDecoder):
    """JSONDecoder with streaming feature"""
    def __init__(self):
        super(JSONDecoder, self).__init__()
        self.buffer = bytearray()

    def feed(self, data):
        self.buffer.extend(data)

    def decode(self):
        try:
            obj, end = self.scan_once(self.buffer.decode(), 0)
            del self.buffer[:end]
            return obj
        except:
            raise StopIteration('No more data to decode.')

    next = decode


def unpack(*args):
    try:
        return json.loads(*args)
    except ValueError:
        pass


pack = json.dumps
unpacker = JSONDecoder
