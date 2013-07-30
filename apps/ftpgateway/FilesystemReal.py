from FilesystemBase import FilesystemBase

from OpenWizzy import o
import os

class FilesystemReal(FilesystemBase):
    def __init__(self, root, cmd_channel,ftproot,readonly=False,name="",ttype="",contentmanager=None):
        """
         - (str) root: the real location on the filesystem which is the root of this fs
         - (str) ftproot: the root as how the ftp client should use it
         - name & ttype: identify the type of filesystem
         - (instance) cmd_channel: the FTPHandler class instance
        """
        FilesystemBase.__init__(self, root, cmd_channel)
        # Set initial current working directory.
        # By default initial cwd is set to "/" to emulate a chroot jail.
        # If a different behavior is desired (e.g. initial cwd = root,
        # to reflect the real filesystem) users overriding this class
        # are responsible to set cwd attribute as necessary.
        self.cmd_channel = cmd_channel
        self.handler=None
        self.cwd = ""
        self.ftproot=ftproot
        self.readonly=readonly
        self.ttype=ttype
        self.name=name
        self.contentmanager=contentmanager
        self.justDeleted="" 
        self.lastMaintenanceCheck=0

    def _ignorePath(self,item):
        #items=[]
        #for item in os.listdir(path):
        ext=o.system.fs.getFileExtension(item)
        if item.find(".quarantine")==0 or item.find(".tmb")==0:
            try:
                o.system.fs.remove(item)
            except:
                pass
            return True
        elif ext=="pyc":
            return True
        #else:
            #items.append(item)

    def listdir(self, path):
        """List the content of a directory."""            
        path1=self.ftp2fs(path)
        #import ipdb; ipdb.set_trace()
        #print "listdir:%s:%s" %(path,path1)
        items=[item for item in os.listdir(path1) if not self._ignorePath(item)]
        return items

    def fs2ftp(self, fspath):
        p=o.system.fs.pathRemoveDirPart(fspath,self.root)
        if len(p)<>0 and p[0]<>"/":
            p="/"+p
        p=self.ftproot+p
        #print "fs2ftp: %s -> %s" % (fspath,p)
        return p

    def openfile(self, path, mode):
        """Open a file returning its handler."""
        #@todo check on extension .redirect (file path:  $originalpath.$size.redirect) read from redirect where to go and repoint open
        if self.readonly and "w" in mode:
            raise RuntimeError("Cannot open file in write mode because filesystem %s is put in readonly."%self.root)
        else:
            path1=self.ftp2fs(path)
            return open(path1, mode)


    def mkstemp(self, suffix='', prefix='', dir=None, mode='wb'):
        """A wrap around tempfile.mkstemp creating a file with a unique
        name.  Unlike mkstemp it returns an object with a file-like
        interface.
        """
        class FileWrapper:
            def __init__(self, fd, name):
                self.file = fd
                self.name = name
            def __getattr__(self, attr):
                return getattr(self.file, attr)

        text = not 'b' in mode
        # max number of tries to find out a unique file name
        tempfile.TMP_MAX = 50
        fd, name = tempfile.mkstemp(suffix, prefix, dir, text=text)
        file = os.fdopen(fd, mode)
        return FileWrapper(file, name)


    # def maintenanceCheck(self):
    #     now=q.base.time.getTimeEpoch()
    #     if self.lastMaintenanceCheck < (now-5*60):
    #         self.lastMaintenanceCheck=now
    #         self.maintenance()

    # def maintenance(self):
    #     now=q.base.time.getTimeEpoch()
    #     out=""
    #     for line in self.justDeleted.split("\n"):
    #         epoch,path=line.split("_")
    #         if int(epoch)>now-60:
    #             out+=line+"\n"
    #     self.justDeleted=out


    def checkDirIsInJustDeleted(self,path):
        return path.find(self.justDeleted)==0
        # for line in self.justDeleted.split("\n"):
        #     epoch,path2=line.split("_")
        #     if path.find(path2)==0:
        #         return True
        # return False


    # --- Wrapper methods around os.* calls

    def chdir(self, ftppath):
        """Change the current directory."""
        path=self.ftp2fs(ftppath)
        if not o.system.fs.exists(path):
            #chech if in just deleted
            if self.checkDirIsInJustDeleted(path):
                self.cwd = self._removeFtproot(ftppath)
                return 
        print "chdir for fs %s_%s : %s"%(self.ttype,self.name,path)
        try:
            os.chdir(path)
        except OSError:
            raise
        else:
            self.cwd = self._removeFtproot(ftppath)

    def mkdir(self, path):
        """Create the specified directory."""
        path=self.ftp2fs(path)
        o.system.fs.createDir(path)
        ttype,id,path2=self.identify(path)        
        if id<>"":
            if ttype=="spaces":
                self.contentmanager.notifySpaceModification(self.name)
                o.apps.system.contentmanager.notifySpaceNewDir(id,None,path)

    def rmdir(self, path):
        """Remove the specified directory."""    
        path2=self.ftp2fs(path)
        # ttype,id,path2=self.identify(path)        
        # if id<>"":
        #     if ttype=="spaces":
        #         self.contentmanager.notifySpaceDelete(self.name)
        #     elif ttype=="buckets":
        #         self.contentmanager.notifyBucketDelete(self.name)
        #     elif ttype=="actors":
        #         self.contentmanager.notifyActorDelete(self.name)            
        if not o.system.fs.exists(path2):
            return
        o.system.fs.removeDirTree(path2)
        # self.justDeleted="%s_%s"%(q.base.time.getTimeEpoch(),path2)
        self.justDeleted=path2
        # os.rmdir(path)

    def remove(self, path):
        """Remove the specified file."""
        path=self.ftp2fs(path)
        os.remove(path)

    def rename(self, src, dst):
        """Rename the specified src file to the dst filename."""
        src=self.ftp2fs(src)
        dst=self.ftp2fs(dst)
        os.rename(src, dst)

    def chmod(self, path, mode):
        """Change file/directory mode."""
        #raise NotImplementedError
        path=self.ftp2fs(path)
        if not hasattr(os, 'chmod'):
            raise NotImplementedError
        os.chmod(path, mode)

    def stat(self, path):
        """Perform a stat() system call on the given path."""
        path2=self.ftp2fs(path)
        st=os.stat(path2)            
        return st

    lstat = stat

    # --- Wrapper methods around os.path.* calls

    def isfile(self, path):
        """Return True if path is a file."""
        path=self.ftp2fs(path)
        return os.path.isfile(path)

    def islink(self, path):
        """Return True if path is a symbolic link."""
        path=self.ftp2fs(path)
        return os.path.islink(path)

    def isdir(self, path):
        """Return True if path is a directory."""
        return True
        path=self.ftp2fs(path)            
        return os.path.isdir(path)

    def getsize(self, path):
        """Return the size of the specified file in bytes."""
        path=self.ftp2fs(path)
        return os.path.getsize(path)

    def getmtime(self, path):
        """Return the last modified time as a number of seconds since
        the epoch."""
        path=self.ftp2fs(path)
        return os.path.getmtime(path)

    #def realpath(self, path):
        #"""Return the canonical version of path eliminating any
        #symbolic links encountered in the path (if they are
        #supported by the operating system).
        #"""
        #return os.path.realpath(path)

    def lexists(self, path):
        """Return True if path refers to an existing path, including
        a broken or circular symbolic link.
        """
        path=self.ftp2fs(path)
        return os.path.lexists(path)

    def get_user_by_uid(self, uid):
        """Return the username associated with user id.
        If this can't be determined return raw uid instead.
        On Windows just return "owner".
        """
        return "owner"
        # if pwd is not None:
        #     try:
        #         return pwd.getpwuid(uid).pw_name
        #     except KeyError:
        #         return uid
        # else:
        #     return "owner"

    def get_group_by_gid(self, gid):
        """Return the groupname associated with group id.
        If this can't be determined return raw gid instead.
        On Windows just return "group".
        """
        return "group"
        # if grp is not None:
        #     try:
        #         return grp.getgrgid(gid).gr_name
        #     except KeyError:
        #         return gid
        # else:
        #     return "group"

    def readlink(self, path):
        """Return a string representing the path to which a
        symbolic link points.
        """
        from pylabs.Shell import ipshellDebug,ipshell
        print "DEBUG NOW readlink not implemented"
        ipshell()
        
        path=self.ftp2fs(path)
        return os.readlink(path)

    def identify(self,path):
        if path[0]<>"/":
            path=self.ftpnorm(path)
        path=self.ftp2fs(path)
        path=o.system.fs.getDirName(path)
        items=o.system.fs.pathNormalize(path).split(os.sep)
        type=""
        id=0
        key=""

        while len(items)>0:
            curpath=os.sep.join(items)
            id=o.system.fs.getParentDirName(curpath+"/")
            if o.system.fs.exists(o.system.fs.joinPaths(curpath,".space")):
                #found space
                type="spaces"
                break
            elif o.system.fs.exists(o.system.fs.joinPaths(curpath,".bucket")):
                #found space
                type="buckets"
                break
            elif o.system.fs.exists(o.system.fs.joinPaths(curpath,".actor")):
                #found space
                type="actors"
                break
            items.pop()
        #items.pop()
        path=os.sep.join(items)
        return type,id,path


    def on_file_received(self, path):        
        if self.ttype=="spaces":
            self.contentmanager.notifySpaceModification(self.name)
            print "notify %s modification" % self.ttype
        elif self.ttype=="buckets":
            self.contentmanager.notifyBucketModification(self.name)
            print "notify %s modification" % self.ttype
        elif self.ttype=="actors":
            self.contentmanager.notifyActorModification(self.name)
            print "notify %s modification" % self.ttype

    def on_file_sent(self,path):
        pass

    def on_mkdir(self,path):
        pass

    
