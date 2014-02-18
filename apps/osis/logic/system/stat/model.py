from JumpScale import j
import time

OsisBaseObject=j.core.osis.getOsisBaseObjectClass()

class Stat(OsisBaseObject):

    """
    identifies a stat key in the grid
    """

    def __init__(self, ddict={}, key=None, value=None):
        if ddict <> {}:
            self.load(ddict)
        else:
            # self.initmeta("stat","1.0")
            self.key = key
            self.value = value
            self.nid = 0 #on which node can we find this stat
            self.lastcheck= time.time() #epoch of last time the info was checked from reality


    def getSetGuid(self):
        """
        use osis to define & set unique guid (sometimes also id)
        """
        self.guid = self.key
        self.lastcheck=j.base.time.getTimeEpoch()

        return self.guid
