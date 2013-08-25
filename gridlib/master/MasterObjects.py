from JumpScale import j
import struct
import os
import time


class GridAgent:

    def __init__(self, path="", key="", name="", nsid=0, epoch=0, stat="", bindata=None, changelog=[]):
        if bindata <> None:
            self.unserialize(bindata, changelog)
        else:
            self.path = path
            self.key = key
            self.nsid = nsid
            self.name = name

    def markchanged(self):
        """
        """
        if not self.changed:
            self.changed = True

    def __repr__(self):
        return str(self.__dict__)

    __str__ = __repr__


class MasterObjectsFactory():

    def getAgent(self, bindata=None):
        return MBObjectsDB(nsid)
