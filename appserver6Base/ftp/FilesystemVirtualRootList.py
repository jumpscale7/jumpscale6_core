
from FilesystemBase import FilesystemBase

from pylabs import q
import os

class FilesystemVirtualRootList(FilesystemBase):
    """
    basis for 1 level down eg spaces
    """

    def __init__(self, cmd_channel,name2pathFunction,type,contentmanager):
        root=type
        FilesystemBase.__init__(self, root, cmd_channel)
        self.cwd = "/"
        self.list=[]
        self.name2pathFunction=name2pathFunction
        self.name2path={}
        self.type=type
        self.ftproot="/%s"%type
        self.contentmanager=contentmanager

    def listdir(self, path):
        print "list for rootfilesystemlist: %s" % self.cwd
        self.name2path=self.name2pathFunction()
        self.list=self.name2path.keys()
        return self.list

    def chdir(self, ftppath):
        print "chdirrootfslist:%s" % ftppath
        self.cwd=self._removeFtproot(ftppath)

    def mkdir(self, path):
        parent=q.system.fs.getDirName(path+"/",True)
        rpath=""      
        if self.type=="spaces":
            self.contentmanager.notifySpaceNew(path=rpath,name=parent)
        elif self.type=="buckets":
            self.contentmanager.notifyBucketNew(path=rpath,name=parent)
        elif self.type=="actors":
            if parent.find("__")==-1:
                msg="Cannot create actor with name which is not constructed as $appname__$actorname, here %s"%parent
                q.errorconditionhandler.raiseOperationalWarning("","ftpserver.fs",msg)
            self.contentmanager.notifyActorNew(path=rpath,name=parent)
        return

    def rmdir(self, path):
        parent=q.system.fs.getDirName(path+"/",True)
        rpath=self.name2path[parent]        
        if self.type=="spaces":
            q.system.fs.removeDirTree(rpath)
            self.contentmanager.notifySpaceDelete(path)
            print "NOTIFY DELETE SPACE %s"%rpath
        elif self.type=="buckets":
            q.system.fs.removeDirTree(rpath)
            self.contentmanager.notifyBucketDelete(path)            
            print "NOTIFY DELETE BUCKET %s"%rpath
        elif self.type=="actors":
            q.system.fs.removeDirTree(rpath)
            self.contentmanager.notifyActorDelete(path)
            print "NOTIFY DELETE ACTOR %s"%rpath

    def fs2ftp(self, path):
        raise RuntimeError("not implemented")

    def ftp2fs(self, ftppath):
        return self.joinPaths(self.ftppath,ftppath)

    def remove(self, path):
        return
    def rename(self, src, dst):
        return

    def chmod(self, path, mode):
        return

    def stat(self, path):
        return

    def lstat(self, path):
        return 

    def isfile(self, path):
        """Return True if path is a file."""
        return False

    def islink(self, path):
        """Return True if path is a symbolic link."""
        return False

    def isdir(self, path):
        """Return True if path is a directory."""
        return True

    def getsize(self, path):
        """Return the size of the specified file in bytes."""
        return 0

    def getmtime(self, path):
        """Return the last modified time as a number of seconds since
        the epoch."""
        return 0

    def format_list(self, basedir, listing, ignore_err=True):
        mtimestr = "Sep 02  3:40"
        for basename in listing:
            yield "%s %3s %-8s %-8s %8s %s %s\r\n" % ("elc", 0, "", "",0, mtimestr, basename)

    def format_mlsx(self, basedir, listing, perms, facts, ignore_err=True):
        for dirname in listing:
            # item="type=dir;size=0;perm=el;modify=20071127230206; %s" % dirname
            item="modify=20130120092556;perm=el;size=4096;type=dir; %s" % dirname
            # print "FACT:%s" % item
            yield "%s\r\n"%item

    def open(self, filename, mode):
        return None

