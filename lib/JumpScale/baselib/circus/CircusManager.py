from JumpScale import j


class CircusManager:
    def __init__(self):
        self.configpath="/opt/jumpscale/cfg/startup"

    def addProcess(self,name,cmd,args="",warmup_delay=0,numprocesses=1):
        
        T="[watcher:%s]\n"%name
        T+="cmd = %s\n"%cmd
        # e.g. cmd :/usr/share/elasticsearch/bin/elasticsearch -fD es.config=/etc/elasticsearch/elasticsearch.yml
        T+="args = %s\n"%args
        T+="warmup_delay = %s\n"%warmup_delay
        T+="numprocesses = %s\n"%numprocesses

        j.system.fs.writeFile(self._getPath(name),T)

    def _getPath(self,name):
        path="%s/%s.ini"%(self.configpath,name)
        return path

    def removeProcess(self,name):
        j.system.fs.remove(self._getPath(name))
        j.tools.circus.client.rm(name=name)

    def apply(self):
        """
        make sure circus knows about it
        """
        j.tools.circus.client.reload()
        j.tools.circus.client.reloadconfig()
        stats=j.tools.circus.client.status()
        if stats["statuses"]["circushttpd"]=="stopped":
            j.tools.circus.client.start()

    def listProcesses(self):
        items=j.system.fs.listFilesInDir(self.configpath, recursive=False, filter="*.ini")
        items=[j.system.fs.getBaseName(item).rstrip(".ini") for item in items]
        return items

