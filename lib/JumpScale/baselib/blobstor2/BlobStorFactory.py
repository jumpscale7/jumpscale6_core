from JumpScale import j

from BlobStorClient import *
from BlobStorServer import *

class BlobStorFactory:
    def __init__(self):
        self.logenable=True
        self.loglevel=5
        self.blobstorCache={}

    def getClient(self, namespace, name="default"):
        from IPython import embed
        print "DEBUG NOW BlobStorFactory"
        embed()
        
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

