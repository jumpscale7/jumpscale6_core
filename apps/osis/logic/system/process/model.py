from JumpScale import j

OsisBaseObject=j.core.osis.getOsisBaseObjectClass()

class Process(OsisBaseObject):

    """
    unique process
    """

    def __init__(self, ddict={}, gid=0,aid=0,nid=0,name="",instance="",systempid=0, id=''):
        if ddict <> {}:
            self.load(ddict)
            self.getSetGuid()
        else:
            self.init("process","1.0")
            self.gid = gid
            self.nid = nid
            self.jpdomain= ""
            self.jpname= ""
            self.name = name
            self.ports = []
            self.instance = instance
            self.systempid = systempid  # system process id (PID) at this point
            self.guid = None
            # self.sguid = None
            self.epochstart = j.base.time.getTimeEpoch()
            self.epochstop = 0
            self.active = True
            self.lastcheck=0 #epoch of last time the info was checked from reality
            self.cmd=""
            self.workingdir=''

            r=["nr_file_descriptors","nr_ctx_switches_voluntary","nr_ctx_switches_involuntary","nr_threads",\
                "cpu_time_user","cpu_time_system","cpu_percent","mem_vms","mem_rss",\
                "io_read_count","io_write_count","io_read_bytes","io_write_bytes","nr_connections_in","nr_connections_out"]
            for item in r:
                self.__dict__[item]=0.0
                self.__dict__["%s_total"%item]=0.0
            self.getSetGuid()

    def getUniqueKey(self):
        """
        return unique key for object, is used to define unique id
        """

        C="%s_%s_%s_%s_%s_%s_%s"%(self.systempid,self.gid,self.nid,\
            self.jpdomain,self.jpname,self.instance,self.name)
        return j.tools.hash.md5_string(C)

    def getSetGuid(self):
        """
        use osis to define & set unique guid (sometimes also id)
        """
        self.gid = int(self.gid)
        self.nid = int(self.nid)
        self.guid = "%s_%s_%s" % (self.gid,self.nid,self.systempid)
        self.id = self.guid
        self.lastcheck=j.base.time.getTimeEpoch() 
        return self.guid

