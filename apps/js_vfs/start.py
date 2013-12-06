#!/usr/bin/env python

from __future__ import with_statement

import os
import sys
import errno
import time
from stat import S_IFDIR, S_IFLNK, S_IFREG  
from fuse import FUSE, FuseOSError, Operations
from errno import ENOENT

from JumpScale import j

j.application.start("fusehome")

j.logger.consoleloglevel = 5

class DB():
    

class Passthrough(Operations):
    def __init__(self, organization,user):
        path=j.system.fs.joinPaths("/opt/home/",organization,user)
        j.system.fs.createDir(path)
        self.root=path
        self.user=user
        self.organization=organization
        self.readonly=True

    def _full_path(self, partial):
        if partial.startswith("/"):
            partial = partial[1:]

        splitted=partial.split("/")
        user=splitted[0]

        partial2="/".join(splitted[1:])

        if self._existsTmpPath(partial2):
            path=self._getTmpPath(partial2)
        else:
            path = os.path.join("/opt/home/defaulthome/", partial2)

        print "partial:%s fullpath:%s"%(partial,path)

        return path

    # Filesystem methods
    # ==================

    def _getTmpPath(self,path):
        if path.strip().strip("/")=="":
            path="%s/%s"%(self.root,"tmp")
        else:
            path2="/".join(path.split("/")[1:])
            path="%s/%s/%s"%(self.root,"tmp",path2)
        return path

    def _existsTmpPath(self,path):
        return j.system.fs.exists(path=self._getTmpPath(path))

    def log(self,cat,msg):
        print "%s:%s"%(cat,msg)

    def access(self, path, mode):
        self.log("access",path)
        full_path = self._full_path(path)
        if not os.access(full_path, mode):
            raise FuseOSError(errno.EACCES)

    def chmod(self, path, mode):
        self.log("chmod",path)
        full_path = self._full_path(path)
        self.log("chmod",path)
        return os.chmod(full_path, mode)

    def chown(self, path, uid, gid):
        self.log("chown",path)
        full_path = self._full_path(path)
        self.log("chown",path)
        return os.chown(full_path, uid, gid)

    def getattr(self, path, fh=None):        
        self.log("getattr",path)
        full_path = self._full_path(path)
        if not j.system.fs.exists(path=full_path):
            raise FuseOSError(ENOENT)
        st = os.lstat(full_path)
        return dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
                     'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))

    def readdir(self, path, fh):
        dirents = ['.', '..']
        if path.strip().strip("/")=="":
            dirents.append(self.user)
            self.log("readdir.root",path)
        else:
            full_path = self._full_path(path)
            self.log("readdir","%s:%s"%(path,full_path))
            if os.path.isdir(full_path):
                dirents.extend(os.listdir(full_path))
        for r in dirents:
            yield r

    def readlink(self, path):
        self.log("readlink",path)
        pathname = os.readlink(self._full_path(path))
        if pathname.startswith("/"):
            # Path name is absolute, sanitize it.
            return os.path.relpath(pathname, self.root)
        else:
            return pathname

    def mknod(self, path, mode, dev):
        if self.readonly:
            fpath=self._getTmpPath(path)
            self.log("mknod.readonly",fpath)
        else:
            fpath=self._full_path(path)
            self.log("mknod",fpath)
        return os.mknod(fpath, mode, dev)

    def rmdir(self, path):
        self.log("rmdir",path)
        full_path = self._full_path(path)
        return os.rmdir(full_path)



    def mkdir(self, path, mode):  
        if self.readonly:
            path2=self._getTmpPath(path)
            self.log("mkdir.readonly",path2)
            j.system.fs.createDir(path2)
            from IPython import embed
            print "DEBUG NOW oo"
            embed()
            
        else:
            path2=self._full_path(path)
            self.log("mkdir",path2)
        return os.mkdir(path2, mode)

    def statfs(self, path):
        self.log("statfs",path)
        full_path = self._full_path(path)
        stv = os.statvfs(full_path)
        return dict((key, getattr(stv, key)) for key in ('f_bavail', 'f_bfree',
            'f_blocks', 'f_bsize', 'f_favail', 'f_ffree', 'f_files', 'f_flag',
            'f_frsize', 'f_namemax'))

    def unlink(self, path):
        self.log("unlink",path)
        return os.unlink(self._full_path(path))

    def symlink(self, target, name):
        self.log("symlink",path)    
        return os.symlink(self._full_path(target), self._full_path(name))

    def rename(self, old, new):
        self.log("rename","%s->%s"%(old,new))   
        return os.rename(self._full_path(old), self._full_path(new))

    def link(self, target, name):
        self.log("link",path)    
        return os.link(self._full_path(target), self._full_path(name))

    def utimens(self, path, times=None):
        return os.utime(self._full_path(path), times)

    # File methods
    # ============

    def open(self, path, flags):        
        full_path = self._full_path(path)
        self.log("open","%s:%s"%(path,full_path))
        return os.open(full_path, flags)

    def create(self, path, mode, fi=None):
        if self.readonly:
            self.log("create.readonly",path)
            full_path=self._getTmpPath(path)
        else:
            self.log("create",path)
            full_path = self._full_path(path)

        return os.open(full_path, os.O_WRONLY | os.O_CREAT, mode)

    def read(self, path, length, offset, fh):
        self.log("read",path)
        os.lseek(fh, offset, os.SEEK_SET)
        return os.read(fh, length)

    def write(self, path, buf, offset, fh):
        if self.readonly:
            self.log("write.readonly",path)
            return 
        self.log("write",path)
        os.lseek(fh, offset, os.SEEK_SET)
        return os.write(fh, buf)

    def truncate(self, path, length, fh=None):
        self.log("truncate",path)
        full_path = self._full_path(path)
        with open(full_path, 'r+') as f:
            f.truncate(length)

    def flush(self, path, fh):
        self.log("flush",path)     
        return os.fsync(fh)

    def release(self, path, fh):
        self.log("release",path)   
        return os.close(fh)

    def fsync(self, path, fdatasync, fh):
        self.log("fsync",path)
        return self.flush(path, fh)


def main(mountpoint, root):
    FUSE(Passthrough(root), mountpoint, foreground=True)

if __name__ == '__main__':
    # main(sys.argv[2], sys.argv[1])
    organization=sys.argv[1]
    user=sys.argv[2]

    FUSE(Passthrough(organization,user), "/home", foreground=True)

