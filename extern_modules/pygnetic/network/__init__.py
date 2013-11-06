# -*- coding: utf-8 -*-
"""Network adapters."""

from .. import _utils
from .. import client
from .. import server

selected_adapter = None


def select_adapter(names):
    """Select first found adapter

    :param names: string or list of strings with names of libraries
    :return: adapter module
    """
    global selected_adapter
    selected_adapter = _utils.find_adapter(__name__, names)
    return selected_adapter


def get_adapter(names):
    """Return adapter

    :param names: string or list of strings with names of libraries
    :return: adapter module
    """
    return _utils.find_adapter(__name__, names)


class Client(object):
    """Proxy class for selected :term:`network adapter`.

    :keyword n_adapter: override default :term:`network adapter` for
        class instance (default: None - module selected with :func:`.init`)
    """
    n_adapter = None

    def __init__(self, *args, **kwargs):
        n_adapter = kwargs.pop('n_adapter', self.n_adapter)
        if n_adapter is not None:
            if not isinstance(n_adapter, client.Client):
                n_adapter = get_adapter(n_adapter)
        elif selected_adapter is not None:
            n_adapter = selected_adapter
        else:
            raise AttributeError("Client adapter is not selected")
        n_adapter = n_adapter.Client(*args, **kwargs)
        object.__setattr__(self, 'n_adapter', n_adapter)

    def __getattr__(self, attr):
        return getattr(self.n_adapter, attr)

    def __setattr__(self, attr, value):
        setattr(self.n_adapter, attr, value)


class Server(object):
    """Proxy class for selected :term:`network adapter`.

    :keyword n_adapter: override default :term:`network adapter` for
        class instance (default: None - module selected with :func:`.init`)
    """
    n_adapter = None

    def __init__(self, *args, **kwargs):
        n_adapter = kwargs.pop('n_adapter', self.n_adapter)
        if n_adapter is not None:
            if not isinstance(n_adapter, server.Server):
                n_adapter = get_adapter(n_adapter)
        elif selected_adapter is not None:
            n_adapter = selected_adapter
        else:
            raise AttributeError("Server adapter is not selected")
        n_adapter = n_adapter.Server(*args, **kwargs)
        object.__setattr__(self, 'n_adapter', n_adapter)

    def __getattr__(self, attr):
        return getattr(self.n_adapter, attr)

    def __setattr__(self, attr, value):
        setattr(self.n_adapter, attr, value)
