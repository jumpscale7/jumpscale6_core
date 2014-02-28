from JumpScale import j
import lzma
import JumpScale.baselib.gitlab
import JumpScale.baselib.blobstor2

class Item():
    def __init__(self,data=""):
        state="start"
        self.hash=""
        self.text=""
        self.size=""
        self.mtime=0

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
        # self.client = j.servers.zdaemon.getZDaemonClient("127.0.0.1",port=2345,user=login,passwd=passwd,ssl=False,sendformat='m', returnformat='m',category="blobserver")
        self.client=j.clients.blobstor2.getClient(namespace=namespace, name=blobclientname)
        self.namespace=namespace
        self.repoId=1 # will be implemented later with osis
        self.compress=False
        self.errors=[]

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

    def _dump2stor(self, data):
        if len(data)==0:
            return ""

        datahash = j.tools.hash.md5_string(data)
        data2 = lzma.compress(data) if self.compress else data
        if not self.client.exists(key=datahash,repoId=self.repoId):
            self.client.set(key=datahash, data=data2,repoId=self.repoId)
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

    def doError(self,path,msg):
        self.errors.append([path,msg])

    def _handleMetadata(self, path,prefix,ttype,linkdest=None,MD5=True):
        """
        @return (mdchange,contentchange) True if changed, False if not
        """
        print "MD:%s "%path,

        srcpart=j.system.fs.pathRemoveDirPart(path,prefix,True)                        
        dest=j.system.fs.joinPaths(self.MDPath,"MD",srcpart)

        try:
            stat=j.system.fs.statPath(path)
        except Exception,e:
            if not j.system.fs.exists(path):
                #can be link which does not exist
                #or can be file which is deleted in mean time
                self.doError(path,"could not find, so could not backup.") 
                return (False,False)

        #next goes for all types
        if j.system.fs.exists(path=dest):
            item=self.getMDObjectFromFs(dest)
            change=False
            mdchange=False
        else:
            j.system.fs.createDir(j.system.fs.getDirName(dest))
            item=Item()
            change=True
            mdchange=True

        if ttype=="F":          
            if item.mtime<>stat.st_mtime or item.size<>stat.st_size:
                if MD5:
                    newMD5=j.tools.hash.md5(path)
                    if item.hash<>newMD5:
                        change=True
                        mdchange=True
                        item.hash=newMD5
                else:
                    change=True
                    mdchange=True
        elif ttype=="L":
            if not item.__dict__.has_key("dest"):
                mdchange=True                
            elif linkdest<>item.dest:
                mdchange=True

        if mdchange==False:
            #check metadata changed based on mode, uid, gid & mtime
            if item.mtime<>stat.st_mtime or item.mode<>stat.st_mode or\
                    item.uid<>stat.st_uid or item.gid<>stat.st_gid or item.size<>stat.st_size:
                mdchange=True

        if mdchange:
            print "MDCHANGE"
            item.mode=stat.st_mode
            item.uid=stat.st_uid
            item.gid=stat.st_gid
            # item.atime=stat.st_atime
            item.ctime=stat.st_ctime
            item.mtime=stat.st_mtime            

            if ttype=="F":
                item.size=stat.st_size
                item.type="F"
            elif ttype=="D":
                item.type="D"
                dest=j.system.fs.joinPaths(self.MDPath,"dirs",srcpart,".meta")
                j.system.fs.createDir(j.system.fs.getDirName(dest))
            elif ttype=="L":                
                item.dest=linkdest
                if j.system.fs.isDir(path):
                    dest=j.system.fs.joinPaths(self.MDPath,"links",srcpart,".meta")
                    item.type="LD"
                else:
                    dest=j.system.fs.joinPaths(self.MDPath,"links",srcpart)
                    item.type="LF"
                j.system.fs.createDir(j.system.fs.getDirName(dest))

            j.system.fs.writeFile(dest, str(item))

        return (mdchange,change)

    def restore(self, src, dest, namespace):
        """
        src is location on metadata dir
        dest is where to restore to
        """
        self.errors=[]

        if src[0] != "/":
            src = "%s/%s" % (self.MDPath, src.strip())

        if not j.system.fs.exists(path=src):
            raise RuntimeError("Could not find source (on mdstore)")

        for item in j.system.fs.listFilesInDir(src, True):
            destpart=j.system.fs.pathRemoveDirPart(item, src, True)
            destfull=j.system.fs.joinPaths(dest, destpart)

            self.restore1file(item, destfull, namespace)

    def getMDObjectFromFs(self,path):
        itemObj=Item(j.system.fs.fileGetContents(path))
        return itemObj

    def restore1file(self, src, dest, namespace):

        print "restore: %s %s" % (src, dest)

        itemObj=self.getMDObjectFromFs(src)

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

    def backupBatch(self,batch):
        """
        batch is [[src,dest]]
        """
        key2paths={}            
        for src,dest in batch:
            key2paths[j.tools.hash.md5(src)]=(src,dest)
            self._storeMD(src,dest)

        notexist=self.client.existsBatch(keys=key2paths.keys()) 

        for notexistkey in notexist:
            src,dest=key2paths[notexistkey]

            hashes=[]
            if src[-4:]==".pyc":
                return
            for data in self._read_file(src):
                hashes.append(self._dump2stor(data))

            if len(hashes)>1:
                out = "##HASHLIST##\n"
                hashparts = "\n".join(hashes)
                out += hashparts
                # Store in blobstor
                out_hash = self._dump2stor(out)

                # The meta data part, this is how we will get this hash list!
                item.hashlist = out_hash
            else:
                if len(hashes)==0 or hashes[0]=="":
                    item.hash=""

    def backup(self,path,destination="", pathRegexIncludes={},pathRegexExcludes={".*\\.pyc"},childrenRegexExcludes=[".*/dev/.*",".*/proc/.*"]):

        #check if there is a dev dir, if so will do a special tar
        ##BACKUP:
        #tar Szcvf testDev.tgz saucy-amd64-base/rootfs/dev/
        ##restore
        #tar xzvf testDev.tgz -C testd

        self.errors=[]

        if j.system.fs.exists(j.system.fs.joinPaths(path,"dev")):
            cmd="cd %s;tar Szcvf __dev.tgz dev"%path
            j.system.process.execute(cmd)

        destClist=j.system.fs.joinPaths(self.STORpath, "../TMP","changes","%s.changes"%self.namespace)
        destFlist=j.system.fs.joinPaths(self.STORpath, "../TMP","changes","%s.found"%self.namespace)
        j.system.fs.createDir(j.system.fs.getDirName(destClist))
        j.system.fs.createDir(j.system.fs.getDirName(destFlist))
        changes = open(destClist, 'w')
        found = open(destFlist, 'w')

        w=j.base.fswalker.get()
        callbackMatchFunctions=w.getCallBackMatchFunctions(pathRegexIncludes,pathRegexExcludes,includeFolders=True,includeLinks=True)

        def processfile(path,stat,arg):
            self=arg["self"]
            prefix=arg["prefix"]
            changed=self._handleMetadata(path,prefix=prefix,ttype="F")
            if changed:
                arg["changes"].write("%s\n"%path)
            arg["found"].write("%s\n"%path)

        def processdir(path,stat,arg):
            self=arg["self"]
            prefix=arg["prefix"]
            changed=self._handleMetadata(path,prefix=prefix,ttype="D")
            if changed:
                arg["changes"].write("%s\n"%path)
            arg["found"].write("%s\n"%path)            

        def processlink(src,dest,stat,arg):
            path=src
            self=arg["self"]
            prefix=arg["prefix"]
            destpart=j.system.fs.pathRemoveDirPart(dest,prefix,True)                                   
            changed=self._handleMetadata(path,prefix=prefix,ttype="L",linkdest=destpart)
            if changed:
                arg["changes"].write("%s\n"%path)
            arg["found"].write("%s\n"%path)            

        callbackFunctions={}
        callbackFunctions["F"]=processfile
        callbackFunctions["D"]=processdir
        callbackFunctions["L"]=processlink            

        arg={}
        arg["self"]=self
        arg["prefix"]=path
        arg["changes"]=changes
        arg["found"]=found
        # arg["destination"]=destination
        # arg["batch"]=[]
        w.walk(path,callbackFunctions,arg=arg,callbackMatchFunctions=callbackMatchFunctions,childrenRegexExcludes=childrenRegexExcludes)

        changes.close()
        found.close()
        
        # self.backupBatch(arg["batch"])

        if len(self.errors)>0:
            out=""
            for path,msg in self.errors:
                out+="%s:%s\n"%(path,msg)
            j.system.fs.writeFile(j.system.fs.joinPaths(self.MDPath,destination,"ERRORS.LOG"),out)

    def createplist(self):

        destF=j.system.fs.joinPaths(self.STORpath, "../TMP","plists","F_%s.plist"%self.namespace)
        destL=j.system.fs.joinPaths(self.STORpath, "../TMP","plists","l_%s.plist"%self.namespace)
        destD=j.system.fs.joinPaths(self.STORpath, "../TMP","plists","D_%s.plist"%self.namespace)
        j.system.fs.createDir(j.system.fs.joinPaths(self.STORpath, "../TMP","plists"))
        fileF = open(destF, 'w')
        fileL = open(destL, 'w')
        fileD = open(destD, 'w')

        def processfile(path,stat,arg):
            path2=j.system.fs.pathRemoveDirPart(path, arg["base"], True)
            # print "%s  :   %s"%(path,path2)
            md=self.getMDObjectFromFs(path)
            fileF.write("%s|%s|%s|%s\n"%(path2,md.size,md.mtime,md.hash))

        def processlink(path,stat,arg):
            path2=j.system.fs.pathRemoveDirPart(path, arg["base"], True)
            # print "%s  :   %s"%(path,path2)
            md=self.getMDObjectFromFs(path)
            fileL.write("%s|%s\n"%(path2,md.dest))

        def processdir(path,stat,arg):
            path2=j.system.fs.pathRemoveDirPart(path, arg["base"], True)
            # print "%s  :   %s"%(path,path2)
            md=self.getMDObjectFromFs(path)
            fileD.write("%s\n"%(path))

        callbackFunctions={}
        callbackFunctions["F"]=processfile

        arg={}
        arg["base"]=self.MDPath
        w=j.base.fswalker.get()
        callbackFunctions["F"]=processfile
        if j.system.fs.exists(path=self.MDPath+"/md"):
            w.walk(self.MDPath+"/md",callbackFunctions,arg=arg,childrenRegexExcludes=[])
        callbackFunctions["F"]=processlink
        if j.system.fs.exists(path=self.MDPath+"/links"):
            w.walk(self.MDPath+"/links",callbackFunctions,arg=arg,childrenRegexExcludes=[])
        callbackFunctions["F"]=processdir
        if j.system.fs.exists(path=self.MDPath+"/dirs"):
            w.walk(self.MDPath+"/dirs",callbackFunctions,arg=arg,childrenRegexExcludes=[])

        fileF.close()
        fileL.close()
        fileD.close()

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
        blob = self.client.get(key=blob_hash)

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

    def __init__(self,backupname,blobclientName,gitlabName="incubaid"):
        self.blobclientName=blobclientName
        self.gitlabName=gitlabName        
        self.gitlab=j.clients.gitlab.get(gitlabName)
        self.backupname=backupname
        self.mdpath="/opt/backup/MD/%s"%backupname
        if not j.system.fs.exists(path=self.mdpath):    
            if not self.gitlab.existsProject(namespace=self.gitlab.loginName, name=backupname):
                self.gitlab.createproject(backupname, description='backup set', issues_enabled=0, wall_enabled=0, merge_requests_enabled=0, wiki_enabled=0, snippets_enabled=0, public=0)#, group=accountname)            
        self.gitclient = self.gitlab.getGitClient(self.gitlab.loginName, backupname, clean=False,path=self.mdpath)
            
        self.filemanager=JSFileMgr(MDPath=self.mdpath,namespace="backup",blobclientname=blobclientName)

    def backup(self,path,destination="", pathRegexIncludes={},pathRegexExcludes={},childrenRegexExcludes=[".*/dev/.*","/proc/.*"]):
        self._clean()
        self.filemanager.backup(path,destination=destination, pathRegexIncludes=pathRegexIncludes,pathRegexExcludes=pathRegexExcludes,childrenRegexExcludes=childrenRegexExcludes)
        self.commitMD()

    def createplist(self):
        self.filemanager.createplist()

    def _clean(self):
        for ddir in j.system.fs.listDirsInDir(self.mdpath,False,True,findDirectorySymlinks=False):
            if ddir.lower()<>".git":
                j.system.fs.removeDirTree(j.system.fs.joinPaths(self.mdpath,ddir))
        for ffile in j.system.fs.listFilesInDir(self.mdpath, recursive=False, followSymlinks=False):
            j.system.fs.remove(ffile)
        

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
        self._clean()
        self.filemanager.backupRecipe(recipe)
        self.commitMD()

    def commitMD(self):
        print "commit to git"
        self.gitclient.commit("backup %s"%j.base.time.getLocalTimeHRForFilesystem())
        if j.system.net.tcpPortConnectionTest(self.gitlab.addr,self.gitlab.port):
            #found gitlab
            print "push to git"
            self.gitclient.push()
        else:
            print "WARNING COULD NOT COMMIT CHANGES TO GITLAB, no connection found.\nDO THIS LATER!!!!!!!!!!!!!!!!!!!!!!"
