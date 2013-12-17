from JumpScale import j

OsisBaseObject=j.core.osis.getOsisBaseObjectClass()

class Machine(OsisBaseObject):

    """
    identifies a machine in the grid
    can be a lxc container or kvm vm or ...
    """

    def __init__(self, ddict={}):
        if ddict <> {}:
            self.load(ddict)
        else:
            self.init("machine","1.0")
            self.id = 0
            self.gid = 0
            self.nid = 0
            self.name = ""
            self.roles = []
            self.netaddr = None
            self.guid = None
            self.ipaddr=[]
            self.active = True
            self.state = ""  #STARTED,STOPPED,RUNNING,FROZEN,CONFIGURED,DELETED
            self.mem=0 #in MB
            self.cpucore=0 #nr of cores cpu
            self.description=""
            self.otherid=""
            self.type = "" #KVM,LXC

