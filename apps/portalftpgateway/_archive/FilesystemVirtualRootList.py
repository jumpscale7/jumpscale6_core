
from FilesystemVirtualRoot import FilesystemVirtualRoot

from OpenWizzy import o
import os

class FilesystemVirtualRootList(FilesystemVirtualRoot):
    """
    basis for 1 level down eg spaces
    """

    def __init__(self, root, cmd_channel,list):
        FilesystemVirtualRoot.__init__(self, root, cmd_channel)
        self.cwd = root
        self.list=list

    def listdir(self, path):
        print "list for rootfilesystemlist: %s" % self.cwd
        return self.list()

    def chdir(self, path):
        print "chdirrootfslist:%s" % path
        self._cwd=path
        #self._cwd = self.fs2ftp(path)

    def fs2ftp(self, path):
        p=o.system.fs.pathRemoveDirPart(path,self.cmd_channel.rootpath).replace("\\","/")
        if len(p)<>0 and p[0]<>"/":
            p="/"+p
        #print "fs2ftp_list: %s -> %s" % (path,p)
        return p

    def ftp2fs(self, ftppath):
        return self.root

