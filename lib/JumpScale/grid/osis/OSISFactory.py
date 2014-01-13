from JumpScale import j
from OSISCMDS import OSISCMDS
from OSISClientForCat import OSISClientForCat
from OSISBaseObject import OSISBaseObject
import random
import imp
import sys
import ujson

class FileLikeStreamObject(object):
    def __init__(self):
        self.out=""

    def write(self, buf,**args):
        for line in buf.rstrip().splitlines():
            #print "###%s"%line
            self.out+="%s\n"%line

class OSISFactory:

    """
    """


    def _redirect(self):
        self._out=FileLikeStreamObject()
        if not self._sysstdout:
            self._sysstdout=sys.stdout
        sys.stdout=self._out

    def _stopRedirect(self,pprint=False):
        if self._sysstdout:
            sys.stdout=self._sysstdout
        out = None
        if self._out:
            out=self._out.out
            if pprint:
                print out
        self._out=None 
        return out

    def __init__(self):
        self._sysstdout = None
        self.osisConnections = {}
        self.osisConnectionsCat={}
        self.nodeguids={}
        if j.application.config.exists("gridmaster.superadminpasswd"):
            self.superadminpasswd=j.application.config.get("gridmaster.superadminpasswd")
        else:
            self.superadminpasswd=None
        self.key=j.application.config.get("osis.key")
        

    def encrypt(self,obj):
        if not j.basetype.string.check(obj):
            if j.basetype.dictionary.check(obj):
                val=obj
            else:
                val=obj.__dict__
            val=ujson.dumps(val)
        val=j.db.serializers.blowfish.dumps(val,self.key)
        return val

    def decrypt(self,text):
        if not j.basetype.string.check(text):
            raise RuntimeError("needs to be string")
        text=j.db.serializers.blowfish.loads(text,self.key)
        return text

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
        self.cmds=zd.daemon.cmdsInterfaces["osis"][-1]
        zd.start()

    def getClient(self, ipaddr="localhost", port=5544,user=None,passwd=None,ssl=False):
        self._redirect()
        try:
            key = "%s_%s_%s_%s" % (ipaddr, port,user,passwd)
            if self.osisConnections.has_key(key):
                return self.osisConnections[key]
            # self.osisConnections[key] = OSISClient(ipaddr, port)
            j.logger.log("get client to osis")

            if user==None:
                user="node"
                passwd=j.application.config.get("grid.node.machineguid")
            elif user=="root" and not passwd:
                if j.application.config.exists("gridmaster.superadminpasswd"):
                    passwd=j.application.config.get("gridmaster.superadminpasswd")
                else:
                    raise RuntimeError("Superadmin passwd has not been defined on this node, please put in hrd (gridmaster.superadminpasswd) or use argument 'passwd'.")
            self.osisConnections[key] = j.core.zdaemon.getZDaemonClient(addr=ipaddr, port=port, category="osis",\
                user=user, passwd=passwd,ssl=ssl,sendformat="j", returnformat="j")
        except Exception,e:
            out=self._stopRedirect(pprint=True)            
            raise RuntimeError("Could not connect to osis: %s %s.\nOut:%s\nError:%s\n"%(key,user,out,e))
        finally:
            self._stopRedirect()
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
