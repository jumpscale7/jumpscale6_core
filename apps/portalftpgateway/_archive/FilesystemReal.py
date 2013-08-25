from FilesystemBase import FilesystemBase

from JumpScale import j
import os


class FilesystemReal(FilesystemBase):

    def __init__(self, root, cmd_channel, ftproot, cwd, readonly=False):
        """
         - (str) root: the user "real" home directory (e.g. '/home/user')
         - (instance) cmd_channel: the FTPHandler class instance
        """
        FilesystemBase.__init__(self, root, cmd_channel)
        # Set initial current working directory.
        # By default initial cwd is set to "/" to emulate a chroot jail.
        # If a different behavior is desired (e.g. initial cwd = root,
        # to reflect the real filesystem) users overriding this class
        # are responsible to set _cwd attribute as necessary.
        self._cwd = '/'
        self._root = root
        self.cmd_channel = cmd_channel
        self.handler = None
        self.cwd = cwd  # @why cwd & _cwd
        self.cwdftp = ""
        self.ftproot = ftproot
        self.readonly = readonly

    def ftp2fs(self, ftppath):
        if ftppath.find(self.ftproot) == 0:
            ftppath = ftppath[len(self.ftproot):]
        result = j.system.fs.joinPaths(self.root, ftppath)
        return result

    def ftp2fs(self, ftppath):
        if ftppath.find(self.ftproot) == 0:
            ftppath = ftppath[len(self.ftproot):]
        result = j.system.fs.joinPaths(self.root, ftppath)
        return result

    def _ignorePath(self, item):
        # items=[]
        # for item in os.listdir(path):
        ext = j.system.fs.getFileExtension(item)
        if item.find(".quarantine") == 0 or item.find(".tmb") == 0:
            try:
                j.system.fs.remove(item)
            except:
                pass
            return True
        elif ext == "pyc":
            return True
        # else:
            # items.append(item)

    def listdir(self, path):
        """List the content of a directory."""
        path1 = self.ftp2fs(path)
        # print "listdir:%s:%s" %(path,path1)
        items = [item for item in os.listdir(path1) if not self._ignorePath(item)]
        return items

    def fs2ftp(self, fspath):
        p = j.system.fs.pathRemoveDirPart(fspath, self.root)
        if len(p) != 0 and p[0] != "/":
            p = "/" + p
        p = self.ftproot + p
        # print "fs2ftp: %s -> %s" % (fspath,p)
        return p

    def open(self, filename, mode):
        """Open a file returning its handler."""
        #@todo check on extension .redirect (file path:  $originalpath.$size.redirect) read from redirect where to go and repoint open
        if self.readonly and "w" in mode:
            raise RuntimeError("Cannot open file in write mode because filesystem %s is put in readonly." % self.root)
        else:
            path1 = self.ftp2fs(path)
            return open(filename, mode)

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

    # --- Wrapper methods around os.* calls

    def chdir(self, ftppath):
        """Change the current directory."""
        # temporarily join the specified directory to see if we have
        # permissions to do so
        path = self.ftp2fs(ftppath)
        print "chdir for %s : %s" % (ftppath, path)
        #basedir = os.getcwd()
        try:
            os.chdir(path)
        except OSError:
            raise
        else:
            self._cwd = ftppath

    def mkdir(self, ftppath):
        """Create the specified directory."""
        path = self.ftp2fs(ftppath)
        j.system.fs.createDir(path)

    def rmdir(self, path):
        """Remove the specified directory."""
        path = self.ftp2fs(path)
        os.rmdir(path)

    def remove(self, path):
        """Remove the specified file."""
        path = self.ftp2fs(path)
        os.remove(path)

    def rename(self, src, dst):
        """Rename the specified src file to the dst filename."""
        src = self.ftp2fs(src)
        dst = self.ftp2fs(dst)
        os.rename(src, dst)

    def chmod(self, path, mode):
        """Change file/directory mode."""
        raise NotImplementedError
        path = self.ftp2fs(path)
        if not hasattr(os, 'chmod'):
            raise NotImplementedError
        os.chmod(path, mode)

    def stat(self, path):
        """Perform a stat() system call on the given path."""
        return os.stat(path)

    def lstat(self, path):
        """Like stat but does not follow symbolic links."""
        path = self.ftp2fs(path)
        return os.lstat(path)

    if not hasattr(os, 'lstat'):
        lstat = stat

    # --- Wrapper methods around os.path.* calls

    def isfile(self, path):
        """Return True if path is a file."""
        path = self.ftp2fs(path)
        return os.path.isfile(path)

    def islink(self, path):
        """Return True if path is a symbolic link."""
        path = self.ftp2fs(path)
        return os.path.islink(path)

    def isdir(self, path):
        """Return True if path is a directory."""
        path = self.ftp2fs(path)
        return os.path.isdir(path)

    def getsize(self, path):
        """Return the size of the specified file in bytes."""
        path = self.ftp2fs(path)
        return os.path.getsize(path)

    def getmtime(self, path):
        """Return the last modified time as a number of seconds since
        the epoch."""
        path = self.ftp2fs(path)
        return os.path.getmtime(path)

    # def realpath(self, path):
        #"""Return the canonical version of path eliminating any
        # symbolic links encountered in the path (if they are
        # supported by the operating system).
        #"""
        # return os.path.realpath(path)

    def lexists(self, path):
        """Return True if path refers to an existing path, including
        a broken or circular symbolic link.
        """
        path = self.ftp2fs(path)
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

    if hasattr(os, 'readlink'):
        def readlink(self, path):
            """Return a string representing the path to which a
            symbolic link points.
            """
            path = self.ftp2fs(path)
            return os.readlink(path)
