#!/usr/bin/env python
from JumpScale import j

import JumpScale.grid.geventws
import time
# import JumpScale.baselib.statmanager
import JumpScale.baselib.graphite
import psutil
import importlib
import sys

j.system.platform.psutil=psutil

import JumpScale.lib.diskmanager

import JumpScale.baselib.stataggregator

j.application.start("jumpscale:jsprocessmanager")

j.logger.consoleloglevel = 5

#check redis is there if not try to start
if not j.system.net.tcpPortConnectionTest("127.0.0.1",7768):
    j.packages.findNewest(name="redis").install()
    j.packages.findNewest(name="redis").start()


def checkosis():
    masterip=j.application.config.get("grid.master.ip")
    osis = j.core.osis.getClient(masterip, user='root')

def checkagentcontroller():
    masterip=j.application.config.get("grid.master.ip")
    client=j.clients.agentcontroller.get(masterip)
    return client
    
import JumpScale.grid.agentcontroller

j.tools.startupmanager.startProcess("jumpscale","osis")

masterip=j.application.config.get("grid.master.ip")
if masterip in j.system.net.getIpAddresses():

    if not j.tools.startupmanager.exists("jumpscale","osis"):
        raise RuntimeError("Could not find osis installed on local system, please install.")

    if not j.tools.startupmanager.exists("jumpscale","agentcontroller"):
        raise RuntimeError("Could not find osis installed on local system, please install.")
    
    if not j.system.net.tcpPortConnectionTest("127.0.0.1",5544):
        j.tools.startupmanager.startProcess("jumpscale","osis")
    if not j.system.net.tcpPortConnectionTest("127.0.0.1",4444):        
        j.tools.startupmanager.startProcess("jumpscale","agentcontroller")

success=False
while success==False:
    try:
        checkosis()
        cl=checkagentcontroller()
        success=True
    except Exception,e:
        msg="Cannot connect to osis or agentcontroller on %s, will retry in 5 sec."%(masterip)
        j.events.opserror(msg, category='processmanager.startup', e=e)
        time.sleep(5)
    


#delete previous scripts
todel=["eventhandling","loghandling","monitoringobjects","processmanagercmds"]
for delitem in todel:
    j.system.fs.removeDirTree(delitem)

#import new code
#download all monitoring & cmd scripts

import tarfile
scripttgz=cl.getProcessmanagerScripts()
ppath="/tmp/processMgrScripts_%s.tar"%j.base.idgenerator.generateRandomInt(1,1000000)
j.system.fs.writeFile(ppath,scripttgz)
tar = tarfile.open(ppath, "r:bz2")

# tmppath="/tmp/%s"%j.base.idgenerator.generateRandomInt(1,100000)
for tarinfo in tar:
    if tarinfo.isfile():
        if tarinfo.name.find("processmanager/")==0:
            dest=tarinfo.name.replace("processmanager/","")           
            tar.extract(tarinfo.name, "/opt/jumpscale/apps")
            # j.system.fs.createDir(j.system.fs.getDirName(dest))
            # j.system.fs.moveFile("%s/%s"%(tmppath,tarinfo.name),dest)
# j.system.fs.removeDirTree(tmppath)
j.system.fs.remove(ppath)

j.core.grid.init()

class Empty():
    pass

class MgrCmds():

    def __init__(self, daemon):
        self.daemon = daemon
        j.processmanager=self

        self.adminpasswd = j.application.config.get('grid.master.superadminpasswd')
        self.adminuser = 'root'#j.application.config.get('system.superadmin.login')

        self.daemon._adminAuth=self._adminAuth
        
        masterip=j.application.config.get("grid.master.ip")
        self.daemon.osis = j.core.osis.getClient(masterip, user='root')

    def _init(self):
        self.loadMonitorObjectTypes()
        for key,cmdss in self.daemon.cmdsInterfaces.iteritems():

            for cmds in cmdss:
                print cmds
                if key != 'core':
                    if hasattr(cmds, '_name'):
                        setattr(self, cmds._name, cmds)
                    if hasattr(cmds, '_init'):
                        cmds._init()
        
        self.childrenPidsFound={} #children already found, to not double count

    def loadMonitorObjectTypes(self):
        j.processmanager.cache=Empty()
        for item in j.system.fs.listFilesInDir("monitoringobjects",filter="*.py"):
            name=j.system.fs.getBaseName(item).replace(".py","")
            if name[0]<>"_":
                monmodule = importlib.import_module('monitoringobjects.%s' % name)
                classs=getattr(monmodule, name)
                print "load factory:%s"%name
                factory = getattr(monmodule, '%sFactory' % name)(self, classs)
                j.processmanager.cache.__dict__[name.lower()]=factory        

    def getMonitorObject(self,name,id,monobject=None,lastcheck=0,session=None):
        if session<>None:
            self._adminAuth(session.user,session.passwd)

        if not j.processmanager.__dict__.has_key(name):
            raise RuntimeError("Could not find factory for monitoring object:%s"%name)

        if lastcheck==0:
            lastcheck=time.time()
        val=j.processmanager.__dict__[name].get(id,monobject=monobject,lastcheck=lastcheck)
        if session<>None:
            return val.__dict__
        else:
            return val

    def _adminAuth(self,user,passwd):
        if user != self.adminuser or passwd != self.adminpasswd:
            raise RuntimeError("permission denied")           



daemon = j.servers.geventws.getServer(port=4445)

daemon.addCMDsInterface(MgrCmds, category="core")  # pass as class not as object !!! chose category if only 1 then can leave ""

cmds=daemon.daemon.cmdsInterfaces["core"][1]

class DummyDaemon():
    def _adminAuth(self,user,passwd):
        raise RuntimeError("permission denied")

sys.path.append(j.system.fs.getcwd())
for item in j.system.fs.listFilesInDir("processmanagercmds",filter="*.py"):
    name=j.system.fs.getBaseName(item).replace(".py","")
    if name[0]<>"_":
        module = importlib.import_module('processmanagercmds.%s' % name)
        classs = getattr(module, name)
        tmp=classs()
        daemon.addCMDsInterface(classs, category=tmp._name)

cmds.daemon.schedule=daemon.schedule
cmds.daemon.parentdaemon=daemon
cmds._init()

daemon.start()

j.application.stop()
