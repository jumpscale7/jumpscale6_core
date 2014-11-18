from JumpScale import j
import JumpScale.baselib.remote
import sys
# import importlib
import imp
try:
    import ujson as json
except:
    import json

import JumpScale.baselib.redis
import copy
import time
import JumpScale.baselib.webdis

from fabric.api import hide
import time

redis=j.clients.redis.getRedisClient("127.0.0.1", 9999)

class ScriptRun():
    def __init__(self):
        self.runid=j.admin.runid
        self.epoch=int(time.time())
        self.error=""
        self.result=""
        self.state="OK"
        self.out=""
        self.extraArgs=""
        self.gridname=""
        self.nodename=""

    def __str__(self):
        return str(self.__dict__)

    __repr__=__str__

class JNode():
    def __init__(self):
        self.actionsDone={}
        self.lastcheck=0
        self.gridname=""
        self.name=""
        self.ip=""
        self.host=""
        self.enabled=True
        self.remark=""
        self.roles=[]
        self.passwd=None
        self._basepath=j.dirs.replaceTxtDirVars(j.application.config.get("admin.basepath"))
        self.cuapi=None
        self.args=None
        self.currentScriptRun=None

    def getScriptRun(self):
        if self.currentScriptRun==None:
            self.currentScriptRun=ScriptRun()
            self.currentScriptRun.gridname=self.gridname
            self.currentScriptRun.nodename=self.name
        return self.currentScriptRun

    def executeCmds(self,cmds,die=True,insandbox=False):
        scriptRun=self.getScriptRun()
        out=scriptRun.out
        for line in cmds.split("\n"):
            if line.strip()<>"" and line[0]<>"#":
                self.log("execcmd",line)
                if insandbox:
                    line2="source /opt/jsbox/activate;%s"%line 
                else:
                    line2=line               
                try:                    
                    out+="%s\n"%self.cuapi.run(line2)
                except BaseException,e:
                    if die:
                        self.raiseError("execcmd","error execute:%s"%line,e)

    def killProcess(self,filterstr,die=True):
        found=self.getPids(filterstr)
        for item in found:
            self.log("killprocess","kill:%s"%item)
            try:
                self.cuapi.run("kill -9 %s"%item)
            except Exception,e:
                if die:
                    self.raiseError("killprocess","kill:%s"%item,e)

    def getPids(self,filterstr,die=True):
        self.log("getpids","")
        with hide('output'):
            try:
                out=self.cuapi.run("ps ax")
            except Exception,e:
                if die:
                    self.raiseError("getpids","ps ax",e)
        found=[]
        for line in out.split("\n"):
            if line.strip()<>"":
                if line.find(filterstr)<>-1:
                    line=line.strip()
                    found.append(int(line.split(" ")[0]))   
        return found

    def jpackageStop(self,name,filterstr,die=True):
        self.log("jpackagestop","%s (%s)"%(name,filterstr))
        try:
            self.cuapi.run("source /opt/jsbox/activate;jpackage stop -n %s"%name)
        except Exception,e:
            if die:
                self.raiseError("jpackagestop","%s"%name,e)
        
        found=self.getPids(filterstr)
        if len(found)>0:
            for item in found:
                try:
                    self.cuapi.run("kill -9 %s"%item)            
                except:
                    pass

    def jpackageStart(self,name,filterstr,nrtimes=1,retry=1):
        found=self.getPids(filterstr)
        self.log("jpackagestart","%s (%s)"%(name,filterstr))
        for i in range(retry):
            if len(found)==nrtimes:
                return
            scriptRun=self.getScriptRun()
            try:
                self.cuapi.run("source /opt/jsbox/activate;jpackage start -n %s"%name)  
            except Exception,e:
                if die:
                    self.raiseError("jpackagestart","%s"%name,e)                          
            time.sleep(1)
            found=self.getPids(filterstr)
        if len(found)<nrtimes:
            self.raiseError("jpackagestart","could not jpackageStart %s"%name)

    def serviceStop(self,name,filterstr):
        self.log("servicestop","%s (%s)"%(name,filterstr))
        try:
            self.cuapi.run("sudo stop %s"%name)
        except:
            pass
        found=self.getPids(filterstr)
        scriptRun=self.getScriptRun()
        if len(found)>0:
            for item in found:
                try:
                    self.cuapi.run("kill -9 %s"%item)            
                except:
                    pass
        found=self.getPids(filterstr)
        if len(found)>0:
            self.raiseError("servicestop","could not serviceStop %s"%name)

    def serviceStart(self,name,filterstr,die=True):
        self.log("servicestart","%s (%s)"%(name,filterstr))
        found=self.getPids(filterstr)
        if len(found)==0:
            try:
                self.cuapi.run("sudo start %s"%name)          
            except:
                pass            
        found=self.getPids(filterstr)
        if len(found)==0 and die:
            self.raiseError("servicestart","could not serviceStart %s"%name)            

    def serviceReStart(self,name,filterstr):
        self.serviceStop(name,filterstr)
        self.serviceStart(name,filterstr)

    def raiseError(self,action,msg,e=None):
        scriptRun=self.getScriptRun()
        scriptRun.state="ERROR"
        if e<>None:
            msg="Stack:\n%s\nError:\n%s\n"%(j.errorconditionhandler.parsePythonErrorObject(e),e)
            scriptRun.state="ERROR"
            scriptRun.error+=msg

        for line in msg.split("\n"):
            toadd="%-10s: %s\n" % (action,line)
            scriptRun.error+=toadd
            print "**ERROR** %-10s:%s"%(self.name,toadd)
        self.lastcheck=0
        j.admin.setNode(self)
        j.admin.setNode(self)
        raise RuntimeError("**ERROR**")

    def log(self,action,msg):
        out=""
        for line in msg.split("\n"):
            toadd="%-10s: %s\n" % (action,line)
            print "%-10s:%s"%(self.name,toadd)
            out+=toadd

    def setpasswd(self,passwd):
        #this will make sure new password is set
        self.log("setpasswd","")
        cl=j.tools.expect.new("sh")
        if self.args.seedpasswd=="":
           self.args.seedpasswd=self.findpasswd()
        try:
            cl.login(remote=self.name,passwd=passwd,seedpasswd=None)
        except Exception,e:
            self.raiseError("setpasswd","Could not set root passwd.")

    def findpasswd(self):
        self.log("findpasswd","find passwd for superadmin")
        cl=j.tools.expect.new("sh")
        for passwd in j.admin.rootpasswds:
            try:            
                pass
                cl.login(remote=self.name,passwd=passwd,seedpasswd=None)
            except Exception,e:
                self.raiseError("findpasswd","could not login using:%s"%passwd,e)
                continue
            self.passwd=passwd
            j.admin.setNode(self)
        return "unknown"

    def check(self):
        j.base.time.getTimeEpoch()

    def connectSSH(self):
        return self._connectCuapi()

    def _connectCuapi(self):
        if self.ip == "":
            if j.system.net.pingMachine(self.args.remote,1):
                self.ip=self.args.remote
            else:
                j.events.opserror_critical("Could not ping node:'%s'"% self.args.remote)

        self.cuapi.connect(self.ip)

        if self.args.passwd<>"":
            # setpasswd()
            j.remote.cuisine.fabric.env["password"]=self.args.passwd
        elif self.passwd<>None and self.passwd<>"unknown":
            # setpasswd()
            j.remote.cuisine.fabric.env["password"]=self.passwd
        # else:
        #     self.findpasswd()

        return self.cuapi

    def uploadFromCfgDir(self,ttype,dest,additionalArgs={}):
        dest=j.dirs.replaceTxtDirVars(dest)
        cfgdir=j.system.fs.joinPaths(self._basepath, "cfgs/%s/%s"%(j.admin.args.cfgname,ttype))

        additionalArgs["hostname"]=self.name

        cuapi=self.cuapi
        if j.system.fs.exists(path=cfgdir):
            self.log("uploadcfg","upload from %s to %s"%(ttype,dest))

            tmpcfgdir=j.system.fs.getTmpDirPath()
            j.system.fs.copyDirTree(cfgdir,tmpcfgdir)
            j.dirs.replaceFilesDirVars(tmpcfgdir)
            j.application.config.applyOnDir(tmpcfgdir,additionalArgs=additionalArgs)

            items=j.system.fs.listFilesInDir(tmpcfgdir,True)
            done=[]
            for item in items:
                partpath=j.system.fs.pathRemoveDirPart(item,tmpcfgdir)
                partpathdir=j.system.fs.getDirName(partpath).rstrip("/")
                if partpathdir not in done:
                    cuapi.dir_ensure("%s/%s"%(dest,partpathdir), True)
                    done.append(partpathdir)
                try:            
                    cuapi.file_upload("%s/%s"%(dest,partpath),item)#,True,True)  
                except Exception,e:
                    j.system.fs.removeDirTree(tmpcfgdir)
                    self.raiseError("uploadcfg","could not upload file %s to %s"%(ttype,dest))
            j.system.fs.removeDirTree(tmpcfgdir)

    def upload(self,source,dest):
        args=j.admin.args
        if not j.system.fs.exists(path=source):
            self.raiseError("upload","could not find path:%s"%source)
        self.log("upload","upload %s to %s"%(source,dest))
        # from IPython import embed
        # print "DEBUG NOW implement upload in Admin"  #@todo
        # embed()
    
        for item in items:
            partpath=j.system.fs.pathRemoveDirPart(item,cfgdir)
            partpathdir=j.system.fs.getDirName(partpath).rstrip("/")
            if partpathdir not in done:
                print cuapi.dir_ensure("%s/%s"%(dest,partpathdir), True)
                done.append(partpathdir)            
            cuapi.file_upload("%s/%s"%(dest,partpath),item)#,True,True)                       

    def __repr__(self):
        roles=",".join(self.roles)
        return ("%-10s %-10s %-50s %-15s %-10s %s"%(self.gridname,self.name,roles,self.ip,self.host,self.enabled))

    __str__=__repr__

class AdminFactory:
    def get(self,args,failWhenNotExist=False):
        return Admin(args,failWhenNotExist)

class Admin():
    def __init__(self,args,failWhenNotExist=False):
        self.args=args
        self._basepath=j.dirs.replaceTxtDirVars(j.application.config.get("admin.basepath"))
        self.hostKeys=[]
        self.gridNameAliases={}
        if args.action==None or (not args.action in ["createidentity","applyconfiglocal"]):
            if args.local:
                args.remote="127.0.0.1"
                args.passwd=""
            # else:
            #     if args.remote =="":
            #         args.remote=j.console.askString("Ip address of remote")    
                #create ssh connection
            self.cuapi = j.remote.cuisine.api      
            if args.g:
                roles = list()
                if args.roles:
                    roles = args.roles.split(",")
                #@todo change to use hostkeys (reem)
                raise RuntimeError("not implemented")
                nodes = self._getActiveNodes()
                hosts = [node['name'] for node in nodes]
                for node in nodes:
                    for role in roles:
                        if role not in node['roles']:
                            hosts.remove(node['name'])
                            break
                self.hostKeys = hosts
                self.hostKeys.sort()
            elif args.remote=="" and  args.gridname<>"":
                for gridname in args.gridname.split(","):
                    for hostKey in self.getHostNamesKeys(args.gridname):
                        self.hostKeys.append(hostKey)
            else:
                for gridname in args.gridname.split(","):
                    self.hostKeys+=["%s__%s"%(gridname,item) for item in args.remote.split(",")]

            self.hostKeys.sort()
            # if hosts<>[]:
            #     if failWhenNotExist==False:
            #         for host in hosts:
            #             #check 
            #             if j.system.net.tcpPortConnectionTest("m3pub",22):
            #                 self.cuapi.fabric.api.env["hosts"].append(host)
            #                 self.hostKeys.append(host)
            #     else:
            #         self.hostKeys=hosts
            #         self.cuapi.fabric.api.env["hosts"]=hosts
            # else:            
            #     self.cuapi.connect(args.remote)
        self.sysadminPasswd=""
        self.js={}        
        # DO NOT USE CREDIS IN THIS CONTEXT, NOT THREAD SAFE
        self.redis = j.clients.redis.getRedisClient("127.0.0.1", 9999)
        # self.nodes={}
        self.hrd= j.core.hrd.getHRD(self._getPath("cfg/","superadmin.hrd"))
        self.rootpasswds=self.hrd.getList("superadmin.passwds")
        self.loadJumpscripts()
        self.loadNodes()
        if self.args.runid<>"":
            self.runid=self.args.runid
        else:
            self.runid=self.redis.incr("admin:scriptrunid")
        if self.args.__dict__.has_key("reset") and self.args.reset:
            self.deleteScriptRunInfo()
        # 
        # self.config2gridmaster() #this should not be done every time

    def reset(self):
        #clear redis
        self.redis.delete("admin:nodes")
        self.redis.delete("admin:scriptruns")

    def _getActiveNodes(self):
        import JumpScale.grid.osis
        oscl = j.core.osis.getClientByInstance('main')
        ncl = j.core.osis.getClientForCategory(oscl, 'system', 'node')
        return ncl.simpleSearch({'active': True})

    def _getPath(self,sub,file=""):        
        path= "%s/%s"%(self._basepath,sub)
        path=path.replace("\\","/")
        path=path.replace("//","/")
        if path[-1]<>"/":
            path+="/"
        if file<>"":
            path+=file
        return path

    def raiseError(self,action,msg,e=None):
        #@todo make better
        raise RuntimeError("%s;%s"%(action,msg))

    def getNode(self,gridname="",name=""):
        name=name.lower()
        gridname=gridname.lower()

        if gridname=="" and name=="":
            node=JNode()
            node.cuapi=self.cuapi
            node.currentScriptRun=None
            node.getScriptRun()
            node.args=self.args
            return node

        if gridname=="":
            if j.system.net.pingMachine(name.strip("/").strip(),1):
                node=JNode()
                node.ip=name
                node.hostname=name
                node.args=self.args
                node.cuapi=self.cuapi
                node.currentScriptRun=None
                node.getScriptRun()
                return node
            else:
                raise RuntimeError("Could not find node:'%s'"%name)

        
        if self.redis.hexists("admin:nodes","%s:%s"%(gridname,name))==False:
            raise RuntimeError("could not find node: '%s/%s'"%(gridname,name))
            # node=JNode()
            # node.ip=name
            # node.host=name
        else:
            data=self.redis.hget("admin:nodes","%s:%s"%(gridname,name))
            node=JNode()
            try:
                node.__dict__.update(json.loads(data))
            except Exception,e:
                raise RuntimeError("could not decode node: '%s/%s'"%(gridname,name))
                # node=JNode()
                # self.setNode(node)
        node.args=self.args
        node.gridname=gridname
        node.name=name
        node.cuapi=self.cuapi
        node.currentScriptRun=None
        node._connectCuapi()
        return node 

    def setNode(self,node):
        node2=copy.copy(node.__dict__)
        for key in node2.keys():
            if key[0]=="_":
                node2.pop(key)
        node2.pop("cuapi")
        node2.pop("args")
        node2.pop("currentScriptRun")
        
        self.redis.hset("admin:nodes","%s:%s"%(node.gridname,node.name),json.dumps(node2))
        sr=node.currentScriptRun
        if sr<>None:
            self.redis.hset("admin:scriptruns","%s:%s:%s"%(node.gridname,node.name,sr.runid),json.dumps(sr.__dict__))

    def executeForNode(self,node,jsname,once=True,sshtest=True,**kwargs):
        """
        return node
        """
        sr=node.currentScriptRun
        jsname=jsname.lower()
        now= j.base.time.getTimeEpoch()
        do=True
        if once:
            for item in self.getScriptRunInfo():
                if item.state=="OK" and item.nodename==node.name and item.gridname==node.gridname:
                    do=False
            
        # if self.args.force:
        #     do=True
        if do:
            print "* tcp check ssh"
            if not j.admin.js.has_key(jsname):
                self.raiseError("executejs","cannot find js:%s"%jsname)

            if sshtest and not j.system.net.waitConnectionTest(node.ip,22, self.args.timeout):
                self.raiseError("executejs","jscript:%s,COULD NOT check port (ssh)"%jsname)
                return
            try:                
                sr.result=j.admin.js[jsname](node=node,**kwargs)
                node.actionsDone[jsname]=now
                node.lastcheck=now
            except BaseException,e:
                msg="error in execution of %s.Stack:\n%s\nError:\n%s\n"%(jsname,j.errorconditionhandler.parsePythonErrorObject(e),e)
                sr.state="ERROR"
                sr.error+=msg
                print 
                print msg
                if node.actionsDone.has_key(jsname):
                    node.actionsDone.pop(jsname)
            self.setNode(node)
        else:
            print("No need to execute %s on %s/%s"%(jsname,node.gridname,node.name))
        return node

    def execute(self,jsname,once=True,reset=False,**kwargs):
        res=[]
        for host in self.hostKeys:
            gridname, _, name = host.partition('__')
            node=self.getNode(gridname,name)
            self.executeForNode(node,jsname,once,**kwargs)

    def loadJumpscripts(self):
        # print "load jumpscripts ",
        sys.path.append(self._getPath("jumpscripts"))        
        cmds=j.system.fs.listFilesInDir(self._getPath("jumpscripts"), recursive=True, filter="*.py")
        cmds.sort()
        for item in cmds:
            name=j.system.fs.getBaseName(item).replace(".py","")
            if name[0]<>"_":
                name=name.lower()
                # print "load:%s"%name
                # module = importlib.import_module('jscripts.%s' % name)
                module=imp.load_source('jscript_%s' % name, item)
                self.js[name]= getattr(module, "action")

    def getWebDis(self,enable=True):
        webdis=None
        if enable and j.application.config.exists("grid.watchdog.secret"):
            if j.application.config.exists("grid_master_ip") and j.system.net.tcpPortConnectionTest(j.application.config.get("grid_master_ip"),7779):
                webdis=j.clients.webdis.get(j.application.config.get("grid_master_ip"),7779)
        return webdis

    def loadNodes(self,webdis=False,pprint =False):
        """
        load nodes from config files
        """

        webdis=self.getWebDis(webdis)

        for configpath in j.system.fs.listFilesInDir("%s/apps/admin/cfg"%j.dirs.baseDir,filter="*.cfg"):

            gridname=j.system.fs.getBaseName(configpath).lower().strip()
            if gridname =="active.cfg":
                continue
            gridname=gridname[:-4]
            
            if webdis<>None:  
                key="%s:admin:nodes:%s"%(j.application.config.get("grid_watchdog_secret"),gridname)
                webdis.delete(key)

            nodes = list()
            config = j.config.getConfig(configpath[:-4])

            self.gridNameAliases[gridname.lower()]=[]
            if config.has_key("main"):
                for alias in config["main"].get("alias","").split(","):
                    if alias.lower() not in self.gridNameAliases[gridname.lower()]:
                        self.gridNameAliases[gridname.lower()].append(alias.lower())

            for name, host in config.iteritems():
                node=JNode()
                node.gridname=gridname
                node.name = name
                node.remark = host.get('remark')
                node.ip = host.get('ip')
                node.host = host.get('host')
                node.roles = host.get('roles', '').split(',')
                node.enabled = False if host.get('enabled', '1')  == '1' else True
                self.setNode(node)
                nodes.append(node)
                if webdis<>None:
                    webdis.hset(key,node.name,json.dumps(node.__dict__))

            if pprint:
                line = "Grid %s" % gridname
                print line
                print "=" * len(line)
                print ""
                for node in sorted(nodes, key=lambda x: x.name):
                    print node
                print ''

    def config2gridmaster(self):
        webdis=self.getWebDis()
        if webdis==None:
            raise RuntimeError("cannot connect to webdis, is gridmaster running webdis?")
        self.loadNodes(webdis=True,pprint=False)
        sys.path.append(self._getPath("jumpscripts"))        
        cmds=j.system.fs.listFilesInDir(self._getPath("jumpscripts"), recursive=True, filter="*.py")
        cmds.sort()

        def getcode(path):
            state="start"
            code=""
            for line in j.system.fs.fileGetContents(path).split("\n"):
                if line.find("def action(")<>-1:
                    state="found"
                if state=="found":
                    code+="%s\n"%line
            return code

        key="%s:admin:jscripts"%(j.application.config.get("grid_watchdog_secret"))
        webdis.delete(key)

        for item in cmds:
            name=j.system.fs.getBaseName(item).replace(".py","")
            if name[0]<>"_":
                obj={}
                name=name.lower()
                # print "load:%s"%name
                module=imp.load_source('jscript_%s' % name, item)
                obj["descr"]= getattr(module, "descr","")
                obj["version"]= getattr(module, "version","")
                obj["organization"]= getattr(module, "organization","unknown")
                obj["version"]= getattr(module, "version","1.0")
                obj["code"]=getcode(item)
                
                webdis.hset(key,name,json.dumps(obj))
                # ret=json.loads(self.webdis.hget(key,name))
        
        # print "OK"

    def sshfs(self,gridname,name):
        node=self.getNode(gridname,name)
        if name<>"admin":
            path="/mnt/%s_%s_jsbox"%(node.gridname,node.name)
            j.system.fs.createDir(path)
            cmd="sshfs %s:/opt/jsbox /mnt/%s_%s_jsbox"%(node.ip,node.gridname,node.name)
            print cmd
            j.system.process.executeWithoutPipe(cmd)

            path="/mnt/%s_%s_jsboxdata"%(node.gridname,node.name)
            j.system.fs.createDir(path)
            print cmd
            cmd="sshfs %s:/opt/jsbox_data /mnt/%s_%s_jsboxdata"%(node.ip,node.gridname,node.name)
            j.system.process.executeWithoutPipe(cmd)
        else:
            path="/mnt/%s_%s_code"%(node.gridname,node.name)
            j.system.fs.createDir(path)
            cmd="sshfs %s:/opt/code /mnt/%s_%s_code"%(node.ip,node.gridname,node.name)
            print cmd
            j.system.process.executeWithoutPipe(cmd)
            path="/mnt/%s_%s_jumpscale"%(node.gridname,node.name)
            j.system.fs.createDir(path)
            cmd="sshfs %s:/opt/jumpscale /mnt/%s_%s_jumpscale"%(node.ip,node.gridname,node.name)
            print cmd
            j.system.process.executeWithoutPipe(cmd)

    def sshfsumount(self,gridname="",name=""):
        rc,mount=j.system.process.execute("mount")
        

        def getMntPath(mntpath):
            for line in mount.split("\n"):
                if line.find("sshfs")<>-1 and line.find(mntpath+" ")<>-1:
                    return line.split(" ")[0]
            return None

        def getMntPaths():
            res=[]
            for line in mount.split("\n"):
                if line.find("sshfs")<>-1:
                    line=line.replace("  "," ")
                    line=line.replace("  "," ")                    
                    res.append(line.split(" ")[2])
            return res


        def do(mntpath):
            mntpath2=getMntPath(mntpath)
            if mntpath2==None:
                return None
                
            cmd="umount %s"%(mntpath2)
            rc,out=j.system.process.execute(cmd,False)
            if rc>0:
                if out.find("device is busy")<>-1:
                    res=[]
                    print "MOUNTPOINT %s IS BUSY WILL TRY TO FIND WHAT IS KEEPING IT BUSY"%mntpath
                    cmd ="lsof -bn -u 0|grep '%s'"%mntpath  #only search for root processes
                    print cmd
                    rc,out=j.system.process.execute(cmd,False)
                    for line in out.split("\n"):
                        if line.find(mntpath)<>-1 and line.lower().find("avoiding")==-1 and line.lower().find("warning")==-1:
                            line=line.replace("  "," ")
                            line=line.replace("  "," ")
                            cmd=line.split(" ")[0]
                            pid=line.split(" ")[1]
                            key="%s (%s)"%(cmd,pid)
                            if key not in res:
                                res.append(key)
                    print "PROCESSES WHICH KEEP MOUNT BUSY:"
                    print "\n".join(res)                    
                    return
                raise RuntimeError("could not umount:%s\n%s"%(mntpath,out))

        if gridname=="" and name=="":
            for mntpath in getMntPaths():
                print "UMOUNT:%s"%mntpath
                do(mntpath)
            
        else:
            do("/mnt/%s_%s_jsboxdata"%(gridname,name))
            do("/mnt/%s_%s_jsbox"%(gridname,name))

    def createidentity(self):
        print "MAKE SURE YOU SELECT A GOOD PASSWD, select default destination!"
        do=j.system.process.executeWithoutPipe
        do("ssh-keygen -t dsa")
        keyloc="/root/.ssh/id_dsa.pub"
        if not j.system.fs.exists(path=keyloc):
            raise RuntimeError("cannot find path for key %s, was keygen well executed"%keyloc)
        key=j.system.fs.fileGetContents(keyloc).strip()
        c=""
        login=j.console.askString("official loginname (e.g. despiegk)")
        c+="id.name=%s\n"%j.console.askString("fullname")
        c+="id.email=%s\n"%j.console.askString("email")
        c+="id.mobile=%s\n"%j.console.askString("mobile")
        c+="id.skype=%s\n"%j.console.askString("skype")

        c+="id.key.dsa.pub=%s\n"%key

        idloc=self._getPath("identities/")
        if login=="":
            raise RuntimeError("login cannot be empty")
        userloc=j.system.fs.joinPaths(idloc,login)
        
        j.system.fs.createDir(userloc)
        hrdloc=j.system.fs.joinPaths(idloc,login,"id.hrd")
        j.system.fs.writeFile(filename=hrdloc,contents=c)
        for name in ["id_dsa","id_dsa.pub"]:
            u = j.system.fs.joinPaths(self._basepath, 'identities','system',name)
            j.system.fs.copyFile("/root/.ssh/%s"%name,u)

    def deployssh(self):
        node=self.getNode()
        node.connectSSH()
        keyloc="/root/.ssh/id_dsa.pub"
        
        if not j.system.fs.exists(path=keyloc):
            if j.console.askYesNo("do you want to generate new local ssh key, if you have one please put it there manually!"):
                do=j.system.process.executeWithoutPipe
                do("ssh-keygen -t dsa")
            else:
                j.application.stop()
        key=j.system.fs.fileGetContents(keyloc)
        node.cuapi.ssh_authorize("root",key)

    def _getHostNames(self,hostfilePath,exclude={}):
        """
        gets hostnames from /etc/hosts
        """
        result={}
        for line in j.system.fs.fileGetContents(hostfilePath).split("\n"):
            # print line
            line=line.strip()
            if line.find("########")==0:
                return result
            if line.strip()<>"" and line[0]<>"#":
                line2=line.replace("\t"," ")
                splits=line2.split(" ")
                name=splits[-1]
                ip=splits[0]
                if result.has_key(name):
                    continue
                if line.find("ip6-localhost")<>-1 or line.find("ip6-loopback")<>-1:
                    continue
                if line.find("ip6-localnet")<>-1 or line.find("ip6-mcastprefix")<>-1:
                    continue
                if line.find("ip6-allnodes")<>-1 or line.find("ip6-allrouters")<>-1:
                    continue                    
                if line.find("following lines are desirable")<>-1 or line.find("localhost")<>-1:
                    continue
                result[name]=ip
        return result

    def applyconfiglocal(self):
        #print "will do local changes e.g. for hostnames ",
        hostfilePath="/etc/hosts"
        out="""
# The following lines are desirable for IPv6 capable hosts
::1          ip6-localhost ip6-loopback
fe00::0      ip6-localnet
ff00::0      ip6-mcastprefix
ff02::1      ip6-allnodes
ff02::2      ip6-allrouters

127.0.0.1    localhost

"""        
        
        existingHostnames=self._getHostNames("/etc/hosts")

        def alias(name):
            name=name.lower()
            if self.gridNameAliases.has_key(name):
                return [item.lower() for item in self.gridNameAliases[name]]
            else:
                return []

        newHostnames={}
        for hkey in self.redis.hkeys("admin:nodes"):
            gridname,name=hkey.split(":")
            data=self.redis.hget("admin:nodes","%s:%s"%(gridname,name))
            node=JNode()
            try:
                node.__dict__=json.loads(data)
            except Exception,e:
                raise RuntimeError("could not decode node: '%s/%s'"%(gridname,name))
            n=node.name
            n=n.lower()
            g=node.gridname
            g=g.lower()
            newHostnames["%s.%s"%(n,g)]=node.ip
            for g2 in alias(node.gridname):
                if g2<>g:
                    newHostnames["%s.%s"%(n,g2)]=node.ip

        for hostname,ipaddr in existingHostnames.iteritems():
            if hostname.lower() not in newHostnames.keys():
                out+="%-18s %s\n"%(ipaddr,hostname)

        out+="\n#############################\n\n"

        hkeysNew=newHostnames.keys()
        hkeysNew.sort()

        for hostname in hkeysNew:
            ipaddr=newHostnames[hostname]
            if hostname.lower() in existingHostnames.keys():
                raise RuntimeError("error: found new hostname '%s' which already exists in existing hostsfile."%hostname)
            out+="%-18s %s\n"%(ipaddr,hostname)


        out+="\n"

        j.system.fs.writeFile(filename=hostfilePath,contents=out)


    def getHostNamesKeys(self,gridNameSearch=""):
        C=j.system.fs.fileGetContents("%s/admin/active.cfg"%j.dirs.cfgDir)

        keys=[]
        gridname=""
        for line in C.split("\n"):
            # print line
            line=line.strip()
            if line.find("####")==0:
                break
            if line=="" or line[0]=="#":
                continue
            if line.find("*")==0:
                gridname=line[1:].strip()
                continue
            if gridNameSearch=="" or gridname==gridNameSearch:
                name=line
                keys.append("%s__%s"%(gridname,name))
        return keys

    def getScriptRunInfo(self):
        res=[]
        for hkey in self.redis.hkeys("admin:scriptruns"):
            gridname,nodename,jscriptid=hkey.split(":")
            if jscriptid==str(self.runid):
                sr=ScriptRun()
                sr.__dict__=json.loads(self.redis.hget("admin:scriptruns",hkey))
                res.append(sr)
        return res

    def deleteScriptRunInfo(self):
        res=[]
        for hkey in self.redis.hkeys("admin:scriptruns"):
            gridname,nodename,runid=hkey.split(":")
            if runid==str(self.runid):
                self.redis.hdel("admin:scriptruns",hkey)

    def printResult(self):
        ok=[]
        nok=[]
        error=""
        result=""
        for sr in self.getScriptRunInfo():
            if sr.state=="OK":
                ok.append("%-10s %-15s"%(sr.gridname,sr.nodename))
                if sr.result<>"":
                    result+="#%-15s %-10s############################################################\n"%(sr.gridname,sr.nodename)
                    result+="%s\n\n"%sr.result
            else:
                nok.append("%-10s %-15s"%(sr.gridname,sr.nodename))
                for key,value in sr.__dict__.iteritems():
                    error+="%-15s: %s"%(key,value)
                error+="#######################################################################\n\n"


        j.system.fs.createDir("%s/admin"%j.dirs.varDir)

        if result<>"":
            print "######################## RESULT ##################################"
            print result
            j.system.fs.writeFile(filename="%s/admin/%s.result"%(j.dirs.varDir,sr.runid),contents=result)

        if error<>"":
            print "######################## ERROR ##################################"
            print error
            j.system.fs.writeFile(filename="%s/admin/%s.error"%(j.dirs.varDir,sr.runid),contents=error)

        if error<>"":
            exitcode = 1
        else:
            exitcode=0

        print "\n######################## OK #####################################"
        ok.sort()
        print "\n".join(ok)
        if len(nok)>0:
            print "######################## ERROR ###################################"
            nok.sort()
            print "\n".join(nok)

        return exitcode









