# -*- coding: utf-8 -*-

import logging
from importlib import import_module

_logger = logging.getLogger(__name__)


def get_adapter(a_type, name):
    """Return library adapter

    a_type - adapter type
    name - name of library
    """
    a_name = name + '_adapter'
    try:
        return import_module('.'.join((a_type, a_name)))
    except ImportError as e:
        _logger.debug("%s: %s", e.__class__.__name__, e.message)


def find_adapter(a_type, names):
    """Return first found adapter

    a_type - adapter type
    names - string or list of strings with names of libraries
    """
    if isinstance(names, basestring):
        names = (names,)
    for name in names:
        a_name = name + '_adapter'
        try:
            return import_module('.'.join((a_type, a_name)))
        except ImportError as e:
            _logger.debug("%s: %s", e.__class__.__name__, e.message)
