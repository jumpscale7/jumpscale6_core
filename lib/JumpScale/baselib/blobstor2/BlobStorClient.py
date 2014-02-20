from JumpScale import j

class BlobStorClient2:
    """
    generic usable storage system for larger blobs =  a blob is e.g. a file or a directory (which is then compressed)
    """

    def __init__(self, namespace,addr,port,login,passwd):
        self.namespace=namespace
        self.client= j.servers.zdaemon.getZDaemonClient(addr,port=port,user=login,passwd=passwd,ssl=False,sendformat='m', returnformat='m',category="blobserver")

    def exists(self, key, repoId=""):
        """
        Checks if the blobstor contains an entry for the given key
        @param key: key to
        """
        return self.client.exists(self.namespace, key, repoId=repoId)

    def getMD(self, key):
        return self.client.getMD(self.namespace, key)

    def delete(self, key, force=False,repoId=""):
        return self.client.delete(self.namespace, key, repoId=repoId, force=force)

    def set(self, key, data, repoId=""):
        """
        set 1 block of data, data is preformatted (e.g. compressed, encrypted, ...)
        """
        return self.client.set(self.namespace, key, data, repoId=repoId)

    def get(self, key):
        """
        get the block back
        """
        return self.client.get(self.namespace, key)

    def deleteNamespace(self):
        return self.client.deleteNamespace(self.namespace)


    def download(self, key, destination):
        pass

    def checkIdentical(self, key, destination):
        """
        return True if destination is still same as on blobsystem
        else False
        """
        raise RuntimeError("not implemented")
        metadata = self.getMetadata(key)
        filetype = metadata.filetype
        if filetype == "file":
            hashh = j.tools.hash.md5(destination)
        else:
            hashh, filesdescr = j.tools.hash.hashDir(destination)
        return metadata.hash == hashh

    def copyToOtherBlobStor(self, key, blobstor):
        raise RuntimeError("not implemented")
        if True or not blobstor.exists(key):
            tmpfile, metadata = self._download(key, destination="", uncompress=False, keepTempFile=True)
            self._put(blobstor, metadata, tmpfile)
            if not self.config['type'] == 'local':
                j.system.fs.remove(tmpfile)
        else:
            j.clients.blobstor.log("No need to download '%s' to blobstor, because is already there" % key, "download")

    def _put(self, blobstor, metadata, tmpfile):
        hashh = metadata.hash
        targetDirName = j.system.fs.joinPaths(blobstor._getDestination(('ftp',)), hashh[0:2], hashh[2:4])
        if metadata.filetype == "file":
            targetFileNameTgz = j.system.fs.joinPaths(targetDirName, hashh + ".gz")
        else:
            targetFileNameTgz = j.system.fs.joinPaths(targetDirName, hashh + ".tgz")
        targetFileNameMeta = j.system.fs.joinPaths(targetDirName, hashh + ".meta")

        if blobstor.config["type"] == "local":
            targetFileNameTgz = targetFileNameTgz.replace("file://", "")
            j.system.fs.createDir(j.system.fs.getDirName(targetFileNameTgz))
            j.system.fs.copyFile(tmpfile, targetFileNameTgz)
        else:
            #@todo P1 need to create the required dir (do directly with FTP)
            try:
                j.cloud.system.fs.copyFile('file://' + tmpfile, targetFileNameTgz)
            except Exception,e:
                if str(e).find("Failed to login on ftp server")<>-1:
                    if j.application.shellconfig.interactive:
                        j.console.echo("Could not login to FTP server for blobstor, please give your login details.")
                        login=j.console.askString("login")
                        passwd=j.console.askPassword("passwd", False)
                        config=j.config.getInifile("blobstor")
                        ftpurl=config.getValue(blobstor.name,"ftp")
                        if ftpurl.find("@")<>-1:
                            end=ftpurl.split("@")[1].strip()
                        else:
                            end=ftpurl.split("//")[1].strip()
                        ftpurl="ftp://%s:%s@%s"%(login,passwd,end)
                        config.setParam(blobstor.name,"ftp",ftpurl)
                        blobstor.loadConfig()
                        return self._put(blobstor, metadata, tmpfile)
                j.errorconditionhandler.processPythonExceptionObject(e)

        j.cloud.system.fs.writeFile(targetFileNameMeta, metadata.content)





    def put(self, path, type="", expiration=0, tags="", blobstors=[]):
        """
        put file or directory to blobstor
        @param expiration in hours
        """
        raise RuntimeError("not implemented")

        anyPutDone = False

        if not j.system.fs.exists(path):
            raise RuntimeError("Cannot find file %s" % path)
        if j.system.fs.isFile(path):
            filetype = "file"
        elif j.system.fs.isDir(path):
            filetype = "dir"
        else:
            raise RuntimeError("Cannot find file (exists but is not a file or dir) %s" % path)

        if filetype == "file":
            hashh = j.tools.hash.md5(path)
            filesdescr = ""
        else:
            hashh, filesdescr = j.tools.hash.hashDir(path)

        if hashh=="":
            #means empty dir
            return "", "", False

        j.clients.blobstor.log("Path:'%s' Hash:%s" % (path,hashh),category="upload",level=5)

        tmpfile = j.system.fs.getTempFileName()

        if filetype == "file":
            # @TODO: Check what realpath should be.
            #if not j.system.windows.checkFileToIgnore(realpath):
            #    j.system.fs.gzip(path, tmpfile)
            pass
        else:
            j.system.fs.targzCompress(path, tmpfile, followlinks=False)

        hashFromCompressed = j.tools.hash.md5(tmpfile)
        descr = ""
        descr += "whoami=%s\n" %  j.application.getWhoAmiStr()
        descr += "appname=%s\n" % j.application.appname
        descr += "tags=%s\n" % tags
        descr += "expiration=%s\n" % expiration
        descr += "type=%s\n" % type
        descr += "epochtime=%s\n" % j.base.time.getTimeEpoch()
        descr += "filepath=%s\n" % path
        descr += "filetype=%s\n" % filetype
        descr += "md5=%s\n" % hashFromCompressed
        descr += "\n"
        descr += "================================================================\n"
        descr += filesdescr + "\n"

        metadata = BlobMetadata(descr, hashh)

        if self.exists(hashh):
            j.clients.blobstor.log("No need to upload '%s' to blobstor:'%s/%s', have already done so." % (path,self.name,self.namespace),category="upload",level=5)

            #return hashh,descr,anyPutDone
        else:
            self._put(self, metadata, tmpfile)
            anyPutDone = True
            j.clients.blobstor.log('Successfully uploaded blob: ' + path,category="upload",level=5)

        for blobstor in blobstors:
            if blobstor.exists(hashh):
                j.clients.blobstor.log("No need to upload '%s' to blobstor:'%s/%s', have already done so." % (path,blobstor.name,self.namespace),category="upload",level=5)
            else:
                self._put(blobstor, metadata, tmpfile)
                anyPutDone = True
                j.clients.blobstor.log("Successfully uploaded '%s' to blobstor:'%s/%s'" % (path,blobstor.name,self.namespace) ,category="upload",level=5)

        j.system.fs.remove(tmpfile)
        return hashh, descr, anyPutDone
