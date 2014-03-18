from JumpScale import j
from OSISCMDS import OSISCMDS
from OSISClientForCat import OSISClientForCat
from OSISBaseObject import OSISBaseObject
from OSISBaseObjectComplexType import OSISBaseObjectComplexType

import inspect
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

class ClassEmpty():
    pass

class OSISFactory:

    """
    """

    def _redirect(self):
        self._out=FileLikeStreamObject()
        if not self._sysstdout:
            self._sysstdout=sys.stdout
        # sys.stdout=self._out

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
        if j.application.config.exists("grid.master.superadminpasswd"):
            self.superadminpasswd=j.application.config.get("grid.master.superadminpasswd")
        else:
            self.superadminpasswd=None
        self.key=j.application.config.get("osis.key")
        self.osisModels={}
        self.namespacesInited={}
        

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

        if not j.system.net.tcpPortConnectionTest("127.0.0.1",9200):
            j.packages.findNewest(name="elasticsearch").install()
            j.packages.findNewest(name="elasticsearch").start()
        if not j.system.net.tcpPortConnectionTest("127.0.0.1",8081) or not j.system.net.tcpPortConnectionTest("127.0.0.1",2003):
            j.packages.findNewest(name="graphite").install()
            j.packages.findNewest(name="graphite").start()

        if not j.system.net.tcpPortConnectionTest("127.0.0.1",8081) or not j.system.net.tcpPortConnectionTest("127.0.0.1",2003) or not j.system.net.tcpPortConnectionTest("127.0.0.1",9200):
            raise RuntimeError("cannot start osis, could not find running elastic search and/or carbon/graphite")

        zd = j.core.zdaemon.getZDaemon(port=port,name="osis")
        zd.addCMDsInterface(OSISCMDS, category="osis")  # pass as class not as object !!!
        zd.daemon.cmdsInterfaces["osis"].init()
        self.cmds=zd.daemon.cmdsInterfaces["osis"]
        zd.start()

    def getClient(self, ipaddr="localhost", port=5544,user=None,passwd=None,ssl=False,gevent=False):
        with j.logger.nostdout() as stdout:
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
                    if j.application.config.exists("grid.master.superadminpasswd"):
                        passwd=j.application.config.get("grid.master.superadminpasswd")
                    else:
                        raise RuntimeError("Superadmin passwd has not been defined on this node, please put in hrd (grid.master.superadminpasswd) or use argument 'passwd'.")
                self.osisConnections[key] = j.core.zdaemon.getZDaemonClient(addr=ipaddr, port=port, category="osis",\
                    user=user, passwd=passwd,ssl=ssl,sendformat="j", returnformat="j",gevent=gevent)
            except Exception,e:
                print stdout.getvalue()
                raise RuntimeError("Could not connect to osis: %s %s.\nOut:%s\nError:%s\n"%(key,user,stdout.getvalue(),e))
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

    def getOSISBaseObjectComplexType(self):
        return OSISBaseObjectComplexType

    def getOsisImplementationParentClass(self, namespacename):
        """
        return parent class for osis implementation (is the implementation from which each namespace & category inherits)
        """
        implpath = j.system.fs.joinPaths("logic", namespacename, "OSIS_parent.py")
        classs = self._loadModuleClass(implpath)
        return classs

    def _generateOsisModelClassFromSpec(self,namespace,specpath,modelName="",classpath=""):
        """
        generate class files for spec (can be more than 1)
        generated in classpath/modelName/OsisGeneratedRootObject.py
        and also classpath/modelName/model.py
        @return classpath
        """
        import JumpScale.baselib.specparser                
        j.core.specparser.parseSpecs(specpath, appname="osismodel", actorname=namespace)
        # spec = j.core.specparser.getModelSpec(namespace, category, "root")

        modelNames = j.core.specparser.getModelNames("osismodel", namespace)

        if classpath=="":
            classpath=j.system.fs.joinPaths(j.dirs.varDir,"code","osismodel",namespace)

        extpath=j.system.fs.getDirName(inspect.getfile(self.getClient))
        templpath=j.system.fs.joinPaths(extpath,"_templates","osiscomplextypes")
        j.system.fs.copyDirTree(templpath, classpath, keepsymlinks=False, eraseDestination=False, \
            skipProtectedDirs=False, overwriteFiles=False, applyHrdOnDestPaths=None)        
                
        if len(modelNames) > 0:

            for modelName in modelNames:
                modelspec = j.core.specparser.getModelSpec("osismodel", namespace, modelName)
                modeltags = j.core.tags.getObject(modelspec.tags)

                # # will generate the tasklets
                # modelHasTasklets = modeltags.labelExists("tasklets")
                # if modelHasTasklets:
                #     j.core.codegenerator.generate(modelspec, "osis", codepath=actorpath, returnClass=False, args=args)

                # if spec.hasTasklets:
                #     self.loadOsisTasklets(actorobject, actorpath, modelName=modelspec.name)

                code = j.core.codegenerator.getCodeJSModel("osismodel", namespace, modelName)
                if modelspec.tags == None:
                    modelspec.tags = ""
                index = j.core.tags.getObject(modelspec.tags).labelExists("index")
                tags = j.core.tags.getObject(modelspec.tags)

                classnameGenerated="JSModel_%s_%s_%s"%("osismodel", namespace, modelName)
                classnameNew="%s_%s"%(namespace,modelName)
                classnameNew2="%s_%s_osismodelbase"%(namespace,modelName)
                code=code.replace(classnameGenerated,classnameNew2)

                classpathForModel=j.system.fs.joinPaths(classpath,modelName)
                j.system.fs.createDir(classpathForModel)
                classpath3=j.system.fs.joinPaths(classpathForModel,"%s_osismodelbase.py"%classnameNew)
                j.system.fs.writeFile(filename=classpath3,contents=code)

                mpath=j.system.fs.joinPaths(classpathForModel,"model.py")
                if not j.system.fs.exists(path=mpath):
                    j.system.fs.copyFile(j.system.fs.joinPaths(classpath,"model_template.py"),mpath)
                    content=j.system.fs.fileGetContents(mpath)
                    content=content.replace("$modelbase","%s"%classnameNew)
                    j.system.fs.writeFile(filename=mpath,contents=content)

        return classpath

    def generateOsisModelDefaults(self,namespace,specpath=""):
        import JumpScale.portal.codegentools

        if specpath=="":
            specpath=j.system.fs.joinPaths("logic", namespace, "model.spec")

        basepathspec=j.system.fs.getDirName(specpath)


        if j.system.fs.exists(path=specpath):
            print "SPECPATH:%s" %specpath
            self._generateOsisModelClassFromSpec(namespace,specpath=basepathspec,classpath=basepathspec)

    def getModelTemplate(self):
        extpath=j.system.fs.getDirName(inspect.getfile(self.getClient))
        return j.system.fs.joinPaths(extpath,"_templates","model_template.py")


    def getOsisModelClass(self,namespace,category,specpath=""):
        """
        returns class generated from spec file or from model.py file
        """
        key="%s_%s"%(namespace,category)

        if not self.osisModels.has_key(key):
            print "getOsisModelClass: %s_%s"%(namespace, category)
            # #need to check if there is a specfile or we go from model.py  
            if specpath=="":
                specpath=j.system.fs.joinPaths("logic", namespace, "model.spec")            

            basepathspec=j.system.fs.getDirName(specpath)            
            basepath=j.system.fs.joinPaths(basepathspec,category)            
            modelpath=j.system.fs.joinPaths(basepath,"model.py")

            if j.system.fs.exists(path=modelpath):                
                klass= j.system.fs.fileGetContents(modelpath)
                name=""
                for line in klass.split("\n"):
                    if line.find("(OsisBaseObject")<>-1 and line.find("class ")<>-1:
                        name=line.split("(")[0].lstrip("class").strip()
                if name=="":
                    raise RuntimeError("could not find: class $modelName(OsisBaseObject) in model class file, should always be there")

                sys.path.append(basepath)
                module = imp.load_source(key,modelpath)
                self.osisModels[key]=module.__dict__[name]
            else:
                raise RuntimeError("Could not find model.py in %s"%basepath)

        return self.osisModels[key]

    def _loadModuleClass(self, path):
        '''Load the Python module from disk using a random name'''
        modname = "osis_%s"%path.replace("/","_").replace("logic_","")[:-3]
        
        # while modname in sys.modules:
        #     modname = generate_module_name()

        print path

        module = imp.load_source(modname, path)
        # find main classname of module
        # classes=[item for item in module.__dict__.keys() if (item<>"q" and item[0]<>"_")]
        # if len(classes)<>1:
        #     j.errorconditionhandler.raiseBug(message="there must be only 1 class implemented in %s"%path,category="osis.init")
        # classname=classes[0]
        # return module.__dict__[classname]
        try:
            return module.mainclass
        except Exception,e:
            raise RuntimeError("Could not load module on %s, could not find 'mainclass', check code on path. Error:%s"% (path,e))
            
