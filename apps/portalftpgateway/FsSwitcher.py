
from JumpScale import j

from FilesystemVirtualRoot import FilesystemVirtualRoot
from OsisList import OsisList
from FilesystemReal import FilesystemReal
from FilesystemVirtualRootList import FilesystemVirtualRootList
from FilesystemDD import FilesystemDD


class FsSwitcher():

    def __init__(self, contentmanager, filemgr, client):
        self.spaces = {}
        self.buckets = {}
        self.actors = {}
        self.contentdirs = {}
        self.lastRoot = ""
        self.contentmanager = contentmanager
        self.filemanager = filemgr
        self.client = client
        self.getActors()
        self.getSpaces()
        self.getBuckets()
        self.getContentDirs()

        self.fs = {}

    def getContentDirs(self):
        result = self.contentmanager.getContentDirsWithPaths()
        self.contentdirs = {}
        for name, path in result:
            name = str(name)
            path = str(path)
            self.contentdirs[name] = path
        return self.contentdirs

    def getSpaces(self):
        result = self.contentmanager.getSpacesWithPaths()
        self.spaces = {}
        for name, path in result:
            name = str(name)
            path = str(path)
            self.spaces[name] = path
        return self.spaces

    def getBuckets(self):
        self.buckets = {}
        result = self.contentmanager.getBucketsWithPaths()
        for name, path in result:
            name = str(name)
            path = str(path)
            self.buckets[name] = path
        return self.buckets

    def getActors(self):
        self.actors = {}
        result = self.contentmanager.getActorsWithPaths()
        for name, path in result:
            name = str(name)
            path = str(path)
            self.actors[name] = path
        return self.actors

    def getFs(self, path, cmd_channel):

        if path == "" or path == "/" or path.find("/..") == 0:
            return FilesystemVirtualRoot(cmd_channel)

        ids = path.strip("/").split("/")
        key = "__".join(ids[0:2])

        # print "# GETFS:%s" % key

        # cache
        if key in self.fs:
            # print "cache:%s"%key
            fs = self.fs[key]
        else:

            # detect type
            ttype = ids[0]
            fs = None

            # if ttype=="megafs":
            #     fs= FilesystemDD("/generic",cmd_channel,"/megafs",self.filemanager)
            #     self.fs[key]=fs
            #     return fs

            if ttype in ["spaces", "buckets", "actors", "contentdirs", "osis"]:
                if len(ids) == 1:
                    name = ""
                else:
                    name = ids[1]

                if ttype == "osis":
                    fs = OsisList(cmd_channel, self.client)
                elif name == "":
                    # root of spaces,actors or buckets
                    if ttype == "spaces":
                        fs = FilesystemVirtualRootList(cmd_channel, self.getSpaces, ttype, self.contentmanager)
                    elif ttype == "actors":
                        fs = FilesystemVirtualRootList(cmd_channel, self.getActors, ttype, self.contentmanager)
                    elif ttype == "buckets":
                        fs = FilesystemVirtualRootList(cmd_channel, self.getBuckets, ttype, self.contentmanager)
                    elif ttype == "contentdirs":
                        fs = FilesystemVirtualRootList(cmd_channel, self.getContentDirs, ttype, self.contentmanager)
                else:
                    ftproot = "/" + "/".join(ids[0:2])
                    rpath = None
                    if ttype == "spaces":
                        if name in self.spaces:
                            rpath = self.spaces[name]
                    elif ttype == "actors":
                        if name in self.actors:
                            rpath = self.actors[name]
                    elif ttype == "buckets":
                        if name in self.buckets:
                            rpath = self.buckets[name]
                    elif ttype == "contentdirs":
                        if name in self.contentdirs:
                            rpath = self.contentdirs[name]
                    # real root of special filesystem
                    if rpath:
                        fs = FilesystemReal(rpath, cmd_channel, ftproot=ftproot, readonly=False, name=name,
                                            ttype=ttype, contentmanager=self.contentmanager)

            # if path.find("/stor")==0:
            #     fs= FilesystemReal(STORPATH,cmd_channel,ftproot="/stor",readonly=False,name=name,\
            #         ttype=ttype,contentmanager=self.contentmanager)

            if fs == None:
                return None

            self.fs[key] = fs

        # check
        # if path.find(fs.ftproot)<>0:
        #     raise RuntimeError("ftproot '%s' should be in path where we chdir to '%s'"%(fs.ftproot,path))

        # set cwd
        fs.cwd = fs._removeFtproot(path)
        print "##FSSW: CWD '%s'" % fs.cwd

        return self.fs[key]
