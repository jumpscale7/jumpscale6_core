from JumpScale import j

import JumpScale.baselib.gitlab
import JumpScale.baselib.blobstor2

class Item():
    def __init__(self,data=""):
        state="start"
        self.hash=""
        self.text=""
        self.size=""
        if data<>"":
            for line in data.split("\n"):
                if line.strip()=="" or line[0]=="#":
                    continue
                if line.find("####")<>-1:
                    state="text"
                    continue
                if state=="start":
                    key,value=line.split(":")
                    self.__dict__[key.strip()]=value.strip()
                if state=="text":
                    self.text+="%s\n"%line

    def __repr__(self):
        out=""
        for key,value in self.__dict__.iteritems():
            if key<>"text":
                out+="%s:%s\n"%(key,value)
        out+="####\n"
        out+=self.text
        return out

    __str__=__repr__

class JSFileMgr():
    def __init__(self, MDPath, cachePath="",namespace="backup",blobclientname="default"):
        self.errors=[]
        self._MB4=1024*1024*4 #4Mbyte
        self.excludes=["*.pyc"]

        self.MDPath = MDPath

        if cachePath=="":
            cachePath="/opt/backup/CACHE"

        self.cachePath = cachePath  # Intermediate link path!

        # Local blob STOR
        self.STORpath="/opt/backup/STOR"

        passwd = j.application.config.get('grid.master.superadminpasswd')
        login="root"
        # blobstor2 client
        self.client = j.servers.zdaemon.getZDaemonClient("127.0.0.1",port=2345,user=login,passwd=passwd,ssl=False,sendformat='m', returnformat='m',category="blobserver")
        self.client=j.clients.blobstor2.getClient(namespace=namespace, name=blobclientname)

    def _normalize(self, path):
        path=path.replace("'","\\'")
        path=path.replace("[","\\[")
        path=path.replace("]","\\]")
        return path

    def action_link(self, src, dest):
        #DO NOT IMPLEMENT YET
        j.system.fs.createDir(j.system.fs.getDirName(dest))
        print "link:%s %s"%(src, dest)

        if j.system.fs.exists(path=dest):
            stat=j.system.fs.statPath(dest)
            if stat.st_nlink<2:
                raise RuntimeError("only support linked files")
        else:
            cmd="ln '%s' '%s'"%(self._normalize(src),self._normalize(dest))
            try:
                j.system.process.execute(cmd)
            except Exception,e:
                print "ERROR",
                print cmd
                print e
                self.errors.append(["link",cmd,e])

    def _dump2stor(self, namespace, data, compress=True):
        if len(data)==0:
            return ""

        datahash = j.tools.hash.md5_string(data)
        data2 = lzma.compress(data) if compress else data
        if not self.client.exists(namespace, datahash):
            self.client.set(namespace, datahash, data2)

        return datahash

    def _read_file(self,path, block_size=0):
        if block_size==0:
            block_size=self._MB4

        with open(path, 'rb') as f:
            while True:
                piece = f.read(block_size)
                if piece:
                    yield piece
                else:
                    return

    def _action_backup(self, src, dest, namespace):
        j.system.fs.createDir(j.system.fs.getDirName(dest))
        print "backup:%s %s"%(src,dest)
        # j.system.fs.hardlinkFile(srcfull2,dest)
        if j.system.fs.exists(path=dest):
            stat=j.system.fs.statPath(dest)
            if not stat.st_nlink==1:
                raise RuntimeError("cannot be backed up")
        item=Item()
        item.hash=j.tools.hash.md5(src)

        stat=j.system.fs.statPath(src)

        item.size=stat.st_size
        item.mode=stat.st_mode
        item.uid=stat.st_uid
        item.gid=stat.st_gid
        item.atime=stat.st_atime
        item.ctime=stat.st_ctime
        item.mtime=stat.st_mtime

        hashes=[]

        for data in self._read_file(src):
            hashes.append(self._dump2stor(namespace, data))

        if len(hashes)>1:
            out = "##HASHLIST##\n"
            hashparts = "\n".join(hashes)
            out += hashparts
            # Store in blobstor
            out_hash = self._dump2stor(namespace, out, compress=False)

            # The meta data part, this is how we will get this hash list!
            item.hashlist = out_hash
        else:
            if len(hashes)==0 or hashes[0]=="":
                item.hash=""

        j.system.fs.writeFile(dest, str(item))

    def restore(self, src, dest, namespace):
        """
        src is location on metadata dir
        dest is where to restore to
        """

        if src[0] != "/":
            src = "%s/%s" % (self.MDPath, src.strip())

        if not j.system.fs.exists(path=src):
            raise RuntimeError("Could not find source (on mdstore)")

        for item in j.system.fs.listFilesInDir(src, True):
            destpart=j.system.fs.pathRemoveDirPart(item, src, True)
            destfull=j.system.fs.joinPaths(dest, destpart)

            self.restore1file(item, destfull, namespace)

    def restore1file(self, src, dest, namespace):

        print "restore: %s %s" % (src, dest)

        itemObj=Item(j.system.fs.fileGetContents(src))

        j.system.fs.createDir(j.system.fs.getDirName(dest))

        if itemObj.hash.strip()=="":
            j.system.fs.writeFile(dest,"")
            return

        blob_path = self._getBlobPath(namespace, itemObj.hash)
        if j.system.fs.exists(blob_path):
            # Blob exists in cache, we can get it from there!
            print "Blob FOUND in cache: %s" % blob_path
            j.system.fs.copyFile(blob_path, dest)
            return

        # Get the file directly or get the blob storing the hashes of file parts!
        blob_hash = itemObj.hashlist if hasattr(itemObj, "hashlist") else itemObj.hash

        # Get blob from blobstor2
        blob = self.client.get(namespace, blob_hash)

        # Write the blob
        self._writeBlob(dest, blob, itemObj, namespace)

    def _writeBlob(self, dest, blob, item, namespace):
        """
        Write blob to destination
        """

        check="##HASHLIST##"
        if blob.find(check)==0:
            # found hashlist
            print "FOUND HASHLIST %s" % blob
            hashlist = blob[len(check) + 1:]
            j.system.fs.writeFile(dest,"")
            for hashitem in hashlist.split("\n"):
                if hashitem.strip() != "":
                    blob_block = self.client.get(namespace, hashitem)
                    data = lzma.decompress(blob_block)
                    j.system.fs.writeFile(dest, data, append=True)
        else:
            # content is there
            data = lzma.decompress(blob)
            j.system.fs.writeFile(dest, data)

        # chmod/chown
        os.chmod(dest,int(item.mode))
        os.chown(dest,int(item.uid),int(item.gid))

    def backupRecipe(self,recipe):
        """
        walk over recipe & execute action on it
        example recipe


        #when star will do for each dir
        /tmp/JSAPPS/apps : * : /DEST/apps
        #when no * then dir & below
        /tmp/JSAPPS/bin :  : /DEST/bin
        #now only for 1 subdir
        /tmp/JSAPPS/apps : asubdirOfApps : /DEST/apps

        """

        action=self._action_backup

        def do(sourcedir, parts, dest, namespace, action):
            """
            read recipe & process
            """
            sourcedir=sourcedir.strip()
            dest=dest.strip()

            if parts.find("*")<>-1:
                parts=",".join(j.system.fs.listDirsInDir(sourcedir, recursive=False, dirNameOnly=True, findDirectorySymlinks=True))

            for sourcepart in parts.split(","):
                sourcepart=sourcepart.strip()
                srcfull=j.system.fs.joinPaths(sourcedir,sourcepart)
                if not j.system.fs.exists(path=srcfull):
                    raise RuntimeError("Could not find %s"%srcfull)

                for item in j.system.fs.listFilesInDir(srcfull,True,exclude=self.excludes):
                    destpart=j.system.fs.pathRemoveDirPart(item,sourcedir,True)
                    srcpart2=j.system.fs.pathRemoveDirPart(item,srcfull,True)
                    destfull=j.system.fs.joinPaths(dest,destpart)
                    srcfull2=j.system.fs.joinPaths(srcfull,srcpart2)

                    action(srcfull2,destfull, namespace)

        for line in recipe.split("\n"):
            if line.strip()=="" or line[0]=="#":
                continue
            source, sourceparts, namespace, dest=line.split(":")

            # namespace in blobstor
            namespace = namespace.strip()

            if dest[0]<>"/":
                dest="%s/%s"%(self.MDPath,dest.strip())

            do(source, sourceparts, dest, namespace, action)

        if len(self.errors)>0:
            print "#############ERRORS###################"
            print "\n".join(errors)

    def _getBlobPath(self, namespace, key):
        """
        Get the blob path in Cache dir
        """
        # Get the Intermediate path of a certain blob
        storpath = j.system.fs.joinPaths(self.cachePath, namespace, key[0:2], key[2:4], key)
        return storpath

    def _getBlob(self, src, namespace):
        """
        Retrieves the blobs in Cache path
        """

        # Create the Item Object
        itemObj = Item(j.system.fs.fileGetContents(src))

        blob_hash = itemObj.hashlist if hasattr(itemObj, "hashlist") else itemObj.hash

        # Get blob from blobstor2
        blob = self.client.get(namespace, blob_hash)

        # The path which this blob should be saved
        blob_path = self._getBlobPath(namespace, itemObj.hash)
        j.system.fs.createDir(j.system.fs.getDirName(blob_path))

        self._writeBlob(blob_path, blob, itemObj, namespace)

        return blob_path

    def linkRecipe(self, src, dest, namespace):
        """
        Hardlink Recipe from Cache Dir
        """

        if not self.cachePath:
            raise RuntimeError("Link Path is not Set!")

        if src[0] != "/":
            src = "%s/%s" % (self.MDPath, src.strip())

        if not j.system.fs.exists(path=src):
            raise RuntimeError("Could not find source (on mdstore)")

        for item in j.system.fs.listFilesInDir(src, True):
            # Retrieve blob & blob_path in intermediate location
            blob_path = self._getBlob(item, namespace)

            # the hardlink destination
            destpart = j.system.fs.pathRemoveDirPart(item, src, True)
            destfull = j.system.fs.joinPaths(dest, destpart)

            # Now, make the link
            self.action_link(blob_path, destfull)

class BackupClient:
    """
    """

    def __init__(self,blobclientName,gitlabName="incubaid" ):
        self.blobclientName=blobclientName
        self.gitlabName=gitlabName        
        self.gitlab=j.clients.gitlab.get(gitlabName)


    def backupRecipe(self,recipe):
        """
        do backup of sources as specified in recipe
        example recipe

        #when star will do for each dir
        /tmp/JSAPPS/apps : * : /DEST/apps
        #when no * then dir & below
        /tmp/JSAPPS/bin :  : /DEST/bin
        #now only for 1 subdir
        /tmp/JSAPPS/apps : asubdirOfApps : /DEST/apps

        """
        from IPython import embed
        print "DEBUG NOW backupRecipe"
        embed()
        
        JSFileMgr()