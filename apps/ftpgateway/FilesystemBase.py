
from OpenWizzy import o
import os
import time
import stat
from tarfile import filemode as _filemode

_months_map = {1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun', 7:'Jul',
               8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec'}

class FilesystemBase(object):
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
        self.cwd = '/'
        self.root = root
        self.ftproot= root
        self.cmd_channel = cmd_channel
        self.handler=None

    # --- Pathname / conversion utilities


    def realpath(self,path):
        return self.ftp2fs(path)

    def joinPaths(self,*args):
        out=""
        for arg in args:
            out+="%s/"%arg
        out=out.replace("//","/")
        out=out.replace("//","/")        
        if len(out)>2:
            out=out.rstrip("/")
        return out
      

    def ftpnorm(self, ftppath):
        if ftppath.strip()=="":
            ftppath=self.joinPaths(self.ftproot,self.cwd)
        
        ftppathn=os.path.normpath(ftppath)
        ftppathn=ftppathn.replace("\\","/").strip()
        # print "%s -> %s" % (ftppath,ftppathn)

        if ftppathn[0]<>"/":
            ftppathn=self.joinPaths(self.ftproot,self.cwd,ftppathn)
        return ftppathn

    def _removeFtproot(self,ftppath):
        if ftppath.find(self.ftproot)==0:
            ftppath=ftppath[len(self.ftproot)+1:]
        else:
            import ipdb; ipdb.set_trace()
            
            raise RuntimeError("ftppath needs to start with self.ftproot")
        return ftppath

    def ftp2fs(self, ftppath):
        ftppath=self.ftpnorm(ftppath)
        ftppath=self._removeFtproot(ftppath)
        # print "REMOVEROOT:%s"%ftppath
        result= o.system.fs.joinPaths(self.root,ftppath)
        # print "ISDIRPOST:%s"%result
        return result

        # if os.path.normpath(self.root) == os.sep:
        #     return os.path.normpath(self.ftpnorm(ftppath))
        # else:
        #     p = self.ftpnorm(ftppath)[1:]
        #     return os.path.normpath(os.path.join(self.root, p))

    # def ftpnorm(self, ftppath):
    #     """Normalize a "virtual" ftp pathname (tipically the raw string
    #     coming from client) depending on the current working directory.

    #     Example (having "/foo" as current working directory):
    #     >>> ftpnorm('bar')
    #     '/foo/bar'

    #     Note: directory separators are system independent ("/").
    #     Pathname returned is always absolutized.
    #     """
    #     if os.path.isabs(ftppath):
    #         p = os.path.normpath(ftppath)
    #     else:
    #         p = os.path.normpath(os.path.join(self.cwd, ftppath))
    #     # normalize string in a standard web-path notation having '/'
    #     # as separator.
    #     p = p.replace("\\", "/")
    #     # os.path.normpath supports UNC paths (e.g. "//a/b/c") but we
    #     # don't need them.  In case we get an UNC path we collapse
    #     # redundant separators appearing at the beginning of the string
    #     while p[:2] == '//':
    #         p = p[1:]
    #     # Anti path traversal: don't trust user input, in the event
    #     # that self.cwd is not absolute, return "/" as a safety measure.
    #     # This is for extra protection, maybe not really necessary.
    #     if not os.path.isabs(p):
    #         raise RuntimeError("ftpnorm error, possible security breach")
    #         p = "/"
    #     return p

    # def ftp2fs(self, ftppath):
    #     """Translate a "virtual" ftp pathname (tipically the raw string
    #     coming from client) into equivalent absolute "real" filesystem
    #     pathname.

    #     Example (having "/home/user" as root directory):
    #     >>> ftp2fs("foo")
    #     '/home/user/foo'

    #     Note: directory separators are system dependent.
    #     """
    #     raise NotImplementedError

    # def fs2ftp(self, fspath):
    #     """Translate a "real" filesystem pathname into equivalent
    #     absolute "virtual" ftp pathname depending on the user's
    #     root directory.

    #     Example (having "/home/user" as root directory):
    #     >>> fs2ftp("/home/user/foo")
    #     '/foo'

    #     As for ftpnorm, directory separators are system independent
    #     ("/") and pathname returned is always absolutized.

    #     """
    #     raise NotImplementedError


    def validpath(self, path):
        """
        """
        raise RuntimeError("not implemented")

    def openfile(self, filename, mode):
        """Open a file returning its handler"""
        raise RuntimeError("not implemented")        

    def mkstemp(self, suffix='', prefix='', dir=None, mode='wb'):
        """A wrap around tempfile.mkstemp creating a file with a unique
        name.  Unlike mkstemp it returns an object with a file-like
        interface.
        """
        raise RuntimeError("not implemented")        

    def chdir(self, ftppath):
        """Change the current directory."""
        raise RuntimeError("not implemented")        

    def mkdir(self, ftppath):
        """Create the specified directory."""
        raise RuntimeError("not implemented")        

    def listdir(self, path):
        """List the content of a directory."""
        raise RuntimeError("not implemented")        

    def rmdir(self, path):
        """Remove the specified directory."""
        raise RuntimeError("not implemented")        

    def remove(self, path):
        """Remove the specified file."""
        raise RuntimeError("not implemented")        

    def rename(self, src, dst):
        """Rename the specified src file to the dst filename."""
        raise RuntimeError("not implemented")        

    def chmod(self, path, mode):
        """Change file/directory mode."""
        raise NotImplementedError

    def stat(self, path):
        """Perform a stat() system call on the given path."""
        return os.stat(path)

    def lstat(self, path):
        """Like stat but does not follow symbolic links."""
        raise NotImplementedError

    if not hasattr(os, 'lstat'):
        lstat = stat

    # --- Wrapper methods around os.path.* calls

    def isfile(self, path):
        """Return True if path is a file."""
        raise NotImplementedError

    def islink(self, path):
        """Return True if path is a symbolic link."""
        raise NotImplementedError

    def isdir(self, path):
        """Return True if path is a directory."""
        raise NotImplementedError

    def getsize(self, path):
        """Return the size of the specified file in bytes."""
        raise NotImplementedError

    def getmtime(self, path):
        """Return the last modified time as a number of seconds since
        the epoch."""
        raise NotImplementedError

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
        return os.path.lexists(path)

    def get_user_by_uid(self, uid):
        """Return the username associated with user id.
        If this can't be determined return raw uid instead.
        On Windows just return "owner".
        """
        raise NotImplementedError

    def get_group_by_gid(self, gid):
        """Return the groupname associated with group id.
        If this can't be determined return raw gid instead.
        On Windows just return "group".
        """
        raise NotImplementedError

    def readlink(self, path):
        """Return a string representing the path to which a
        symbolic link points.
        """
        raise NotImplementedError

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
        try:      
            # print "format_mlsx:%s"%basedir
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

            basedir2=self.ftp2fs(basedir)
            for basename in listing:
                file = os.path.join(basedir2, basename)
                retfacts = dict()
                # in order to properly implement 'unique' fact (RFC-3659,
                # chapter 7.5.2) we are supposed to follow symlinks, hence
                try:
                    st = os.stat(file) 
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
                # print "FACT:%s" % factstring+" "+basename
                yield "%s %s\r\n" % (factstring, basename)
        except Exception, err:
            from pylabs.Shell import ipshellDebug,ipshell
            print "DEBUG NOW error in format MLSD"
            ipshell()
                

