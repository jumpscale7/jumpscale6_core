
from FilesystemBase import FilesystemBase

from OpenWizzy import o
import os
import inspect

class OsisList(FilesystemBase):
    """
    basis for 1 level down eg spaces
    """

    def __init__(self, cmd_channel, client):
        FilesystemBase.__init__(self, 'osis', cmd_channel)
        self.cwd = "/"
        self.list=[]
        self.name2path={}
        self.ftproot="/%s"% 'osis'
        self.client = client
        self.actors = o.apps.system.contentmanager.getActors()

    def _getActorClient(self, appname, actorname):
        if hasattr(o.apps, appname):
            app = getattr(o.apps, appname)
            if hasattr(app, actorname):
                return getattr(app, actorname)
        return self.client.getActor(appname, actorname)


    def listdir(self, path):
        print "list for rootfilesystemlist: '%s' '%s'" % (self.cwd, path)
        parts = self.cwd.split('/')
        dirs = []
        if not self.cwd:
            dirs = [ x.split('__')[0] for x in self.actors ]
        elif len(parts) == 1:
            dirs = [ x.split('__')[1] for x in self.actors if x.startswith(self.cwd) ]
        elif len(parts) == 2:
            print '***** %s' % parts
            actor = self._getActorClient(*parts)
            if hasattr(actor, 'models'):
                dirs = [ x[0] for x in inspect.getmembers(getattr(actor, 'models')) if not x[0].startswith('_') ]
        elif len(parts) == 3:
            actor = self._getActorClient(*parts[0:2])
            methodname = "model_%s_list" % parts[2]
            dirs = [ "%s.json" %x for x in getattr(actor, methodname)() ]
        return list(set(dirs))

    def chdir(self, ftppath):
        print "chdirrootfslist:%s" % ftppath
        return
        self.cwd=self._removeFtproot(ftppath)

    def mkdir(self, path):
        return

    def rmdir(self, path):
        return

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
        tdir = "drwxr-xr-x    3 ftp      ftp          4096 Dec 04 05:52 %s\r\n"
        tfile = "-rwxr-xr-x    3 ftp      ftp          4096 Dec 04 05:52 %s\r\n"
        for basename in listing:
            if basename.endswith('.json') or basename.endswith('.hrd'):
                yield tfile % basename
            else:
                yield tdir % basename


    def format_mlsx(self, basedir, listing, perms, facts, ignore_err=True):
        tdir = "type=dir;perm=flcdmpe;size=4096;modify=20071103093626;unix.mode=0755;unix.uid=1002;unix.gid=1002;unique=801e32; %s\r\n"
        tfile = "type=file;perm=flcdmpe;size=4096;modify=20071103093626;unix.mode=0755;unix.uid=1002;unix.gid=1002;unique=801e32; %s\r\n"
        for basename in listing:
            if basename.endswith('.json') or basename.endswith('.hrd'):
                yield tfile % basename
            else:
                yield tdir % basename

    def openfile(self, filename, mode):
        return None

