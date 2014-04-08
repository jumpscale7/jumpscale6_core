from JumpScale import j
import copy
OsisBaseObject=j.core.osis.getOsisBaseObjectClass()

class BSNamespace(OsisBaseObject):

    """
    identifies a disk in blobstor
    """

    def __init__(self, ddict={}):
        if ddict <> {}:
            self.load(ddict)
        else:
            self.id = 0
            self.maxsize = 0    #in GB (if 0 no limit)
            self.used = 0       #in GB
            self.domain=""
            self.name = ""
            self.encrtype = ""
            self.encrkey=""
            self.comprtype = ""
            self.comprAtClient=False
            self.encrAtClient=False
            self.spaceGuid=""
            self.gid = 0
            self.guid = None
            self.active = True
            self.replicaNr=3            #3 means 3 copies are kept, so can loose 2 before data loss
            self.replicaMaxSizeKB=256   #256 means files bigger than 256KB will be spreaded out, otherwise replicated
            self.spreadpolicy="6/2"     #6/2 means 2 from 6 can be lost, so as long as 4 available we can reconstruct the data
            self.nodeSafe=None          #if True then we calculated that we can loose nodes in stead of disks e.g. for 6/2 need at least 6 nodes
            self.routeMap=[]            #list of nodeids which take the data 
            self.routeMapHistory=""     #holds the history of the routemaps if there were changes  (as json)
            self.lastupdate=0           #epoch of last time the info was updated from reality
        self.getSetGuid()

    def getUniqueKey(self):
        """
        return unique key for object, is used to define unique id
        """
        C="%s_%s_%s"%(self.gid,self.domain,self.name)
        return j.tools.hash.md5_string(C)

    def getContentKey(self):
        ddict=copy.copy(self.__dict__)
        ddict.pop("lastupdate")
        ddict.pop("guid")
        return j.tools.hash.md5_string(str(ddict))

    def getSetGuid(self):
        """
        use osis to define & set unique guid (sometimes also id)
        """
        self.gid = int(self.gid)
        self.guid = "%s_%s" % (self.gid, self.id)
        self.lastupdate=j.base.time.getTimeEpoch()
        return self.guid

