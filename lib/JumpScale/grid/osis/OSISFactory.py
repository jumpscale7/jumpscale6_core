from JumpScale import j
from OSISCMDS import OSISCMDS
from OSISClientForCat import OSISClientForCat
from OSISBaseObject import OSISBaseObject
import random
import imp
import sys


class OSISFactory:

    """
    """

    def __init__(self):
        self.osisConnections = {}
        self.osisConnectionsCat={}

    def getLocal(self, path="", overwriteHRD=False, overwriteImplementation=False, namespacename=None):
        """
        create local instance starting from path
        """
        osis=OSISCMDS()
        osis.init()
        return osis

    def startDaemon(self, path="", overwriteHRD=False, overwriteImplementation=False, namespacename=None, port=5544):
        """
        start deamon
        """
        zd = j.core.zdaemon.getZDaemon(port=port,name="osis")
        zd.setCMDsInterface(OSISCMDS, category="osis")  # pass as class not as object !!!
        zd.daemon.cmdsInterfaces["osis"][-1].init()
        zd.start()

    def getClient(self, ipaddr="localhost", port=5544,user="root",passwd="rooter",ssl=False):
        key = "%s_%s" % (ipaddr, port)
        if self.osisConnections.has_key(key):
            return self.osisConnections[key]
        # self.osisConnections[key] = OSISClient(ipaddr, port)
        j.logger.log("get client to osis")
        self.osisConnections[key] = j.core.zdaemon.getZDaemonClient(addr=ipaddr, port=port, category="osis",\
            user=user, passwd=passwd,ssl=ssl,sendformat="j", returnformat="j")
        return self.osisConnections[key]

    def getClientForCategory(self, client,namespace, category):
        """
        how to use

        client=j.core.osis.getClient("localhost",port=5544,user="root",passwd="rooter",ssl=False)
        client4node=j.core.osis.getClientForCategory(client,"system","node")
        """        
        key = "%s_%s_%s_%s" % (client._client.transport._addr, client._client.transport._port,namespace,category)
        if self.osisConnectionsCat.has_key(key):
            return self.osisConnectionsCat[key]
        self.osisConnectionsCat[key]= OSISClientForCat(client, namespace, category)
        return self.osisConnectionsCat[key]

    def getOsisBaseObjectClass(self):
        return OSISBaseObject

    def getOsisImplementationParentClass(self, namespacename):
        """
        return parent class for osis implementation (is the implementation from which each namespace & category inherits)

        """
        implpath = j.system.fs.joinPaths("logic", namespacename, "OSIS_parent.py")
        classs = self._loadModuleClass(implpath)
        return classs

    def _loadModuleClass(self, path):
        '''Load the Python module from disk using a random name'''
        # Random name -> name in sys.modules
        def generate_module_name():
            '''Generate a random unused module name'''
            return '_osis_module_%d' % random.randint(0, sys.maxint)
        modname = generate_module_name()
        while modname in sys.modules:
            modname = generate_module_name()

        print path

        module = imp.load_source(modname, path)
        # find main classname of module
        # classes=[item for item in module.__dict__.keys() if (item<>"q" and item[0]<>"_")]
        # if len(classes)<>1:
        #     j.errorconditionhandler.raiseBug(message="there must be only 1 class implemented in %s"%path,category="osis.init")
        # classname=classes[0]
        # return module.__dict__[classname]
        return module.mainclass
