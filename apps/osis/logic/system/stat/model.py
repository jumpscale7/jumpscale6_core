from JumpScale import j

OsisBaseObject=j.core.osis.getOsisBaseObjectClass()

class Stat(OsisBaseObject):

    """
    identifies a stat key in the grid
    """

    def __init__(self, ddict={}):
        if ddict <> {}:
            self.load(ddict)
        else:
            self.init("stat","1.0")
            self.key = 0
            self.nid = 0 #on which node can we find this stat

