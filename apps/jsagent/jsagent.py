from JumpScale import j

j.application.start("jsagent")
import time
import atexit
import psutil
import os
import select
import subprocess
from JumpScale.baselib import cmdutils
import JumpScale.grid.agentcontroller
import gevent
import gevent.monkey
from gevent.pywsgi import WSGIServer
import socket

gevent.monkey.patch_socket()
gevent.monkey.patch_time()

processes={}

import JumpScale.baselib.redis

#from lib.web import PMWSServer

import JumpScale.grid.processmanager


class Process():
    def __init__(self):
        self.name="unknown"
        self.domain=""
        self.instance="0"
        self.pid=0
        self.workingdir=None
        self.cmds=[]
        self.env=None
        self.pythonArgs={}
        self.pythonObj=None
        self.pythonCode=None
        self.logpath=None
        self.ports=[]
        self.psstring=""
        self.sync=False
        self.p=None

    def start(self):
        if self.cmds<>[]:
            self._spawnProcess()
        if self.pythonCode<>None:
            if self.sync:
                self.do()
            else:
                self.pid=os.fork()
                if self.pid==0:
                    self.do()
                else:
                    self.refresh()        

    def refresh(self):
        self.p= psutil.Process(self.pid)

    def kill(self):
        if self.p<>None:
            self.p.kill()

    def is_running(self):
        rss,vms=self.p.get_memory_info()
        return vms<>0

    def _spawnProcess(self):   
        if self.logpath==None:
            self.logpath=j.system.fs.joinPaths(j.dirs.logDir,"processmanager","logs","%s_%s_%s.log"%(self.domain,self.name,self.instance))
            j.system.fs.createDir(j.system.fs.joinPaths(j.dirs.logDir,"processmanager","logs"))
            f = open(self.logpath,'w')
        else:
            f=None

        try:            
            self.p = psutil.Popen(self.cmds, env=self.env,cwd=self.workingdir,stdin=subprocess.PIPE,stdout=f, stderr=subprocess.STDOUT,bufsize=0,shell=False) #f was: subprocess.PIPE
            self.pid=self.p.pid
        except Exception,e:
            print "could not execute:%s\nError:\n%s"%(self,e)

        time.sleep(0.1)
        if self.is_running()==False:
            print "could not execute:%s\n"%(self)
            log=j.system.fs.fileGetContents(self.logpath)
            print "log:\n%s"%log
        
        # while(True):
        #     # retcode = self.p.poll() #returns None while subprocess is running
        #     # if select.select([self.p.stdout],[],[],0)[0]!=[]:
        #     #     line = self.p.stdout.read(1)
        #     #     print line,
        #     # if(retcode is not None):
        #     #     break
        #     time.sleep(1)

        # print "subprocess stopped"        

    def do(self):
        print 'A new child ',  os.getpid( )
        if self.pythonCode<>None:
            exec(self.pythonCode)

        os._exit(0)  

    def __str__(self):
        return "%s"%self.__dict__

    __repr__=__str__


class ProcessManager():
    def __init__(self,reset=False):
        self.processes={}

        #check there is a redis on port 9998 & 9999 (the new port for all)
        for port in [9999,9998,8001]:
            if j.system.net.tcpPortConnectionTest("localhost",port):
                j.system.process.killProcessByPort(port)

        jp=j.packages.findNewest("jumpscale","redis")
        if not jp.isInstalled(instance="mem"):
            jp.install(hrddata={"redis.name":"mem","redis.port":9999,"redis.disk":"0","redis.mem":20},instance="mem")
        if not jp.isInstalled(instance="disk"):
            jp.install(hrddata={"redis.name":"disk","redis.port":9998,"redis.disk":"1","redis.mem":20},instance="disk")

        for name in ["mem","disk"]:
            p=Process()
            p.domain="jumpscale"
            p.name="redis_%s"%name
            p.instance=name
            p.workingdir="/"
            p.cmds=[j.dirs.replaceTxtDirVars("$base/apps/redis/redis-server"),j.dirs.replaceTxtDirVars("$vardir/redis/%s/redis.conf"%name)]
            p.logpath=j.dirs.replaceTxtDirVars("$vardir/redis/%s/redis.log"%name)
            p.start()
            self.processes[p.pid]=p

        if j.system.net.waitConnectionTest("localhost",9999,2)==False or j.system.net.waitConnectionTest("localhost",9998,2)==False:
            j.events.opserror_critical("could not start redis on port 9998 or 9999 inside processmanager",category="processmanager.redis.start")

        self.redis_mem=j.clients.redis.getGeventRedisClient("localhost",9999)
        self.redis_disk=j.clients.redis.getGeventRedisClient("localhost",9998)

        self.redis_queues={}
        self.redis_queues["io"] = j.clients.redis.getGeventRedisQueue("localhost",9999,"workers:work:io")
        self.redis_queues["hypervisor"] = j.clients.redis.getGeventRedisQueue("localhost",9999,"workers:work:hypervisor")
        self.redis_queues["default"] = j.clients.redis.getGeventRedisQueue("localhost",9999,"workers:work:default")
        self.redis_queues["process"] = j.clients.redis.getGeventRedisQueue("localhost",9999,"workers:work:process")        

        j.processmanager=self

        self.hrd=j.application.instanceconfig
        acip=self.hrd.get("ac.ipaddress")
        acport=self.hrd.getInt("ac.port")
        aclogin=self.hrd.get("ac.login",default="node")
        acpasswd=self.hrd.get("ac.passwd",default="")

        if self.hrd.get("ac.ipaddress")<>"":
            #processmanager enabled
            while j.system.net.waitConnectionTest(acip,acport,2)==False:
                print "cannot connect to agentcontroller, will retry forever: '%s:%s'"%(acip,acport)

            #now register to agentcontroller
            self.acclient = j.clients.agentcontroller.get(acip, login=aclogin, passwd=acpasswd)
            res=self.acclient.registerNode(hostname=socket.gethostname(), machineguid=j.application.getUniqueMachineId())
            nid=res["node"]["id"]
            webdiskey=res["webdiskey"]
            j.application.config.set("grid.node.id",nid)
            j.application.config.set("agentcontroller.webdiskey",webdiskey)
            j.application.config.set("grid.id",res["node"]["gid"])
            j.application.config.set("grid.node.machineguid",j.application.getUniqueMachineId())
            j.application.config.set("grid.master.ip",acip)
            if aclogin=="root":
                j.application.config.set("grid.master.superadminpasswd",acpasswd)
            self.acclient=j.clients.agentcontroller.getByInstance('main')

            jp=j.packages.findNewest("jumpscale","webdis_client")
            if reset or not jp.isInstalled(instance="main"):                
                jp.install(hrddata={"addr":acip,"port":7779},instance="main",reinstall=reset)

            jp=j.packages.findNewest("jumpscale","osis_client")
            if reset or not jp.isInstalled(instance="processmanager"):
                jp.install(hrddata={"osis.client.addr":acip,"osis.client.port":5544,"osis.client.login":aclogin,"osis.client.passwd":acpasswd},instance="processmanager",reinstall=reset)
                self.hrd.set("osis.connection","processmanager")

            jp=j.packages.findNewest("jumpscale","agentcontroller_client")
            if reset or not jp.isInstalled(instance="main"):
                jp.install(hrddata={"agentcontroller.client.addr":acip,"agentcontroller.client.port":4444,"agentcontroller.client.login":aclogin},instance="main",reinstall=reset)
        
    def start(self):

        # self._webserverStart()        
        self._workerStart()
        self._processManagerStart()

        self.mainloop()

    def _webserverStart(self):
        #start webserver
        server=PMWSServer()
        server.pm=self

        p=Process()
        p.domain="jumpscale"
        p.name="web"
        p.instance="main"
        p.workingdir="/"
        p.pythonObj=server
        p.pythonCode="self.pythonObj.start()"
        p.start()
        self.processes[p.pid]=p

    def _processManagerStart(self):
        p=Process()
        p.domain="jumpscale"
        p.name="processmanager"
        p.instance="main"
        p.workingdir="/"
        p.pythonObj=j.core.processmanager
        p.pythonCode="self.pythonObj.start()"
        p.sync=True
        p.start()
        self.processes[p.pid]=p

    def _worker(self,qname):
        worker=Worker(qname)
        worker.run()

    def _workerStart(self):
    
        j.core.osis.client = j.core.osis.getClientByInstance(die=True)

        if j.application.config.exists("grid.id"):
            j.application.initGrid()

        j.logger.consoleloglevel = 2
        j.logger.maxlevel=7

        #below should be non blocking because of redis but does not seem the case?
        for qname in ["default","io","process","hypervisor"]:
            gevent.spawn(self._worker,qname)
            # worker=Worker(qname)
            # worker.run()            
 

    def mainloop(self):
        i=0
        while True:
            i+=1
            # print "NEXT:%s\n"%i    
            toremove=[]        
            for pid,p in self.processes.iteritems():
                # p.refresh()        
                if p.p<>None:        
                    if p.is_running():
                        pass
                    else:
                        toremove.append(pid)
                        pass
                        # print "STOPPED:%s"%p
            for item in toremove:
                p=self.processes[item]
                #make sure you kill
                p.kill()
                self.processes.pop(item)
            time.sleep(1)
            if len(self.processes.keys())==0:
                print "no more children"
                # return
            print len(self.processes.keys())
        

@atexit.register
def kill_subprocesses():
    for pid,p in processes.iteritems():
        p.kill()        


parser = cmdutils.ArgumentParser()
parser.add_argument("-i", '--instance', default="0", help='jsagent instance', required=False)
parser.add_argument("-r", '--reset', action='store_true',help='jsagent reset', required=False,default=False)

opts = parser.parse_args()

jp=j.packages.findNewest("jumpscale","jsagent")
if opts.reset or not jp.isInstalled(instance=opts.instance):
    jp.install(instance=opts.instance,reinstall=opts.reset)

jp = j.packages.findNewest('jumpscale', 'jsagent')
jp.load(opts.instance)
j.application.instanceconfig = jp.hrd_instance

#first start processmanager with all required stuff
pm=ProcessManager(reset=opts.reset)
processes=pm.processes


from lib.worker import Worker

pm.start()

j.application.stop()
