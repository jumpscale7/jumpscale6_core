from JumpScale import j

from _MonObjectBaseFactory import *

class ProcessObjectFactory(MonObjectBaseFactory):
    def __init__(self,host,classs):
        MonObjectBaseFactory.__init__(self,host,classs)
        self.osis=j.core.osis.getClientForCategory(self.host.daemon.osis,"system","process")

    def getProcessStatProps(self,totals=False):
        r=["nr_file_descriptors","nr_ctx_switches_voluntary","nr_ctx_switches_involuntary","nr_threads",\
                "cpu_time_user","cpu_time_system","cpu_percent","mem_vms","mem_rss",\
                "io_read_count","io_write_count","io_read_bytes","io_write_bytes","nr_connections_out","nr_connections_in"]
        if totals:
            r2=[]
            for item in r:
                r2.append(item)
                r2.append("%s_total"%item)
            return r2
        return r


class ProcessObject():

    def __init__(self,pid,psobject=None,lastcheck=0):
        if psobject<>None:
            self.p=psobject
        else:
            self.p=j.system.process.getProcessObject(pid)
        self.children=[]
        self.name=self.p.name
        self.mem_rss,self.mem_vms=self.p.get_memory_info()
        connections= self.p.get_connections()
        self.nr_connections=0
        self.ports=[]
        self.netConnectionsIn=[]
        self.netConnectionsOut=[]
        if len(connections)>0:
            self.nr_connections=len(connections)
            for c in connections:
                if c.status=="LISTEN":
                    #is server
                    port=c.local_address[1]
                    if port not in self.ports:
                        self.ports.append(port)
                    if c.remote_address<>() and c.remote_address not in self.netConnectionsIn:
                        self.netConnectionsIn.append(c.remote_address)
                if c.status=="ESTABLISHED":
                    if c.remote_address not in self.netConnectionsOut:
                        self.netConnectionsOut.append(c.remote_address)

        self.nr_connections_in=len(self.netConnectionsIn)
        self.nr_connections_out=len(self.netConnectionsOut)

        self.io_read_count, self.io_write_count, self.io_read_bytes, self.io_write_bytes=self.p.get_io_counters()
        self.cmd=self.p.getcwd()
        self.parent=self.p.parent.pid
        self.nr_file_descriptors=self.p.get_num_fds()
        self.nr_ctx_switches_voluntary,self.nr_ctx_switches_involuntary=self.p.get_num_ctx_switches()
        self.nr_threads=self.p.get_num_threads()
        # self.nr_openfiles=self.p.get_open_files()
        self.cpu_time_user,self.cpu_time_system=self.p.get_cpu_times()
        self.cpu_percent=self.p.get_cpu_percent(0)
        self.user=self.p.username
        self._totals=None
        if lastcheck<>0:
            self.lastcheck=lastcheck
        else:
            self.lastcheck=time.time()
        self.guid=None #guid from osis

        for child in self.p.get_children():
            if hasattr(child, 'pid'):
                childpid = child.pid
            else:
                childpid = child.getPid()
            child=j.processmanager.cache.processobject.get(childpid,child,lastcheck)
            if not j.processmanager.childrenPidsFound.has_key(childpid):                
                self.children.append(child)
                j.processmanager.childrenPidsFound[int(childpid)]=True
            
    def getGuid(Self):
        return self.pid

    def getStatInfo(self,totals=False):
        """
        @format dict or txt
        """
        result={}
        if totals:
            self.getTotalsChildren()

        for name in j.processmanager.cache.processobject.getProcessStatProps(totals):
            result[name]=self.__dict__[name]

        return result


    def getTotalsChildren(self):
        """
        calculate total for children
        """
        if self._totals==None:

            for item in j.processmanager.cache.processobject.getProcessStatProps():
                newname="%s_total"%item
                self.__dict__[newname]=self.__dict__[item]
                for child in self.children:
                    self.__dict__[newname]+=float(child.__dict__[item])            
                        
        self._totals=True

    def __repr__(self):
        out=""
        for key,val in self.__dict__.iteritems():
            if key not in ["p","children"]:
                out+="%s:%s\n"%(key,val)
        items=out.split("\n")
        items.sort()
        return "\n".join(items)


    __str__ = __repr__

