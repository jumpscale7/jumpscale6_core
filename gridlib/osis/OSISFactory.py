from OpenWizzy import o
from OSIS import OSIS
from OSISClient import OSISClient
from OSISCMDS import OSISCMDS
from OSISClientForCat import OSISClientForCat
import random
import imp
import sys

class OSISFactory:
    """
    """
    def __init__(self):
        self.osisConnections={}

    def getLocal(self,path="",overwriteHRD=False,overwriteImplementation=False,namespacename=None):
        """
        create local instance starting from path
        """
        osis=OSIS()
        osis.init(path,overwriteHRD,overwriteImplementation,namespacename)
        return osis

    def startDaemon(self,path="",overwriteHRD=False,overwriteImplementation=False,namespacename=None,port=5544):
        """
        start deamon
        """
        osis=self.getLocal(path,overwriteHRD,overwriteImplementation,namespacename)
        zd=o.core.zdaemon.getZDaemon(port=port)
        zd.setCMDsInterface(OSISCMDS)  #pass as class not as object !!!
        zd.daemon.cmdsInterfaces[""][-1].osis=osis  #is the first instance of the cmd interface
       
        zd.start()

    def getClient(self,ipaddr="localhost",port=5544):
        key="%s_%s"%(ipaddr,port)
        if self.osisConnections.has_key(key):
            return self.osisConnections[key]
        self.osisConnections[key]= OSISClient(ipaddr,port)
        return self.osisConnections[key]

    def getClientForCategory(self,namespace,category,ipaddr="localhost",port=5544):
        client=self.getClient(ipaddr,port)
        namespaceid,catid=client._getIds(namespace,category)
        return OSISClientForCat(client,namespaceid,catid)

    def getOsisImplementationParentClass(self,namespacename):
        """
        return parent class for osis implementation (is the implementation from which each namespace & category inherits)
        
        """
        implpath=o.system.fs.joinPaths("logic",namespacename,"OSIS_parent.py")
        classs=self._loadModuleClass(implpath)
        return classs

    def _loadModuleClass(self,path):
        '''Load the Python module from disk using a random name'''
        #Random name -> name in sys.modules
        def generate_module_name():
            '''Generate a random unused module name'''
            return '_osis_module_%d' % random.randint(0, sys.maxint)
        modname = generate_module_name()
        while modname in sys.modules:
            modname = generate_module_name()
      

        module = imp.load_source(modname, path)
        # #find main classname of module
        # classes=[item for item in module.__dict__.keys() if (item<>"q" and item[0]<>"_")]
        # if len(classes)<>1:
        #     o.errorconditionhandler.raiseBug(message="there must be only 1 class implemented in %s"%path,category="osis.init")
        # classname=classes[0]        
        # return module.__dict__[classname] 
        return module.mainclass


        

