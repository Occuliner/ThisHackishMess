# -*- coding: utf-8 -*-
"""Module containing Handler base class."""

class Handler(object):
    """Base class for objects handling messages through
    :meth:`net_message_name` methods
    """
    def on_connect(self):
        """Called when connection is established."""
        pass

    def on_disconnect(self):
        """Called when connection is closed."""
        pass

    def on_recive(self, message, **kwargs):
        """Called when message is received, but no corresponding
        net_message_name method exist.

        :param kwargs:
            additional keyword arguments from :term:`network adapter`
        """
        pass
