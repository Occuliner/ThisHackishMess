# -*- coding: utf-8 -*-
"""Module containing base classes for synchronized objects."""

from weakref import WeakKeyDictionary
from message import *


class Mode(object):
    AUTO = 0
    MANUAL = 1


class SyncObject(object):
    """Base class for synchronized objects

    The base class for local objects to be automatically
    synchronized with remote host. Derived class should replace sync_var
    to specify a tuple of variable names for synchronization.
    Each assignment to a variable defined in sync_var will notify
    SyncObjectManager which, depending on sync_mode, will either
    prepare update message (Mode.AUTO) or
    wait with preparation for send_changes call (Mode.MANUAL).
    sync_flags overrides default enet sending flags.
    """
    sync_var = ()
    sync_mode = Mode.AUTO
    sync_flags = None

    def __init__(self, *args, **kwargs):
        super(SyncObject, self).__init__(*args, **kwargs)
        SyncObjectManager.register(self)

    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)
        if name in self.sync_var:
            SyncObjectManager.changed(self, name)

    def on_change(self, var_names):
        """Callback when variable(s) was changed by remote host
        """
        pass

    def on_reply(self, message_id):
        """Callback when there was reply to change from remote host
        """
        pass

    def send_changes(self):
        """Prepare update message to send

        When sync_mode is SYNCOBJECT_MODE_MANUAL,
        notify SyncObjectManager to prepare update message
        """
        pass

    def notify_change(self, var_name):
        """Notify SyncObjectManager that variable was changed
        """
        SyncObjectManager.changed(self, var_name)


class SyncObjectManager(object):
    """Manager of SyncObject instances, shouldn't be used by user

    note:
        Class used by SyncObject automatically, no need to use it.
    """
    _known_types = {}
    _sync_objs = WeakKeyDictionary()
    _type_id_cnt = 0
    _obj_id_cnt = 0

    @classmethod
    def register(cls, obj):
        """Registers new object deriving from SyncObject
        """
        try:
            type_id = cls._known_types[obj.__class__]
        except KeyError:
            type_id = cls._type_id_cnt + 1
            cls._known_types[obj.__class__] = type_id
            cls._type_id_cnt = type_id
        obj_id = cls._obj_id_cnt + 1
        cls._sync_objs[obj] = (type_id, obj_id, set())
        cls._obj_id_cnt = obj_id

    @classmethod
    def changed(cls, obj, var_name):
        """Prepares update message
        """
        cls._sync_objs[obj][2].add(var_name)
        # TODO: finish this
        # TODO: push update message to queue if in auto mode

# TODO: pushing update messages from SyncObject
# TODO: mapping obj type and variables to ints


class RemoteObject(object):
    """Class representing remote SyncObject locally
    """
    pass

# TODO: add methods faking SyncObject attributes
