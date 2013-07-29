
from FilesystemBase import FilesystemBase

from OpenWizzy import o
import os

class FilesystemVirtualRoot(FilesystemBase):
    """
    is our virtual root
    """

    def __init__(self, root, cmd_channel):
        #_Base.__init__(self, root, cmd_channel)
        FilesystemBase.__init__(self, root, cmd_channel)
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
        return

    def rmdir(self, path):
        return

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
            item="type=dir;size=0;perm=el;modify=20071127230206; %s\r\n" % dirname
            #print item,
            yield item

    def open(self, filename, mode):
        return None
