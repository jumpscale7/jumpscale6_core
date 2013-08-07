
from FilesystemBase import FilesystemBase

from OpenWizzy import o
from OpenWizzy.baselib import serializers
import os
import errno
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
        try:
            return self.client.getActor(appname, actorname)
        except:
            raise OSError(errno.ENOENT, "Not existing")


    def listdir(self, path):
        print "list for rootfilesystemlist: '%s' '%s'" % (self.cwd, path)
        parts = [ x for x in os.path.join(self.cwd, path).split('/') if x ] #strip empty parts
        return self._listdir(parts)

    def _listdir(self, parts):
        dirs = []
        if not parts:
            dirs = [ x.split('__')[0] for x in self.actors ]
        elif len(parts) == 1:
            dirs = [ x.split('__')[1] for x in self.actors if x.startswith(parts[0]) ]
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

    def chdir(self, path):
        path = path.replace(self.ftproot, '', 1)
        parts = [ x for x in path.split('/') if x ] #strip empty parts
        dirs = self._listdir(parts[:-1])
        if parts and parts[-1] not in dirs:
            raise OSError(errno.ENOENT, "Could not change to not existing path")
        return

    def mkdir(self, path):
        return

    def rmdir(self, path):
        return

    def _getActorMethod(self, parts, method):
        if len(parts) < 3:
            raise ValueError('Invalid path')
        actor = self._getActorClient(*parts[0:2])
        methodname = "model_%s_%s" % (parts[2], method)
        return getattr(actor, methodname)

    def _getParts(self, path):
        return o.system.fs.joinPaths(self.cwd, path).split('/')

    def _getObject(self, path):
        parts = self._getParts(path)
        method = self._getActorMethod(parts, 'get')
        oid = os.path.splitext(parts[3])[0]
        return method(oid)

    def ftp2fs(self, path, retrieve=True):
        parts = self._getParts(path)
        tmpdir = o.system.fs.joinPaths(o.dirs.tmpDir, *parts[0:-1])
        o.system.fs.createDir(tmpdir)
        tmpfile = o.system.fs.joinPaths(tmpdir, parts[-1])
        if retrieve:
            try:
                obj = self._getObject(path)
            except:
                return tmpfile
            dumped = o.db.serializers.hrd.dumps(obj)
            with open(tmpfile, 'w+') as fd:
                fd.write(dumped)
        return tmpfile

    def fs2ftp(self, path):
        return path[len(o.dirs.tmpDir):]

    def remove(self, path):
        parts = self._getParts(path)
        oid = os.path.splitext(parts[-1])[0]
        method = self._getActorMethod(parts, 'delete')
        method(oid)

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
        fpath = self.ftp2fs(filename)
        return open(fpath, mode)

    def on_file_sent(self,path):
        pass

    def on_file_received(self, fpath):
        path = self.fs2ftp(fpath)
        parts = self._getParts(path)[1:]
        method = self._getActorMethod(parts, 'set')
        content = o.db.serializers.hrd.loads(o.system.fs.fileGetContents(fpath))
        method(content)
