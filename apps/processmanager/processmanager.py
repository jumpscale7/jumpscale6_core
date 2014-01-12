#!/usr/bin/env python
from JumpScale import j

import JumpScale.grid.geventws
import time
import gevent
from gevent.event import Event
# import JumpScale.baselib.statmanager
import JumpScale.baselib.graphite
import psutil
import inspect

j.system.platform.psutil=psutil

import JumpScale.lib.diskmanager

import JumpScale.baselib.stataggregator

j.application.start("jsprocess_manager")

j.logger.consoleloglevel = 5

class Empty():
    pass

class MgrCmds():

    def __init__(self, daemon):
        self.daemon = daemon
        j.processmanager=self

        self.adminpasswd = j.application.config.get('system.superadmin.passwd')
        self.adminuser = j.application.config.get('system.superadmin.login')

        self.daemon._adminAuth=self._adminAuth
        
        masterip=j.application.config.get("grid.master.ip")
        self.daemon.osis = j.core.osis.getClient(masterip, user='root')

    def _init(self):
        
        self.loadMonitorObjectTypes()

    
        for key,cmdss in self.daemon.cmdsInterfaces.iteritems():

            for cmds in cmdss:
                print cmds            
                if key not in ["core"] and cmds.__dict__.has_key("_name"):
                    setattr(self, cmds._name, cmds)
        
        self.childrenPidsFound={} #children already found, to not double count

        self.jumpscripts.loadJumpscripts()

        self.osis_node=j.core.osis.getClientForCategory(self.daemon.osis,"system","node")
        self.osis_nic=j.core.osis.getClientForCategory(self.daemon.osis,"system","nic")
        self.osis_vdisk=j.core.osis.getClientForCategory(self.daemon.osis,"system","vdisk")
        self.osis_disk=j.core.osis.getClientForCategory(self.daemon.osis,"system","disk")
        self.osis_machine=j.core.osis.getClientForCategory(self.daemon.osis,"system","machine")
        

    def loadMonitorObjectTypes(self):
        j.processmanager.cache=Empty()
        for item in j.system.fs.listFilesInDir("monitoringobjects",filter="*.py"):
            name=j.system.fs.getBaseName(item).replace(".py","")
            if name[0]<>"_":
                monmodule = __import__('monitoringobjects.%s' % name)
                monmodule = getattr(monmodule, name)
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


    # def monitorProcess(self, domain="",name="",remember=False,**args):
    #     results={}
    #     for pd in self.manager.getProcessDefs(domain,name):
    #         t=pd.getStatInfo()
    #         t2={}
    #         for key in t.keys():
    #             results["processes.%s.%s.%s"%(pd.domain,pd.name,key)]=t[key]

    #     result2={}
    #     for key in results.keys():
    #         result2[key]=j.system.stataggregator.set(key,results[key],remember=remember)

    #     return result2


    # def monitorSystem(self,remember=False,session=None):
    #     from IPython import embed
    #     print "DEBUG NOW monitorSystem"
    #     embed()
        
        
        # results={}

        # return result2



daemon = j.servers.geventws.getServer(port=4445)

daemon.addCMDsInterface(MgrCmds, category="core")  # pass as class not as object !!! chose category if only 1 then can leave ""

cmds=daemon.daemon.cmdsInterfaces["core"][1]

for item in j.system.fs.listFilesInDir("processmanagercmds",filter="*.py"):
    name=j.system.fs.getBaseName(item).replace(".py","")
    if name[0]<>"_":
        exec ("from processmanagercmds.%s import *"%(name))
        classs=eval("%s"%name)
        tmp=classs(cmds)
        daemon.addCMDsInterface(classs, category=tmp._name)


cmds.daemon.schedule=daemon.schedule
cmds.daemon.parentdaemon=daemon

cmds._init()

daemon.start()

j.application.stop()
