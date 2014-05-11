from JumpScale import j
import sys
import time
import imp
import linecache
import inspect
import JumpScale.baselib.webdis
import JumpScale.baselib.redis

class Dummy():
    pass


class JumpScript(object):
    def __init__(self, ddict=None, path=None):
        self.name=""
        self.organization=""
        self.period = 0
        self.lastrun = 0
        self.source=""
        self.path=path
        self.id = None
        self.startatboot = False
        if ddict:
            self.__dict__.update(ddict)
        if not path:
            self.write()
            self.load()
        else:
            self.path = path
            self.load()
            self.loadAttributes()

    def write(self):
        # jscriptdir = j.system.fs.joinPaths(j.dirs.varDir,"jumpscripts", self.organization)
        # j.system.fs.createDir(jscriptdir)
        # self.path=j.system.fs.joinPaths(jscriptdir, "%s.py" % self.name)
        if self.path==None:
            raise RuntimeError("path cannot be empty")

        content="""
from JumpScale import j

"""
        content += self.source
        j.system.fs.writeFile(filename=self.path, contents=content)

    def load(self):
        md5sum = j.tools.hash.md5_string(self.path)
        modulename = 'JumpScale.jumpscript_%s' % md5sum
        linecache.checkcache(self.path)
        self.module = imp.load_source(modulename, self.path)


    def getDict(self):
        result = dict()
        for attrib in ('name', 'author', 'organization', 'category', 'license', 'version', 'roles', 'source', 'path', 'descr', 'queue', 'async', 'period', 'order', 'log', 'enable', 'startatboot', 'gid', 'id'):
            result[attrib] = getattr(self, attrib)
        return result

    def loadAttributes(self):
        name = getattr(self.module, 'name', "")
        if name=="":
            name=j.system.fs.getBaseName(self.path)
            name=name.replace(".py","").lower()

        source = inspect.getsource(self.module)
        self.name=name
        self.author=getattr(self.module, 'author', "unknown")
        self.organization=getattr(self.module, 'organization', "unknown")
        self.category=getattr(self.module, 'category', "unknown")
        self.license=getattr(self.module, 'license', "unknown")
        self.version=getattr(self.module, 'version', "1.0")
        self.roles=getattr(self.module, 'roles', [])
        self.source=source
        self.descr=self.module.descr
        self.queue=getattr(self.module, 'queue',"default")
        self.async = getattr(self.module, 'async',False)
        self.period=getattr(self.module, 'period',0)
        self.order=getattr(self.module, 'order', 1)
        self.log=getattr(self.module, 'log', True)
        self.enable=getattr(self.module, 'enable', True)
        self.startatboot=getattr(self.module, 'startatboot', False)
        self.gid=getattr(self.module, 'gid', j.application.whoAmI.gid)

    def run(self, *args, **kwargs):
        return self.module.action(*args, **kwargs)

    def execute(self, *args, **kwargs):
        result = None, None
        if not self.enable:
            return
        if not self.async:
            try:
                result = True, self.run(*args, **kwargs)
            except Exception,e:
                eco=j.errorconditionhandler.parsePythonErrorObject(e)
                eco.errormessage='Exec error procmgr jumpscr:%s_%s on node:%s_%s %s'%(self.organization,self.name, \
                        j.application.whoAmI.gid, j.application.whoAmI.nid,eco.errormessage)
                eco.tags="jscategory:%s"%self.category
                eco.tags+=" jsorganization:%s"%self.organization
                eco.tags+=" jsname:%s"%self.name
                j.errorconditionhandler.raiseOperationalCritical(eco=eco,die=False)
                eco.tb = None
                eco.type = str(eco.type)
                result = False, eco.__dict__
        else:
            # self.q_d.enqueue('%s_%s.action'%(action.organization,action.name))
            #NO LONGER USE redisq, now use our own queuing mechanism
            queue = getattr(self, 'queue', 'default')
            j.clients.redisworker.execJumpscript(self.id,_timeout=60,_queue=queue,_log=self.log,_sync=False)

        self.lastrun = time.time()
        print "ok:%s"%self.name
        return result


class JumpscriptFactory:

    """
    """
    def __init__(self):
        self.basedir = j.system.fs.joinPaths(j.dirs.baseDir, 'apps', 'processmanager')
        redis = j.clients.credis.getRedisClient("127.0.0.1", 7768)
        
        if j.application.config.exists("grid_watchdog_secret")==False or j.application.config.get("grid_watchdog_secret")=="":
            raise RuntimeError("please configure grid.watchdog.secret")
        self.secret=j.application.config.get("grid_watchdog_secret")

    def getJSClass(self):
        return JumpScript


    def pushToGridMaster(self): 
        webdis=j.clients.webdis.get(j.application.config.get("grid_master_ip"),7779)
        #create tar.gz of cmds & monitoring objects & return as binary info
        #@todo make async with local workers
        import tarfile
        ppath=j.system.fs.joinPaths(j.dirs.tmpDir,"processMgrScripts_upload.tar")
        with tarfile.open(ppath, "w:bz2") as tar:
            for path in j.system.fs.listFilesInDir("%s/apps/agentcontroller/processmanager"%j.dirs.baseDir,True):
                if j.system.fs.getFileExtension(path)<>"pyc":
                    arcpath="processmanager/%s"%path.split("/processmanager/")[1]
                    tar.add(path,arcpath)
            for path in j.system.fs.listFilesInDir("%s/apps/agentcontroller/jumpscripts"%j.dirs.baseDir,True):
                if j.system.fs.getFileExtension(path)<>"pyc":
                    arcpath="jumpscripts/%s"%path[len(j.system.fs.getParent(j.system.fs.getDirName(path)))+1:]
                    from IPython import embed
                    print "DEBUG NOW yuyuy"
                    embed()
                    
                    tar.add(path,arcpath)
        data=j.system.fs.fileGetContents(ppath)       
        webdis.set("%s:scripts"%(self.secret),data)  
        # scripttgz=webdis.get("%s:scripts"%(self.secret))      
        # assert data==scripttgz

    def loadFromGridMaster(self):
        print "load processmanager code from master"
        webdis=j.clients.webdis.get(j.application.config.get("grid_master_ip"),7779)

        #delete previous scripts
        item=["eventhandling","loghandling","monitoringobjects","processmanagercmds","jumpscripts"]
        for delitem in item:
            j.system.fs.removeDirTree( j.system.fs.joinPaths(self.basedir, delitem))        

        #import new code
        #download all monitoring & cmd scripts


        import tarfile
        scripttgz=webdis.get("%s:scripts"%(self.secret))
        ppath=j.system.fs.joinPaths(j.dirs.tmpDir,"processMgrScripts_download.tar")
        
        j.system.fs.writeFile(ppath,scripttgz)
        tar = tarfile.open(ppath, "r:bz2")

        for tarinfo in tar:
            if tarinfo.isfile():
                print tarinfo.name
                if tarinfo.name.find("processmanager/")==0:
                    # dest=tarinfo.name.replace("processmanager/","")           
                    tar.extract(tarinfo.name, j.system.fs.getParent(self.basedir))
                if tarinfo.name.find("jumpscripts/")==0:
                    # dest=tarinfo.name.replace("processmanager/","")           
                    tar.extract(tarinfo.name, self.basedir)

        j.system.fs.remove(ppath)
