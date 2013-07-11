from pyftpdlib.ftpserver import AbstractedFS

from pylabs import q
import os


# --- filesystem

class AbstractedFS(object):
    """A class used to interact with the file system, providing a
    cross-platform interface compatible with both Windows and
    UNIX style filesystems where all paths use "/" separator.

    AbstractedFS distinguishes between "real" filesystem paths and
    "virtual" ftp paths emulating a UNIX chroot jail where the user
    can not escape its home directory (example: real "/home/user"
    path will be seen as "/" by the client)

    It also provides some utility methods and wraps around all os.*
    calls involving operations against the filesystem like creating
    files or removing directories.
    """

    def __init__(self, root, cmd_channel):
        """
         - (str) root: the user "real" home directory (e.g. '/home/user')
         - (instance) cmd_channel: the FTPHandler class instance
        """
        # Set initial current working directory.
        # By default initial cwd is set to "/" to emulate a chroot jail.
        # If a different behavior is desired (e.g. initial cwd = root,
        # to reflect the real filesystem) users overriding this class
        # are responsible to set _cwd attribute as necessary.
        self._cwd = '/'
        self._root = root
        self.cmd_channel = cmd_channel
        self.handler=None


    @property
    def root(self):
        """The user home directory."""
        return self._root

    @property
    def cwd(self):
        """The user current working directory."""
        return self._cwd

    @root.setter
    def root(self, path):
        self._root = path

    @cwd.setter
    def cwd(self, path):
        self._cwd = path

    # --- Pathname / conversion utilities

    def ftpnorm(self, ftppath):
        """Normalize a "virtual" ftp pathname (tipically the raw string
        coming from client) depending on the current working directory.

        Example (having "/foo" as current working directory):
        >>> ftpnorm('bar')
        '/foo/bar'

        Note: directory separators are system independent ("/").
        Pathname returned is always absolutized.
        """
        if os.path.isabs(ftppath):
            p = os.path.normpath(ftppath)
        else:
            p = os.path.normpath(os.path.join(self.cwd, ftppath))
        # normalize string in a standard web-path notation having '/'
        # as separator.
        p = p.replace("\\", "/")
        # os.path.normpath supports UNC paths (e.g. "//a/b/c") but we
        # don't need them.  In case we get an UNC path we collapse
        # redundant separators appearing at the beginning of the string
        while p[:2] == '//':
            p = p[1:]
        # Anti path traversal: don't trust user input, in the event
        # that self.cwd is not absolute, return "/" as a safety measure.
        # This is for extra protection, maybe not really necessary.
        if not os.path.isabs(p):
            p = "/"
        return p

    def ftp2fs(self, ftppath):
        """Translate a "virtual" ftp pathname (tipically the raw string
        coming from client) into equivalent absolute "real" filesystem
        pathname.

        Example (having "/home/user" as root directory):
        >>> ftp2fs("foo")
        '/home/user/foo'

        Note: directory separators are system dependent.
        """
        # as far as I know, it should always be path traversal safe...
        if os.path.normpath(self.root) == os.sep:
            return os.path.realpath(os.path.normpath(self.ftpnorm(ftppath)))
        else:
            p = self.ftpnorm(ftppath)[1:]
            return os.path.realpath(os.path.normpath(os.path.join(self.root, p)))

    def fs2ftp(self, fspath):
        """Translate a "real" filesystem pathname into equivalent
        absolute "virtual" ftp pathname depending on the user's
        root directory.

        Example (having "/home/user" as root directory):
        >>> fs2ftp("/home/user/foo")
        '/foo'

        As for ftpnorm, directory separators are system independent
        ("/") and pathname returned is always absolutized.

        On invalid pathnames escaping from user's root directory
        (e.g. "/home" when root is "/home/user") always return "/".
        """
        if os.path.isabs(fspath):
            p = os.path.normpath(fspath)
        else:
            p = os.path.normpath(os.path.join(self.root, fspath))
        if not self.validpath(p):
            return '/'
        p = p.replace(os.sep, "/")
        p = p[len(self.root):]
        if not p.startswith('/'):
            p = '/' + p
        return p

    def validpath(self, path):
        """Check whether the path belongs to user's home directory.
        Expected argument is a "real" filesystem pathname.

        If path is a symbolic link it is resolved to check its real
        destination.

        Pathnames escaping from user's root directory are considered
        not valid.
        """
        return True
        root = self.realpath(self.root)
        path = self.realpath(path)
        if not root.endswith(os.sep):
            root = root + os.sep
        if not path.endswith(os.sep):
            path = path + os.sep
        if path[0:len(root)] == root:
            return True
        from pylabs.Shell import ipshellDebug,ipshell
        print "DEBUG NOW validpath is not valid"
        ipshell()

        return False

    # --- Wrapper methods around open() and tempfile.mkstemp

    def open(self, filename, mode):
        """Open a file returning its handler."""
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
        path=self.ftp2fs(ftppath)
        print "chdir for %s : %s"%(ftppath,path)
        #basedir = os.getcwd()
        try:
            os.chdir(path)
        except OSError:
            raise
        else:
            self._cwd = ftppath

    def mkdir(self, ftppath):
        """Create the specified directory."""
        ftppath=self.ftpnorm(ftppath)
        path=self.ftp2fs(ftppath)
        q.system.fs.createDir(path)

    def listdir(self, path):
        """List the content of a directory."""
        path1=self.ftp2fs(path)
        #print "listdir:%s:%s" %(path,path1)
        return os.listdir(path1)

    def rmdir(self, path):
        """Remove the specified directory."""
        path=self.ftp2fs(path)
        os.rmdir(path)

    def remove(self, path):
        """Remove the specified file."""
        path=self.ftpnorm(path)
        path=self.ftp2fs(path)
        os.remove(path)

    def rename(self, src, dst):
        """Rename the specified src file to the dst filename."""
        src=self.ftp2fs(src)
        dst=self.ftp2fs(dst)
        os.rename(src, dst)

    def chmod(self, path, mode):
        """Change file/directory mode."""
        raise NotImplementedError
        path=self.ftp2fs(path)
        if not hasattr(os, 'chmod'):
            raise NotImplementedError
        os.chmod(path, mode)

    def stat(self, path):
        """Perform a stat() system call on the given path."""
        return os.stat(path)

    def lstat(self, path):
        """Like stat but does not follow symbolic links."""
        path=self.ftp2fs(path)
        return os.lstat(path)

    if not hasattr(os, 'lstat'):
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
        if pwd is not None:
            try:
                return pwd.getpwuid(uid).pw_name
            except KeyError:
                return uid
        else:
            return "owner"

    def get_group_by_gid(self, gid):
        """Return the groupname associated with group id.
        If this can't be determined return raw gid instead.
        On Windows just return "group".
        """
        if grp is not None:
            try:
                return grp.getgrgid(gid).gr_name
            except KeyError:
                return gid
        else:
            return "group"

    if hasattr(os, 'readlink'):
        def readlink(self, path):
            """Return a string representing the path to which a
            symbolic link points.
            """
            return os.readlink(path)

    # --- Listing utilities

    def get_list_dir(self, path):
        """"Return an iterator object that yields a directory listing
        in a form suitable for LIST command.
        """
        if self.isdir(path):
            listing = self.listdir(path)
            listing.sort()
            return self.format_list(path, listing)
        # if path is a file or a symlink we return information about it
        else:
            basedir, filename = os.path.split(path)
            self.lstat(path)  # raise exc in case of problems
            return self.format_list(basedir, [filename])

    def format_list(self, basedir, listing, ignore_err=True):
        """Return an iterator object that yields the entries of given
        directory emulating the "/bin/ls -lA" UNIX command output.

         - (str) basedir: the absolute dirname.
         - (list) listing: the names of the entries in basedir
         - (bool) ignore_err: when False raise exception if os.lstat()
         call fails.

        On platforms which do not support the pwd and grp modules (such
        as Windows), ownership is printed as "owner" and "group" as a
        default, and number of hard links is always "1". On UNIX
        systems, the actual owner, group, and number of links are
        printed.

        This is how output appears to client:

        -rw-rw-rw-   1 owner   group    7045120 Sep 02  3:47 music.mp3
        drwxrwxrwx   1 owner   group          0 Aug 31 18:50 e-books
        -rw-rw-rw-   1 owner   group        380 Sep 02  3:40 module.py
        """
        if self.cmd_channel.use_gmt_times:
            timefunc = time.gmtime
        else:
            timefunc = time.localtime
        now = time.time()
        for basename in listing:
            file = os.path.join(basedir, basename)
            try:
                st = self.lstat(file)
            except OSError:
                if ignore_err:
                    continue
                raise
            perms = _filemode(st.st_mode)  # permissions
            nlinks = st.st_nlink  # number of links to inode
            if not nlinks:  # non-posix system, let's use a bogus value
                nlinks = 1
            size = st.st_size  # file size
            uname = self.get_user_by_uid(st.st_uid)
            gname = self.get_group_by_gid(st.st_gid)
            mtime = timefunc(st.st_mtime)
            # if modificaton time > 6 months shows "month year"
            # else "month hh:mm";  this matches proftpd format, see:
            # http://code.google.com/p/pyftpdlib/issues/detail?id=187
            if (now - st.st_mtime) > 180 * 24 * 60 * 60:
                fmtstr = "%d  %Y"
            else:
                fmtstr = "%d %H:%M"
            try:
                mtimestr = "%s %s" % (_months_map[mtime.tm_mon],
                                      time.strftime(fmtstr, mtime))
            except ValueError:
                # It could be raised if last mtime happens to be too
                # old (prior to year 1900) in which case we return
                # the current time as last mtime.
                mtime = timefunc()
                mtimestr = "%s %s" % (_months_map[mtime.tm_mon],
                                      time.strftime("%d %H:%M", mtime))

            # if the file is a symlink, resolve it, e.g. "symlink -> realfile"
            if stat.S_ISLNK(st.st_mode) and hasattr(self, 'readlink'):
                basename = basename + " -> " + self.readlink(file)

            # formatting is matched with proftpd ls output
            yield "%s %3s %-8s %-8s %8s %s %s\r\n" % (perms, nlinks, uname, gname,
                                                      size, mtimestr, basename)

    def format_mlsx(self, basedir, listing, perms, facts, ignore_err=False):
        """Return an iterator object that yields the entries of a given
        directory or of a single file in a form suitable with MLSD and
        MLST commands.

        Every entry includes a list of "facts" referring the listed
        element.  See RFC-3659, chapter 7, to see what every single
        fact stands for.

         - (str) basedir: the absolute dirname.
         - (list) listing: the names of the entries in basedir
         - (str) perms: the string referencing the user permissions.
         - (str) facts: the list of "facts" to be returned.
         - (bool) ignore_err: when False raise exception if os.stat()
         call fails.

        Note that "facts" returned may change depending on the platform
        and on what user specified by using the OPTS command.

        This is how output could appear to the client issuing
        a MLSD request:

        type=file;size=156;perm=r;modify=20071029155301;unique=801cd2; music.mp3
        type=dir;size=0;perm=el;modify=20071127230206;unique=801e33; ebooks
        type=file;size=211;perm=r;modify=20071103093626;unique=801e32; module.py
        """
        basedir=self.ftp2fs(basedir)
        if self.cmd_channel.use_gmt_times:
            timefunc = time.gmtime
        else:
            timefunc = time.localtime
        permdir = ''.join([x for x in perms if x not in 'arw'])
        permfile = ''.join([x for x in perms if x not in 'celmp'])
        if ('w' in perms) or ('a' in perms) or ('f' in perms):
            permdir += 'c'
        if 'd' in perms:
            permdir += 'p'

        for basename in listing:
            file = os.path.join(basedir, basename)
            retfacts = dict()
            # in order to properly implement 'unique' fact (RFC-3659,
            # chapter 7.5.2) we are supposed to follow symlinks, hence
            # use os.stat() instead of os.lstat()
            try:
                st = self.stat(file)
            except OSError:
                if ignore_err:
                    print "error for %s, cannot list (stat)" % file
                    continue
                raise
            # type + perm
            if stat.S_ISDIR(st.st_mode):
                if 'type' in facts:
                    if basename == '.':
                        retfacts['type'] = 'cdir'
                    elif basename == '..':
                        retfacts['type'] = 'pdir'
                    else:
                        retfacts['type'] = 'dir'
                if 'perm' in facts:
                    retfacts['perm'] = permdir
            else:
                if 'type' in facts:
                    retfacts['type'] = 'file'
                if 'perm' in facts:
                    retfacts['perm'] = permfile
            if 'size' in facts:
                retfacts['size'] = st.st_size  # file size
            # last modification time
            if 'modify' in facts:
                try:
                    retfacts['modify'] = time.strftime("%Y%m%d%H%M%S",
                                                        timefunc(st.st_mtime))
                # it could be raised if last mtime happens to be too old
                # (prior to year 1900)
                except ValueError:
                    pass
            if 'create' in facts:
                # on Windows we can provide also the creation time
                try:
                    retfacts['create'] = time.strftime("%Y%m%d%H%M%S",
                                                        timefunc(st.st_ctime))
                except ValueError:
                    pass
            # UNIX only
            if 'unix.mode' in facts:
                retfacts['unix.mode'] = oct(st.st_mode & 0777)
            if 'unix.uid' in facts:
                retfacts['unix.uid'] = st.st_uid
            if 'unix.gid' in facts:
                retfacts['unix.gid'] = st.st_gid

            # We provide unique fact (see RFC-3659, chapter 7.5.2) on
            # posix platforms only; we get it by mixing st_dev and
            # st_ino values which should be enough for granting an
            # uniqueness for the file listed.
            # The same approach is used by pure-ftpd.
            # Implementors who want to provide unique fact on other
            # platforms should use some platform-specific method (e.g.
            # on Windows NTFS filesystems MTF records could be used).
            if 'unique' in facts:
                retfacts['unique'] = "%xg%x" % (st.st_dev, st.st_ino)

            # facts can be in any order but we sort them by name
            factstring = "".join(["%s=%s;" % (x, retfacts[x]) \
                                  for x in sorted(retfacts.keys())])
            yield "%s %s\r\n" % (factstring, basename)


class RootFilesystem(AbstractedFS):
    """
    is our virtual root
    """

    def __init__(self, root, cmd_channel):
        #_Base.__init__(self, root, cmd_channel)
        AbstractedFS.__init__(self, root, cmd_channel)
        # initial cwd was set to "/" to emulate a chroot jail
        self.cwd = "/"

    def validpath(self, path):
        return True

    def mkstemp(self, suffix='', prefix='', dir=None, mode='wb'):
        return None

    def listdir(self, path):
        return ["spaces","buckets","actors","contentdirs","stor"]

    def chdir(self, path):
        self._cwd = "/"

    def mkdir(self, path):
        q.system.fs.createDir(pathr)
        raise RuntimeError("not implemented")

    def rmdir(self, path):
        return

    def remove(self, path):
        return

    def rename(self, src, dst):
        return

    def chmod(self, path, mode):
        return

    def stat(self, path):
        from pylabs.Shell import ipshellDebug,ipshell
        print "DEBUG NOW stat"
        ipshell()

    def lstat(self, path):
        return self.stat(path)

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
            item="type=dir;size=0;perm=el;modify=20071127230206; %s\r\n" % dirname
            #print item,
            yield item

    def open(self, filename, mode):
        return None


class RootFilesystemList(RootFilesystem):
    """
    basis for 1 level down eg spaces
    """

    def __init__(self, root, cmd_channel,list):
        AbstractedFS.__init__(self, root, cmd_channel)
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
        p=q.system.fs.pathRemoveDirPart(path,self.cmd_channel.rootpath).replace("\\","/")
        if len(p)<>0 and p[0]<>"/":
            p="/"+p
        #print "fs2ftp_list: %s -> %s" % (path,p)
        return p

    def ftp2fs(self, ftppath):
        return self.root

class BaseFilesystem(AbstractedFS):
    """
    is our virtual root
    """

    def __init__(self, root, cmd_channel,ftproot,cwd,readonly=False):
        #_Base.__init__(self, root, cmd_channel)
        AbstractedFS.__init__(self, root, cmd_channel)
        self.cwd = cwd
        self.cwdftp=""
        self.ftproot=ftproot
        self.readonly=readonly

    #def chdir(self, path):
        #self._cwd=path

    def ftp2fs(self, ftppath):
        if ftppath.find(self.ftproot)==0:
            ftppath=ftppath[len(self.ftproot):]
        result= q.system.fs.joinPaths(self.root,ftppath)
        return result

    def _ignorePath(self,item):
        #items=[]
        #for item in os.listdir(path):
        ext=q.system.fs.getFileExtension(item)
        if item.find(".quarantine")==0 or item.find(".tmb")==0:
            try:
                q.system.fs.remove(item)
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
        #print "listdir:%s:%s" %(path,path1)
        items=[item for item in os.listdir(path1) if not self._ignorePath(item)]
        return items

    def mkdir(self, path):
        pathr=self.ftp2fs(path)
        q.system.fs.createDir(pathr)

    def fs2ftp(self, fspath):
        p=q.system.fs.pathRemoveDirPart(fspath,self.root)
        if len(p)<>0 and p[0]<>"/":
            p="/"+p
        p=self.ftproot+p
        #print "fs2ftp: %s -> %s" % (fspath,p)
        return p

    def open(self, filename, mode):
        """Open a file returning its handler."""
        #@todo check on extension .redirect (file path:  $originalpath.$size.redirect) read from redirect where to go and repoint open
        #if self.readonly and "w" in mode:
            #return None

        return open(filename, mode)



