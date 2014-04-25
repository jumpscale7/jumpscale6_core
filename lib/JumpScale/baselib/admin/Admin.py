from JumpScale import j
import JumpScale.baselib.remote
import sys
# import importlib
import imp
import ujson
import JumpScale.baselib.credis
import copy
import time

from fabric.api import hide

class JNode():
    def __init__(self):
        self.actionsDone={}
        self.lastcheck=0
        self.name=""
        self.cuapi=None
        self.args=None
        self.passwd=None
        self.error=""
        self.result=""
        self.basepath=j.dirs.replaceTxtDirVars(j.application.config.get("admin.basepath"))

    def executeCmds(self,cmds,die=True):
        out=""
        for line in cmds.split("\n"):
            if line.strip()<>"" and line[0]<>"#":
                if die:
                    out+="%s\n"%self.cuapi.run(line)
                else:
                    try:
                        print line
                        out+="%s\n"%self.cuapi.run(line)
                    except:
                        pass
        self.result+=out
        return out

    def killProcess(self,filterstr):
        found=self.getPids(filterstr)
        for item in found:
            self.cuapi.run("kill -9 %s"%item)

    def getPids(self,filterstr):
        with hide('output'):
            out=self.cuapi.run("ps ax")
        found=[]
        for line in out.split("\n"):
            if line.strip()<>"":
                if line.find(filterstr)<>-1:
                    line=line.strip()
                    found.append(int(line.split(" ")[0]))   

        return found

    def jpackageStop(self,name,filterstr):
        self.cuapi.run("source /opt/jsbox/activate;jpackage stop -n %s"%name)
        found=self.getPids(filterstr)
        if len(found)>0:
            for item in found:
                self.cuapi.run("kill -9 %s"%item)            

    def jpackageStart(self,name,filterstr,nrtimes=1,retry=1):
        found=self.getPids(filterstr)
        for i in range(retry):
            if len(found)==nrtimes:
                return
            self.cuapi.run("source /opt/jsbox/activate;jpackage start -n %s"%name)                
            time.sleep(1)
            found=self.getPids(filterstr)
        if len(found)<nrtimes:
            self.raiseError("jpackageStart","could not jpackageStart %s"%name)

    def serviceStop(self,name,filterstr):
        try:
            self.cuapi.run("sudo stop %s"%name)
        except:
            pass
        found=self.getPids(filterstr)
        if len(found)>0:
            for item in found:
                self.cuapi.run("kill -9 %s"%item)            
        found=self.getPids(filterstr)
        if len(found)>0:
            self.raiseError("service stop","could not serviceStop %s"%name)

    def serviceStart(self,name,filterstr):
        found=self.getPids(filterstr)
        if len(found)==0:
            self.cuapi.run("sudo start %s"%name)
        found=self.getPids(filterstr)
        if len(found)==0:
            self.raiseError("service start","could not serviceStart %s"%name)            

    def serviceReStart(self,name,filterstr):
        self.serviceStop(name,filterstr)
        self.serviceStart(name,filterstr)


    def raiseError(self,action,msg):
        out=""
        for line in msg.split("\n"):
            out+="%-5s:%s: **ERROR** %s\n" % (self.name,action,line)        
        j.admin.raiseError(self.name,action,msg)
        j.admin.log(out)
        self.lastcheck=0
        j.admin.setNode(self)

    def log(self,msg):
        # print msg
        out=""
        for line in msg.split("\n"):
            out+="%-5s: %s\n" % (self.name,line)
        j.admin.log(out)

    def setpasswd(self,passwd):
        #this will make sure new password is set
        self.log("set passwd")
        cl=j.tools.expect.new("sh")
        if self.args.seedpasswd=="":
            self.args.seedpasswd=self.findpasswd()
        try:
            cl.login(remote=self.name,passwd=passwd,seedpasswd=None)
        except Exception,e:
            self.raiseError("setpasswd","Could not set root passwd.")

    def findpasswd(self):
        self.log("find passwd for superadmin")
        cl=j.tools.expect.new("sh")
        for passwd in j.admin.rootpasswds:
            # cl.login(remote=self.args.remote,passwd=passwd,seedpasswd=None)
            try:            
                pass
                cl.login(remote=self.name,passwd=passwd,seedpasswd=None)
            except Exception,e:
                self.raiseError("findpasswd","could not login using:%s"%passwd)
                continue
            self.passwd=passwd
            j.admin.setNode(self)
        return "unknown"

    def check(self):
        j.base.time.getTimeEpoch()

    def _connectCuapi(self):
        self.cuapi.connect(self.name)

        if self.args.passwd<>"":
            # setpasswd()
            j.remote.cuisine.fabric.env["password"]=self.args.passwd
        elif self.passwd<>None and self.passwd<>"unknown":
            # setpasswd()
            j.remote.cuisine.fabric.env["password"]=self.passwd
        # else:
        #     self.findpasswd()

        return self.cuapi

    def uploadFromCfgDir(self,ttype,dest):
        cfgdir=j.system.fs.joinPaths(self.basepath, "cfgs/%s/%s"%(j.admin.args.cfgname,ttype))
        cuapi=self.cuapi
        if j.system.fs.exists(path=cfgdir):
            self.log("upload from %s to %s"%(ttype,dest))
            items=j.system.fs.listFilesInDir(cfgdir,True)
            done=[]
            for item in items:
                partpath=j.system.fs.pathRemoveDirPart(item,cfgdir)
                partpathdir=j.system.fs.getDirName(partpath).rstrip("/")
                if partpathdir not in done:
                    cuapi.dir_ensure("%s/%s"%(dest,partpathdir), True)
                    done.append(partpathdir)
                try:            
                    cuapi.file_upload("%s/%s"%(dest,partpath),item)#,True,True)  
                except Exception,e:
                    self.raiseError("uploadFromCfgDir","could not upload file %s to %s"%(ttype,dest))


    def execute(self,jsname,once=True,**kwargs):
        self.log("execute:%s on %s "%(jsname,self.name))
        jsname=jsname.lower()
        now= j.base.time.getTimeEpoch()
        do=True
        if once:
            if self.actionsDone.has_key(jsname):
                timeexec=self.actionsDone[jsname]
                if timeexec<(now-(3600*10)): #10h ago
                    do=True
                else:
                    do=False
        if self.args.force:
            do=True
        if do:
            self.log("ping test")
            if j.system.net.pingMachine(self.name,1)==False:
               self.raiseError(jsname,"COULD NOT connect (ping)")
               return
            print "* tcp check ssh"
            if not j.admin.js.has_key(jsname):
                raise RuntimeError("cannot find js:%s"%jsname)
            if not j.system.net.tcpPortConnectionTest(self.name,22):
                self.raiseError(jsname,"COULD NOT port check (ssh)")
                return
            self.log("sshapi start cmd:%s"%jsname)
            cuapi=self.cuapi
            try:                
                self.result=j.admin.js[jsname](node=self,**kwargs)
                self.actionsDone[jsname]=now
                self.lastcheck=now
            except BaseException,e:
                if self.actionsDone.has_key(jsname):
                    self.actionsDone.pop(jsname)                
                msg="COULD NOT EXECUTE %s .\nError %s"%(self.name,e)
                # j.errorconditionhandler.processPythonExceptionObject(e)
                self.raiseError(jsname,msg)
                self.error=str(e)

            j.admin.setNode(self)
        else:
            self.log("No need to execute %s on %s"%(jsname,self.name))
            return False

class AdminFactory:
    def get(self,args,failWhenNotExist=False):
        return Admin(args,failWhenNotExist)

class Admin():
    def __init__(self,args,failWhenNotExist=False):
        self.args=args
        self.basepath=j.dirs.replaceTxtDirVars(j.application.config.get("admin.basepath"))
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
                nodes = self._getActiveNodes()
                hosts = [node['name'] for node in nodes]
                for node in nodes:
                    for role in roles:
                        if role not in node['roles']:
                            hosts.remove(node['name'])
                            break
                self.hosts = hosts
                self.hosts.sort()
            elif args.remote=="":
                self.hosts=self.getHostNames().keys()
                self.hosts.sort()
            else:
                self.hosts=args.remote.split(",")
            # if hosts<>[]:
            #     if failWhenNotExist==False:
            #         for host in hosts:
            #             #check 
            #             if j.system.net.tcpPortConnectionTest("m3pub",22):
            #                 self.cuapi.fabric.api.env["hosts"].append(host)
            #                 self.hosts.append(host)
            #     else:
            #         self.hosts=hosts
            #         self.cuapi.fabric.api.env["hosts"]=hosts
            # else:            
            #     self.cuapi.connect(args.remote)
        self.sysadminPasswd=""
        self.applyconfiglocal() #set hosts
        self.js={}
        self.loadJumpscripts()
        
        self.redis = j.clients.redis.getRedisClient("127.0.0.1", 7768)
        self.nodes={}
        self.errors=[]
        self._log=""
        self.hrd= j.core.hrd.getHRD(self._getPath("cfg/","superadmin.hrd"))
        self.rootpasswds=self.hrd.getList("superadmin.passwds")

    def _getActiveNodes(self):
        import JumpScale.grid.osis
        oscl = j.core.osis.getClient(user='root')
        ncl = j.core.osis.getClientForCategory(oscl, 'system', 'node')
        return ncl.simpleSearch({'active': True})

    def log(self,msg):
        msg=msg.strip("\n")+"\n"
        print msg
        self._log+="%s"%msg

    def raiseError(self,name,action,msg):
        self.errors.append([name,action,msg])

    def _getPath(self,sub,file=""):        
        path= "%s/%s"%(self.basepath,sub)
        path=path.replace("\\","/")
        path=path.replace("//","/")
        if path[-1]<>"/":
            path+="/"
        if file<>"":
            path+=file
        return path

    # def pushDir(self)

    def getNode(self,name,reset=False):
        name=name.lower()
        if reset or self.redis.exists("admin:nodes:%s"%name)==0:
            node=JNode()
            self.setNode(node)
            node.name=name
        else:
            data=self.redis.get("admin:nodes:%s"%name)
            node=JNode()
            try:
                node.__dict__=ujson.loads(data)
            except Exception,e:
                node=JNode()
                self.setNode(node)
            node.name=name
        node.cuapi=self.cuapi
        node.args=self.args
        node.result=""
        node.error=""
        node._connectCuapi()
        
        return node

    def upload(self,name,ttype,dest):
        cfgdir="%s/cfgs/%s/%s"%(self.basepath,self.args.cfgname,ttype)
        if j.system.fs.exists(path=cfgdir):
            print "upload %s to %s"%(cfgdir,dest)
            items=j.system.fs.listFilesInDir(cfgdir,True)
            done=[]
            for item in items:
                partpath=j.system.fs.pathRemoveDirPart(item,cfgdir)
                partpathdir=j.system.fs.getDirName(partpath).rstrip("/")
                if partpathdir not in done:
                    print cuapi.dir_ensure("%s/%s"%(dest,partpathdir), True)
                    done.append(partpathdir)            
                cuapi.file_upload("%s/%s"%(dest,partpath),item)#,True,True)    

    def setNode(self,node):
        node2=copy.copy(node.__dict__)
        node2.pop("cuapi")
        node2.pop("args")
        self.redis.set("admin:nodes:%s"%node.name,ujson.dumps(node2))

    def execute(self,jsname,once=True,reset=False,**kwargs):
        res=[]
        for host in self.hosts:
            node=self.getNode(host,reset)
            r=node.execute(jsname,once,**kwargs)
            if r<>False:
                res.append(node)
            else:
                # print "NO need to execute"
                pass
        if len(res)==1:
            res=res[0]
        elif len(res)==0:
            res=None
        return res

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
        # print "OK"

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

        basepath=j.dirs.replaceTxtDirVars(j.application.config.get("admin.basepath"))
        c+="id.key.dsa.pub=%s\n"%key

        idloc=self._getPath("identities/")
        if login=="":
            raise RuntimeError("login cannot be empty")
        userloc=j.system.fs.joinPaths(idloc,login)
        
        j.system.fs.createDir(userloc)
        hrdloc=j.system.fs.joinPaths(idloc,login,"id.hrd")
        j.system.fs.writeFile(filename=hrdloc,contents=c)
        for name in ["id_dsa","id_dsa.pub"]:
            u = j.system.fs.joinPaths(basepath, 'identities','system',name)
            j.system.fs.copyFile("/root/.ssh/%s"%name,u)

    def _getHostNames(self,hostfilePath,exclude={}):
        result={}
        for line in j.system.fs.fileGetContents(hostfilePath).split("\n"):
            # print line
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
        
        result=self.getHostNames(all=True)
        result2=self._getHostNames("/etc/hosts",exclude=result)       

        keys=result2.keys()
        keys.sort()
        for name in keys:
            ip=result2[name]
            out+="%-18s  %s\n"%(ip,name)
        
        out+="\n"

        keys=result.keys()
        keys.sort()
        for name in keys:
            ip=result[name]
            if not result2.has_key(name):
                out+="%-18s  %s\n"%(ip,name)
        
        j.system.fs.writeFile(filename=hostfilePath,contents=out)

    def getHostNames(self,all=False):
        state="start"
        result={}
        if all:
            state="found"
        for line in j.system.fs.fileGetContents(self._getPath("cfg/","hosts")).split("\n"):
            line=line.strip()
            if line=="":
                continue
            if line.find("ip6-localhost")<>-1 or line.find("ip6-loopback")<>-1:
                continue
            if line.find("ip6-localnet")<>-1 or line.find("ip6-mcastprefix")<>-1:
                continue
            if line.find("ip6-allnodes")<>-1 or line.find("ip6-allrouters")<>-1:
                continue                    
            if line.find("following lines are desirable")<>-1 or line.find("localhost")<>-1:
                continue                
            if state=="FOUND":
                if line[0]<>"#":
                    line=line.replace("\t"," ")
                    splits=line.split(" ")
                    name=splits[-1]
                    ip=splits[0]
                    result[name]=ip
            if line.find("#ACTIVE")<>-1:
                state="FOUND"
            if line.find("#ENDACTIVE")<>-1 and all==False:
                state="end"
                break
        return result


    # def getCluster(self,sysadminPasswd=""):
    #     if sysadminPasswd=="":
    #         sysadminPasswd=self.sysadminPasswd
    #     hosts=self.getHostNames().keys()
    #     cl=j.remote.cluster.create("mycluster","mycluster",hosts,sysadminPasswd)

