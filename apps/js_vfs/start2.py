#!/usr/bin/env python

from __future__ import with_statement

import os
import sys
import errno
import time
from stat import S_IFDIR, S_IFLNK, S_IFREG  
from fuse import FUSE, FuseOSError, Operations
from errno import ENOENT
import time

import JumpScale.baselib.key_value_store

import leveldb

from JumpScale import j
import struct

j.application.start("fusehome")

j.logger.consoleloglevel = 5

class Stat():
    def __repr__(self):
        return str(self.__dict__)

    __str__=__repr__

class Base():
    def __init__(self,ddict={}):
        self.__dict__=ddict
        
        if ddict=={}:
            self.newStat()
        else:
            self.stat=Stat()   
            self.stat.st_mode,self.stat.st_nlink,self.stat.st_size,self.stat.st_ctime,self.stat.st_mtime,self.stat.st_atime,self.stat.st_uid,self.stat.st_gid=struct.unpack("IHQIIIII",self.st)
            self.__dict__.pop("st")

    def newStat(self):
        self.stat=Stat()
        self.stat.st_mode=17407
        self.stat.st_nlink=1
        self.stat.st_size=0
        now=int(time.time())
        self.stat.st_ctime=now
        self.stat.st_mtime=now
        self.stat.st_atime=now
        self.stat.st_uid=0
        self.stat.st_gid=0

    def __repr__(self):
        return str(self.__dict__)

    __str__=__repr__

class File(Base):
    def __init__(self,ddict={}):
        Base.__init__(self,ddict=ddict)
        if not self.__dict__.has_key("changes"):
            self.changes=[]
        self.type="F"

    def serialize(self):
        st=struct.pack("IHQIIIII",self.stat.st_mode,self.stat.st_nlink,self.stat.st_size,self.stat.st_ctime,self.stat.st_mtime,self.stat.st_atime,self.stat.st_uid,self.stat.st_gid)
        return {"changes":self.changes,"st":st}

        
class Dir(Base):
    def __init__(self,ddict={}):        
        Base.__init__(self,ddict=ddict)
        self.type="D"
        for item in ["files","dirs","links"]:
            if not self.__dict__.has_key(item):
                self.__dict__[item]=[]

    def serialize(self):
        st=struct.pack("IHQIIIII",self.stat.st_mode,self.stat.st_nlink,self.stat.st_size,self.stat.st_ctime,self.stat.st_mtime,self.stat.st_atime,self.stat.st_uid,self.stat.st_gid)
        return {"files":self.files,"dirs":self.dirs,"links":self.links,"st":st}


class Link(Base):
    def __init__(self,ddict={}):        
        Base.__init__(self,ddict=ddict)
        if not self.__dict__.has_key("dest"):
            self.target=""
        self.type="L"

    def serialize(self):
        st=struct.pack("IHQIIIII",self.stat.st_mode,self.stat.st_nlink,self.stat.st_size,self.stat.st_ctime,self.stat.st_mtime,self.stat.st_atime,self.stat.st_uid,self.stat.st_gid)
        return {"target":self.target,"st":st}


class MD():
    def __init__(self,user,reset=True):
        self.user=user
        self.rootpath="/opt/fuse/users/%s"%user
        j.system.fs.createDir(self.rootpath)

        self.cache={}

        if reset:
            j.system.fs.removeDirTree('%s/fs.db'%self.rootpath)
            j.system.fs.removeDirTree('/tmp/vfs')
            j.system.fs.createDir('/tmp/vfs')

        self.db=leveldb.DB('%s/fs.db'%self.rootpath, create_if_missing=True)
        self.serializer=j.db.serializers.getMessagePack()
        
        if not self.exists("/"):
            self.mkdir("/")


    def path(self,path):
        return path

    def getentry(self,path):
        if self.cache.has_key(path):
            # print "cachehit:%s"%path
            return self.cache[path]

        ddict= self.serializer.loads(self.db.get(self.path(path)))

        if ddict.has_key("changes"):
            self.cache[path]= File(ddict)
        elif ddict.has_key("files"):
            self.cache[path]= Dir(ddict)
        else:
            self.cache[path]= Link(ddict)

        return self.cache[path]

    def exists(self,path):
        if self.cache.has_key(path):
            return True
        return self.db.has(self.path(path))

    def setentry(self,path,obj):
        self.cache[path]=obj        
        data=self.serializer.dumps(obj.serialize())
        self.db.put(self.path(path),data)

    def access(self, path, mode):
        return True

    def chmod(self, path, mode=0100644):
        o=self.getentry(path)
        o.stat.st_mode=mode
        self.setentry(path,o)
        return 0

    def chown(self, path, uid, gid):
        o=self.getentry(path)
        o.stat.st_uid=uid
        o.stat.st_gid=gid
        self.setentry(path,o)
        return 0

    def create(self, path, mode=0100644):
        """
        create file
        """
        o=File(ddict={})
        o.stat.st_mode=mode
        self.registerInParent(path)
        self.setentry(path,o)

    def getattr(self,path):
        o=self.getentry(path)
        
        # st = os.lstat("/etc/fstab")
        if o.type=="D":
            st = os.lstat("/tmp")
            r2= dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
                          'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))
            o.stat.st_mode=r2["st_mode"]

        if o.type=="F":
            st = os.lstat("/etc/fstab")
            r2= dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
                          'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))
            o.stat.st_mode=r2["st_mode"]
        

        return o.stat.__dict__

    def readdir(self,path):
        o=self.getentry(path)
        r=[]
        if o.type=="D":
            r+=o.files
            r+=o.dirs
            r+=o.links
        
        print "dirs:%s"%r
        return r

    def readlink(self,path):
        o=self.getentry(path)
        if o.ttype<>"L":
            raise RuntimeError("error object %s should be link")
        return o.target

    def rmdir(self,path):
        self.db.delete(self.path(path))
        self.unregisterInParent(path)
        self.cache.pop(path)

    def registerInParent(self,path):
        if path.strip("/")<>"":
            parent=j.system.fs.getParent(path)
            op=self.getentry(parent)
            basedir=j.system.fs.getBaseName(path)
            if basedir not in op.dirs:
                op.dirs.append(basedir)
                self.setentry(parent,op)

    def unregisterInParent(self,path):
        if path.strip("/")<>"":
            parent=j.system.fs.getParent(path)
            op=self.getentry(parent)
            basedir=j.system.fs.getBaseName(path)
            if basedir in op.dirs:
                op.dirs.pop(op.dirs.index(basedir))
                self.setentry(parent,op)

    def mkdir(self,path,mode=17407):
        
        o=Dir(ddict={})
        
        o.stat.st_mode=mode
        o.stat.st_size=4096
        self.registerInParent(path)
        self.setentry(path,o)

    def unlink(self, path):
        self.db.delete(self.path(path))
        self.unregisterInParent(path)
        self.cache.pop(path)

    def symlink(self, target,path):
        o=Link(ddict={})
        o.target=target
        self.setentry(path,o)  

    def rename(self, old, new):
        o=self.getentry(old)
        self.setentry(new,o)
        self.unlink(old)
        self.registerInParent(new)
        self.cache.pop(old)

    def utimens(self, path, times=None):
        o=self.getentry(path)
        o.stat.st_mtime=times[0]
        o.stat.st_atime=times[1]
        self.setentry(path,o)

class VFS():

    def __init__(self,backend):
        self.backend=backend
        pass


    def _getTmpPath(self,path):
        if path.strip().strip("/")=="":
            path="%s/%s"%(self.root,"tmp")
        else:
            path2="/".join(path.split("/")[1:])
            path="%s/%s/%s"%(self.root,"tmp",path2)
        return path

    def _existsTmpPath(self,path):
        return j.system.fs.exists(path=self._getTmpPath(path))    


#SLOW IN PYTHON
class Buffer():
    def __init__(self,size):
        self.buffer=bytearray(1024*1024)
        self.start=0
        self.end=0
        self.path=""
        self.size=size
        self.fh=None
        self.free=True

    def write(self,buf, offset):
        st=offset-self.start
        self.end=st+len(buf)
        if self.end>self.size-1:
            self.flush()
        self.buffer[st:self.end]=buf
        # print self.end

    def flush(self):
        os.lseek(self.fh, self.start, os.SEEK_SET)
        os.write(self.fh, self.buffer[0:self.end])
        self.start=self.end+self.start
        self.end=0
   
class VFSFUSE(Operations):
    def __init__(self):
        self.root="/tmp/vfs"
        self.readonly=False
        self.buffers_active={} #key is path
        self.buffers=[]
        for i in range(10):
            self.buffers.append(Buffer(size=1024*1024))

        from Crypto.Cipher import AES
        self.encryptor = AES.new('This is a key123', AES.MODE_CBC, 'This is an IV456')


    # Filesystem methods
    # ==================

    def _full_path(self, partial):
        # fpath=str(os.path.join(self.root, partial))
        fpath="%s/%s"%(self.root,partial)
        print "fpath:%s"%fpath
        return fpath

    def log(self,cat,msg):
        print "%s:%s"%(cat,msg)

    def access(self, path, mode):
        #all access
        if j.md.access(path,mode)==False:
        # self.log("access",path)        
        # full_path = self._full_path(path)
        # if not os.access(full_path, mode):
            raise FuseOSError(errno.EACCES)

    def chmod(self, path, mode):
        self.log("chmod",path)
        # full_path = self._full_path(path)
        return j.md.chmod(path,mode)
        # return os.chmod(full_path, mode)

    def chown(self, path, uid, gid):
        self.log("chown",path)
        # full_path = self._full_path(path)
        return j.md.chown(path, uid, gid)
        # return os.chown(full_path, uid, gid)

    def getattr(self, path, fh=None):                
        # full_path = self._full_path(path)
        self.log("getattr",path)
        if not j.md.exists(path=path):
            print "does not exist"
            raise FuseOSError(ENOENT)
        return j.md.getattr(path)

        # st = os.lstat(full_path)
        # return dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
        #              'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))

    def readdir(self, path, fh):
        full_path = self._full_path(path)
        self.log("readdir","%s:%s"%(path,full_path))        
        # dirents=[]
        # if os.path.isdir(full_path):
        #     dirents.extend(os.listdir(full_path))
        dirents=j.md.readdir(path)
        for r in dirents:
            yield r

        # dirents = ['.', '..']
        # if path.strip().strip("/")=="":
        #     dirents.append(self.user)
        #     self.log("readdir.root",path)
        # else:
        #     full_path = self._full_path(path)
        #     self.log("readdir","%s:%s"%(path,full_path))
        #     if os.path.isdir(full_path):
        #         dirents.extend(os.listdir(full_path))
        # for r in dirents:
        #     yield r

    def readlink(self, path):
        self.log("readlink",path)
        # pathname = os.readlink(self._full_path(path))
        # if pathname.startswith("/"):
        #     # Path name is absolute, sanitize it.
        #     return os.path.relpath(pathname, self.root)
        # else:
        #     return pathname
        return j.md.readlink(path)

    def mknod(self, path, mode, dev):
        return
        # if self.readonly:
        #     fpath=self._getTmpPath(path)
        #     self.log("mknod.readonly",fpath)
        # else:
        #     fpath=self._full_path(path)
        #     self.log("mknod",fpath)
        # return os.mknod(fpath, mode, dev)

    def rmdir(self, path):
        self.log("rmdir",path)
        return j.md.rmdir(path)
        # full_path = self._full_path(path)
        # return os.rmdir(full_path)

    def mkdir(self, path, mode):  
        self.log("mkdir",path)
        j.md.mkdir(path,mode)
        # if self.readonly:
        #     path2=self._getTmpPath(path)
        #     self.log("mkdir.readonly",path2)
        #     j.system.fs.createDir(path2)
        #     from IPython import embed
        #     print "DEBUG NOW oo"
        #     embed()
            
        # else:
        path2=self._full_path(path)
        #     self.log("mkdir",path2)
        return os.mkdir(path2, mode)

    def statfs(self, path):
        self.log("statfs",path)
        return dict(f_bsize=512, f_blocks=4096, f_bavail=2048)
        # full_path = self._full_path(path)
        # stv = os.statvfs(full_path)
        # return dict((key, getattr(stv, key)) for key in ('f_bavail', 'f_bfree',
        #     'f_blocks', 'f_bsize', 'f_favail', 'f_ffree', 'f_files', 'f_flag',
        #     'f_frsize', 'f_namemax'))

    def unlink(self, path):
        self.log("unlink",path)
        return j.md.unlink(path)
        # return os.unlink(self._full_path(path))

    def symlink(self, target, name):
        self.log("symlink",path) 
        return j.md.symlink(target,name)   
        # return os.symlink(self._full_path(target), self._full_path(name))

    def rename(self, old, new):
        self.log("rename","%s->%s"%(old,new))   
        return j.md.rename(old,new)   
        # return os.rename(self._full_path(old), self._full_path(new))

    def link(self, target, name):
        self.log("link",path)    
        return j.md.symlink(target,name) 
        # return os.link(self._full_path(target), self._full_path(name))

    def utimens(self, path, times=None):
        return j.md.utimens(path, times)
        # return os.utime(self._full_path(path), times)

    # File methods
    # ============

    def open(self, path, flags):        
        full_path = self._full_path(path)
        self.log("open","%s:%s"%(path,full_path))
        return os.open(full_path, flags)

    def create(self, path, mode, fi=None):
        j.md.create(path,mode)
        # if self.readonly:
        #     self.log("create.readonly",path)
        #     full_path=self._getTmpPath(path)
        # else:
        #     self.log("create",path)
        #     full_path = self._full_path(path)
        full_path = self._full_path(path)
        return os.open(full_path, os.O_WRONLY | os.O_CREAT, mode)

    def read(self, path, length, offset, fh):
        self.log("read",path)
        os.lseek(fh, offset, os.SEEK_SET)
        buf=os.read(fh, length)

        # buf=self.encryptor.decrypt(buf)

    def findBuffer(self):
        self.buffers_active

    def write(self, path, buf, offset, fh):
        if self.readonly:
            self.log("write.readonly",path)
            return 
        # self.log("write",path)
        # if not self.active.has_key(path):
        #      self.active[path]=Buffer()
        #      self.active[path].start=offset
        # self.active[path].buffer+=buf
        # if len(self.active[path].buffer)>self.writeBlockFlushSize:
        #     print "bufferfull for %s"%path
        #     self.flush(path,fh,sync=False)
        # return len(buf)

        # buf=self.encryptor.encrypt(buf)

        os.lseek(fh, offset, os.SEEK_SET)
        return os.write(fh, buf)

        if not self.buffers_active.has_key(path):
            for b in self.buffers:
                if b.free:
                    self.buffers_active[path]=b
                    b.fh=fh
                    b.start=offset

        self.buffers_active[path].write(buf,offset)

        return len(buf)


    def truncate(self, path, length, fh=None):
        self.log("truncate",path)
        full_path = self._full_path(path)
        with open(full_path, 'r+') as f:
            f.truncate(length)

    def flush(self, path, fh,sync=False):
        self.log("flush",path)
        # try:
        #     os.lseek(fh, self.active[path].start, os.SEEK_SET)
        #     os.write(fh, self.active[path].buffer)
        # except Exception,e:
        #     import ipdb
        #     ipdb.set_trace()
            
        if sync:
            return os.fsync(fh)

    def release(self, path, fh):
        self.log("release",path)
        # self.flush(path,fh,sync=False)
        # self.buffers_active[path].flush()

        o=j.md.getentry(path)
        o.stat.st_size=os.stat(self._full_path(path)).st_size
        j.md.setentry(path,o)
        return os.close(fh)

    def fsync(self, path, fdatasync, fh):
        self.log("fsync",path)
        return self.flush(path, fh)


# def main(mountpoint, backend,root):
#     FUSE(Passthrough(root,backend), mountpoint, foreground=True)

if __name__ == '__main__':
    # main(sys.argv[2], sys.argv[1])
    user=sys.argv[1]
    fusepath="/opt/fuse/%s"%user
    j.system.fs.removeDirTree(fusepath)
    j.system.fs.createDir(fusepath)
    j.md=MD(user=user,reset=True)
    j.vfs=VFS(backend="/opt/backend/")
    FUSE(VFSFUSE(), fusepath, foreground=True)

