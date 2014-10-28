from JumpScale import j
import toml

class RsyncInstance:

    def __init__(self):
        self.name
        self.secret
        self.users=[]
        self.readonly=True
        self.exclude="*.pyc .git"


class RsyncServer:
    """
    """

    def __init__(self,root,port=873):
        self.root=root
        self.port=port
        self.pathsecrets="%s/secrets.cfg"%self.root
        self.pathusers="%s/users.cfg"%self.root
        self.distrdir="/opt/jumpscale/apps/agentcontroller/distrdir/"
        j.system.fs.createDir("/etc/rsync")

        if j.system.fs.exists(path=self.pathsecrets):
            self.secrets=toml.loads(j.system.fs.fileGetContents(self.pathsecrets))
        else:
            self.secrets={}

        if j.system.fs.exists(path=self.pathusers):
            self.users=toml.loads(j.system.fs.fileGetContents(self.pathusers))
        else:
            self.users={}

    def addUserAccessUpload(self,user,passwd):
        self.users.append([user,passwd])

    def addSecret(self,name,secret=""):
        if self.secrets.has_key(name) and secret=="":            
            #generate secret
            secret=self.secrets[name]
        if secret=="":
            secret=j.base.idgenerator.generateGUID().replace("-","")

        self.secrets[name.strip()]=secret.strip()
        j.system.fs.writeFile(self.pathsecrets,toml.dumps(self.secrets))
            
    def addUser(self,name,passwd):
        self.users[name.strip()]=passwd.strip()
        j.system.fs.writeFile(self.pathusers,toml.dumps(self.users))   

    def saveConfig(self):

        C="""
#motd file = /etc/rsync/rsyncd.motd
port = $port
log file=/var/log/rsync
max verbosity = 1

[upload]
exclude = *.pyc .git
path = $root/root
comment = upload
uid = root
gid = root
read only = false
auth users = $users
secrets file = /etc/rsync/users

"""
        D="""
[$secret]
exclude = *.pyc .git
path = $root/root/$name
comment = readonlypart
uid = root
gid = root
read only = true
list = no

"""
        users=""
        for name,secret in self.users.iteritems():
            users+="%s,"%name
        users.rstrip(",")

        for name,secret in self.secrets.iteritems():
            path="%s/root/%s"%(self.root,name)            
            j.system.fs.createDir(path)
            D2=D.replace("$secret",secret)
            D2=D2.replace("$name",name)
            C+=D2

        C=C.replace("$root",self.root)
        C=C.replace("$users",users)
        C=C.replace("$port",str(self.port))
            
        j.system.fs.writeFile(filename="/etc/rsync/rsyncd.conf",contents=C)

        path="/etc/rsync/users"
        out=""
        for name,secret in self.users.iteritems():
            out+="%s:%s\n"%(name,secret)

        j.system.fs.writeFile(filename=path,contents=out)

        j.system.fs.chmod(path, permissions=0o600)

        ##with bindmounts
        # cmd="mount | grep /tmp/server"
        
        # rc,out=j.system.process.execute(cmd,dieOnNonZeroExitCode=False)
        # if rc==0:
        #     for line in out.split("\n"):
        #         if line=="":
        #             continue
        #         cmd="umount %s"%line.split(" ",1)[0]
        #         # print cmd
        #         j.system.process.execute(cmd)


        # for name,passwd in self.secrets.iteritems():
        #     src="%s/download/%s"%(self.root,passwd)            
        #     dest="%s/upload/%s"%(self.root,name)
        #     j.system.fs.createDir(src)
        #     j.system.fs.createDir(dest)
        #     # j.system.fs.symlink(dest, src, overwriteTarget=True)


        #     cmd="mount --bind %s %s"%(src,dest)
        #     j.system.process.execute(cmd)


            

    def start(self,background=True):
        self.saveConfig()
        self.prepare()
        
        j.system.process.killProcessByPort(self.port)

        if background:
            cmd="rsync --daemon --config=/etc/rsync/rsyncd.conf"
        else:
            cmd="rsync -v --daemon --no-detach --config=/etc/rsync/rsyncd.conf"
        # print cmd

        j.system.process.executeWithoutPipe(cmd)
     
    def prepare(self):

        pathRegexExcludes = {}
        childrenRegexExcludes=[".*/log/.*","/dev/.*","/proc/.*"]

        def processdir(path,stat,arg):
            print "%s"%path
            from IPython import embed
            print "DEBUG NOW id"
            embed()
            

        callbackFunctions={}
        callbackFunctions["D"]=processdir

        fswalker = j.base.fswalker.get()

        callbackMatchFunctions=fswalker.getCallBackMatchFunctions({},pathRegexExcludes,False,False)
        args={}

        fswalker.walk(self.distrdir,callbackFunctions,args,
                          callbackMatchFunctions,childrenRegexExcludes, 
                          [],pathRegexExcludes)

        from IPython import embed
        print "DEBUG NOW kkk"
        embed()
        



class RsyncClient:
    """
    """

    def __init__(self,name="",addr="localhost",port=873,login="",passwd=""):
        self.addr=addr
        self.port=port
        self.login=login
        self.passwd=passwd
        self.name=name
        self.options="-r --delete-after --modify-window=60 --compress --stats  --progress"
        if self.login=="":
            j.events.inputerror_critical("login needs to be specified",category="rsync.sync.fromserver")
        if self.passwd=="":
            j.events.inputerror_critical("passwd needs to be specified",category="rsync.sync.fromserver")
        if self.name=="":
            j.events.inputerror_critical("name needs to be specified",category="rsync.sync.fromserver")

    def _pad(self,dest):
        if len(dest)<>0 and dest[-1]<>"/":
            dest+="/"
        return dest

    def syncFromServer(self,src,dest):
        src=self._pad(src)
        dest=self._pad(dest)
        j.system.fs.createDir(dest)
        cmd="export RSYNC_PASSWORD=%s;rsync -av %s@%s::upload/%s/%s %s %s"%(self.passwd,self.login,self.addr,self.name,src,dest,self.options)
        print cmd
        j.system.process.executeWithoutPipe(cmd)        

    def syncToServer(self,src,dest):
        src=self._pad(src)
        dest=self._pad(dest)
        cmd="export RSYNC_PASSWORD=%s;rsync -av %s %s@%s::upload/%s/%s %s"%(self.passwd,src,self.login,self.addr,self.name,dest,self.options)
        print cmd
        j.system.process.executeWithoutPipe(cmd)        

    def connect(self,addr,port):
        self.addr=addr
        self.port=port

class RsyncClientSecret(RsyncClient):
    """
    """

    def __init__(self,addr="localhost",port=873,secret=""):
        self.addr=addr
        self.port=port
        self.secret=secret
        self.options="-r --delete-after --modify-window=60 --compress --stats --progress"        
        if self.secret=="":
            j.events.inputerror_critical("secret needs to be specified",category="rsync.sync.fromserver")

    def sync(self,src,dest):
        """
        can only sync from server to client
        """
        src=self._pad(src)
        dest=self._pad(dest)        
        cmd="rsync %s::%s/%s %s %s"%(self.addr,self.secret,src,dest,self.options)
        print cmd
        j.system.process.executeWithoutPipe(cmd)        
