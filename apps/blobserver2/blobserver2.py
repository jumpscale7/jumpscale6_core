
from JumpScale import j
import gevent

import JumpScale.grid.zdaemon

j.application.start("jumpscale:blobserver2")
j.application.initGrid()

import JumpScale.grid.zdaemon

j.logger.consoleloglevel = 2

import inspect
import ujson

class BlobserverCMDS():

    def __init__(self, daemon):

        j.application.initGrid()

        self.daemon = daemon
        self.adminpasswd = j.application.config.get('grid.master.superadminpasswd')
        self.adminuser = "root"

        self.STORpath="/opt/STOR"  #harccoded for now needs to come from HRD

        # j.logger.setLogTargetLogForwarder()

    def set(self,key,value,repoId="",session=None):
        if key<>"" and self.exists(key):
            return key
        key=j.tools.hash.md5_string(value)
        backuppath=j.system.fs.joinPaths(self.STORpath,key[0:2],key[2:4],key)
        j.system.fs.createDir(j.system.fs.getDirName(backuppath))
        j.system.fs.writeFile(backuppath,value)
        mdpath=backuppath+".md"
        if not j.system.fs.exists(path=mdpath):
            md={}
        else:
            md=ujson.loads(j.system.fs.fileGetContents(mdpath))
        if not md.has_key("repos"):
            md["repos"]={}
        md["repos"][str(repoId)]=True
        mddata=ujson.dumps(md)        
        j.system.fs.writeFile(backuppath+".md",mddata)
        return [key,True,True]

    def get(self,key,session=None):
        backuppath=j.system.fs.joinPaths(self.STORpath,key[0:2],key[2:4],key)
        with open(backuppath) as fp:
            data2 = fp.read()
            fp.close()
        return data2

    def getMD(self,key,session=None):
        backuppath=j.system.fs.joinPaths(self.STORpath,key[0:2],key[2:4],key)
        with open(backuppath) as fp:
            data2 = fp.read()
            fp.close()
        return data2        

    def delete(self,key,repoId="",session=None):
        from IPython import embed
        print "DEBUG NOW ppp"
        embed()
        
        if key<>"" and not self.exists(key):
            return 
        backuppath=j.system.fs.joinPaths(self.STORpath,key[0:2],key[2:4],key)
        mdpath=backuppath+".md"
        if not j.system.fs.exists(path=mdpath):       
            raise RuntimeError("did not find metadata")
        md=ujson.loads(j.system.fs.fileGetContents(mdpath))
        if not md.has_key("repos"):
            raise RuntimeError("error in metadata on path:%s, needs to have repos as key."%mdpath)
        if md["repos"].has_key(str(repoId)):
            md["repos"].pop(str(repoId))
        if md["repos"]=={}:
            j.system.fs.remove(backuppath)
            j.system.fs.remove(mdpath)
        else:
            mddata=ujson.dumps(md)        
            j.system.fs.writeFile(backuppath+".md",mddata)

    def exists(self,key,session=None):
        backuppath=j.system.fs.joinPaths(self.STORpath,key[0:2],key[2:4],key)
        return j.system.fs.exists(path=backuppath)

    def _adminAuth(self,user,passwd):
        if user != self.adminuser or passwd != self.adminpasswd:
            raise RuntimeError("permission denied")


daemon = j.servers.zdaemon.getZDaemon(port=2345)

daemon.setCMDsInterface(BlobserverCMDS, category="blobserver")  # pass as class not as object !!! chose category if only 1 then can leave ""

cmds=daemon.daemon.cmdsInterfaces["blobserver"][0]
# cmds.loadJumpscripts()

daemon.start()

j.application.stop()

