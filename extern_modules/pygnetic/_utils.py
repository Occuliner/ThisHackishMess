# -*- coding: utf-8 -*-

import logging
from importlib import import_module

_logger = logging.getLogger(__name__)


def find_adapter(a_type, names):
    """Return first found adapter

    :param a_type: - adapter type
    :param names: - string or list of strings with names of libraries
    :return: adapter module
    """
    if isinstance(names, basestring):
        names = (names,)
    for name in names:
        a_name = name + '_adapter'
        try:
            return import_module('.'.join((a_type, a_name)))
        except ImportError as e:
            _logger.debug("%s: %s", e.__class__.__name__, e.message)


class lazyproperty(object):
    """Decorator for properties calculated only once"""
    def __init__(self, calculate_function):
        self._calculate = calculate_function

    def __get__(self, obj, _=None):
        if obj is None:
            return self
        value = self._calculate(obj)
        setattr(obj, self._calculate.func_name, value)
        return value