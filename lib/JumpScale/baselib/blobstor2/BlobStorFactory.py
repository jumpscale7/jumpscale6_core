from JumpScale import j

from BlobStorClient import *
from BlobStorServer import *

class BlobStorFactory:
    def __init__(self):
        self.logenable=True
        self.loglevel=5
        self.blobstorCache={}

    def getClient(self, namespace, name="default"):
        id=0
        for key in j.application.config.getKeysFromPrefix("blobclient.blobserver"):
            # key=key.replace("gitlabclient.server.","")
            if key.find("name")<>-1:
                if j.application.config.get(key)==name:
                    key2=key.replace("blobclient.blobserver.","")
                    id=key2.split(".")[0]
        if id==0:
            raise RuntimeError("Did not find account:%s for blobserverclient")
        prefix="blobclient.blobserver.%s"%id
        ipaddr=j.application.config.get("%s.addr"%prefix)
        port=j.application.config.get("%s.port"%prefix)
        login=j.application.config.get("%s.login"%prefix)
        passwd=j.application.config.get("%s.passwd"%prefix)
        
        name="%s_%s"%(ipaddr,port)
        if self.blobstorCache.has_key(name):
            return self.blobstorCache[name]
        self.blobstorCache[name]= BlobStorClient2(namespace, ipaddr, port, login, passwd)
        return self.blobstorCache[name]

    def log(self,msg,category="",level=5):
        if level<self.loglevel+1 and self.logenable:
            j.logger.log(msg,category="blobstor.%s"%category,level=level)

class BlobStorFactoryServer:

    def start(self,port=2345):
        BlobStorServer2(port=port)

