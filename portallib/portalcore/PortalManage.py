from OpenWizzy import o
import OpenWizzy.baselib.inifile
import os
from PortalProcess import PortalProcess

class Group():
    pass

class PortalManage():
    """
    management class for appserver
    """

    def startprocess(self,processNr=1,reset=False):
        """
        """
        o.apps=Group()
        o.db.keyvaluestore
        self._initPortal()
        o.core.portal.runningPortal.start(reset=reset)


    def _initPortal(self,processNr=1):

        ini=o.tools.inifile.open(os.path.abspath("cfg/appserver.cfg"))
        appdir=ini.getValue("main", "appdir")

        cfgdir=o.system.fs.joinPaths(o.system.fs.getcwd(),"cfg")
        curdir=o.system.fs.getcwd()

        o.system.fs.changeDir(appdir)

        #self.masterIP=self.gridInifile.getValue("master", "ip")
        #self.masterSecret=self.gridInifile.getValue("master", "secret")
        #self.masterPort=self.gridInifile.getValue("master", "port")

        try:
            ips = o.system.net.getIpAddresses()
        except:
            print "WARNING, COULD NOT FIND LOCAL IP ADDRESSES, use value from appserver config file"  #@todo implement on windows
            ips = list()

        ips = [item for item in ips if item != "127.0.0.1"]
        if len(ips) == 1:
            ini.setParam('main',"ipaddr",ips[0])
            ip=ips[0]
        elif len(ips) == 0:
            ip=ini.getValue("main","ipaddr")
        else:
            ip = ",".join(ips)
            ini.setParam('main',"ipaddr",ip)

        PortalProcess(processNr=processNr,cfgdir=cfgdir,startdir=curdir)



        ##happens in appserverprocess  in the addactorfromspecs
        #for app,actor2,instance in toload:
            #o.core.portal.runningPortal.addActorFromSpecs(app,actor2,instance)
            #key3="%s_%s" % (app,actor2)  #load the models
            #if o.core.specparser.modelnames.has_key(key3):
                #for modelname in o.core.specparser.modelnames[key3]:
                    #actor3="%s_model_%s" % (actor2,modelname)
                    #o.core.portal.runningPortal.addActorFromSpecs(app,actor3,instance)



    #def start(self,secret,nrworkers=1,nrservers=0,extraScreens=[],console=False,qshell=False,isMessageServer=False,dbtype="fs"):
        #"""
        #return an Portal  local env, this will start
        #- appserver master process (wich is also the local messagehandler)
        #- X qworker processes
        #- Y appserver processes

        #@param nrworkers is the amount of workers we want to startup
        #@param nrservers is the amount of appservers we want to startup
        #@param dbtype is "fs" or "arakoon"
        #"""
        #if dbtype == "fs":
            #dbtype = "file_system"

        #if nrworkers==0:
            #raise RuntimeError("Cannot start min nr of workers not defined, needs to be minimal 1")



        #extpath=o.core.portal.pm_extensionpath

        #if o.system.platformtype.isWindows:

            #from OpenWizzy.core.Shell import ipshell
            #print "DEBUG NOW windows appserver manage start"
            #ipshell()
        #else:

            #screens=[]
            #for nr in range(nrworkers):
                #screens.append("worker%s"%str(nr+1))
            #for nr in range(nrservers):
                #screens.append("server%s"%str(nr+1))
            #screens.append("appserver")
            #if console:
                #screens.append("console")
            #if qshell:
                #screens.append("qshell")
            #screens.append("logger")
            #screens.extend(extraScreens)
            #o.system.platformtype.screen.createSession("appserver6",screens)


            #for nr in range(nrworkers):
                #cmd = "python %s/start_worker.py -p %s -s %s" % (extpath,port, secret)
                #o.system.platformtype.screen.executeInScreen("appserver6","worker%s"%str(nr+1),cmd)

            #for nr in range(nrservers):
                ##ARUGMENTS TO START SCRIPT
                #cmd="python %s/start_server.py -p %s -s %s -w %s -d %s" % (extpath,port, secret, nrworkers, dbtype)
                #o.system.platformtype.screen.executeInScreen("appserver6","server%s"%str(nr+1),cmd)
            #if qshell:
                #o.system.platformtype.screen.executeInScreen("appserver6","qshell","/opt/qbase5/qshell")
            #o.system.platformtype.screen.executeInScreen("appserver6","logger","/opt/qbase5/qshell -l")

            #cmd = "python %s/start_server.py -p %s -s %s -w %s -d %s" % (extpath, 9000, secret, nrworkers, dbtype)
            #if not isMessageServer:
                #cmd += " --no-messagehandler"
            #o.system.platformtype.screen.executeInScreen("appserver6","appserver6",cmd)
