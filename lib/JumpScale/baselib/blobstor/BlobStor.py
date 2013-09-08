from JumpScale import j
from JumpScale.core.baseclasses import BaseEnumeration
from BlobStorConfigManagement import BlobStorConfigManagement

class BlobType(BaseEnumeration):
    """
    Blob type
    """

    def __init__(self, value=None):
        self.value = value

    @classmethod
    def _initItems(cls):
        cls.registerItem('log')
        cls.registerItem('varia')
        cls.registerItem('jpackage')
        cls.finishItemRegistration()


class BlobStor:
    """
    generic usable storage system for larger blobs =  a blob is e.g. a file or a directory (which is then compressed)
    """

    def __init__(self, name):
        config = BlobStorConfigManagement()
        
        if name not in config.list():
            raise RuntimeError("Cannot find blobstor connection with name %s" % name)
        else:
            configitem = config.getConfig(name)
        self.config = configitem
        self.namespace = self.config["namespace"]
        self.name = name

    def _getDestination(self, destproto=None):
        if not destproto:
            destproto = ('http', 'ftp')
        if self.config["type"] == "local":
            return 'file://' + self.config["localpath"] + "/%s/" % self.namespace
        else:
            uri = ""
            for proto in destproto:
                if self.config.get(proto, "").strip() != "":
                    uri = self.config[proto]
                    break
            if uri == "":
                raise ValueError("No ftp or http url properly configured as remote blobstor")
            if uri[-1] == "/":
                uri = uri[:-1]
            return uri + "/%s/" % self.namespace

    def exists(self, key):
        """
        Checks if the blobstor contains an entry for the given key

        @param key: key to
        @type key: string
        """

        targetDirPath = j.system.fs.joinPaths(self._getDestination(), key[0:2], key[2:4])

        try:
            resultMeta = j.cloud.system.fs.sourcePathExists(j.system.fs.joinPaths(targetDirPath, '%(key)s.meta' % {'key': key}))
            resultGz = j.cloud.system.fs.sourcePathExists(j.system.fs.joinPaths(targetDirPath, '%(key)s.gz' % {'key': key})) or \
                     j.cloud.system.fs.sourcePathExists(j.system.fs.joinPaths(targetDirPath, '%(key)s.tgz' % {'key': key}))
        except Exception, e:
            j.console.echo("Error in cloudsystem: %s" % e)
            raise RuntimeError("Could not check existence of key %s in blobstor %s in namespace %s, there was error.\n%s" % (key, self.name, self.namespace, e))
        return resultMeta and resultGz

    def getMetadata(self, key):
        if self.exists(key):
            targetDirName = j.system.fs.joinPaths(self._getDestination(), key[0:2], key[2:4])
            targetFileNameMeta = j.system.fs.joinPaths(targetDirName, key + ".meta")
            content = j.cloud.system.fs.fileGetContents(targetFileNameMeta)
            metadata = BlobMetadata(content, key)
            return metadata
        else:
            raise RuntimeError("Cannot find %s on storagesystem" % key)

    def download(self, key, destination):
        self._download(key, destination, uncompress=True, keepTempFile=False)

    def _download(self, key, destination, uncompress=True, keepTempFile=False):
        metadata = self.getMetadata(key)
        filetype = metadata.filetype
        hashh = metadata.hash
        targetDirName = j.system.fs.joinPaths(self._getDestination(), hashh[0:2], hashh[2:4])
        if metadata.filetype == "file":
            targetFileNameTgz = j.system.fs.joinPaths(targetDirName, hashh + ".gz")
        else:
            targetFileNameTgz = j.system.fs.joinPaths(targetDirName, hashh + ".tgz")

        source = ""

        downloading = True
        counter = 0
        while downloading:
            if counter > 0:
                j.console.echo("Could not download %s, %s try" % (key, counter))
            counter += 1
            if counter > 5:
                raise RuntimeError("Could not download %s, have tried 5 times, could be file is corrupt" % source)

            if self.config['type'] == 'local':
                # when blobstore type is local, don't copy the tgz file, that would be a waste of resources
                tmpfile = targetFileNameTgz[len('file://'):]
            else:
                tmpfile = j.system.fs.getTempFileName()
                #here we do the download
                j.cloud.system.fs.copyFile(targetFileNameTgz, 'file://' + tmpfile)

            hashFromCompressed = j.tools.hash.md5(tmpfile)
            if metadata.md5 == hashFromCompressed:
                downloading = False
        if uncompress:
            if filetype == "file":
                j.system.fs.gunzip(tmpfile, destination)
            else:
                j.system.fs.targzUncompress(tmpfile, destination, removeDestinationdir=True)

        if keepTempFile == False:
            # when blobstore type is remote, clean up temporary file
            if self.config['type'] == 'remote':
                j.system.fs.removeFile(tmpfile)
        else:
            return tmpfile, metadata

    def checkIdentical(self, key, destination):
        """
        return True if destination is still same as on blobsystem
        else False
        """
        metadata = self.getMetadata(key)
        filetype = metadata.filetype
        if filetype == "file":
            hashh = j.tools.hash.md5(destination)
        else:
            hashh, filesdescr = j.tools.hash.hashDir(destination)
        return metadata.hash == hashh

    def copyToOtherBlocStor(self, key, blobstor):
        if True or not blobstor.exists(key):
            tmpfile, metadata = self._download(key, destination="", uncompress=False, keepTempFile=True)
            self._put(blobstor, metadata, tmpfile)
            if not self.config['type'] == 'local':
                j.system.fs.remove(tmpfile)
        else:
            j.logger.log("No need to download %s to blobstor, because is already there" % key, 6)

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
            j.cloud.system.fs.copyFile('file://' + tmpfile, targetFileNameTgz)
        j.cloud.system.fs.writeFile(targetFileNameMeta, metadata.content)

    def put(self, path, type="", expiration=0, tags="", blobstores=[], prevkey=None):
        """
        put file or directory to blobstor
        @param expiration in hours
        @param type see: j.enumerators.BlobType....
        """

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
        descr += "agentid=%s\n" % j.application.agentid
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

        #if hashh==prevkey or self.exists(hashh):
        if self.exists(hashh):
            j.console.echo("No need to upload to blobstor:%s, have already done so." % self.namespace)
            #return hashh,descr,anyPutDone
        else:
            self._put(self, metadata, tmpfile)
            anyPutDone = True
            j.logger.log('Successfully uploaded blob: ' + path)

        for blobstor in blobstores:
            if blobstor.exists(hashh):
                j.console.echo("No need to upload to blobstor:%s, have already done so." % blobstor.namespace)
            else:
                self._put(blobstor, metadata, tmpfile)
                anyPutDone = True
                j.logger.log('Successfully uploaded blob: ' + path)

        j.system.fs.remove(tmpfile)
        return hashh, descr, anyPutDone


class BlobMetadata():
    def __init__(self, content, hash):
        self.paths = []
        self.content = content
        self.hash = hash
        state = "start"
        for line in content.split("\n"):
            if state == "filedescr":
                if line.strip() != "":
                    splitted = line.split("|")
                    self.paths.append([splitted[0], "|".join(splitted[1:])])
            if line.find("============") != -1:
                state = "filedescr"
            if state == "start":
                splitted = line.split("=")
                param = splitted[0].strip().lower()
                value = "|".join(splitted[1:]).strip()
                self.__dict__[param] = value


class BlobStorFactory:
    def get(self, name=""):
        return BlobStor(name)

    def parse(self, path):
        """
        Parse a blobstor description file

        @param path: location of the description file
        @type path: string
        @return: parsed description
        @rtype: BlobDescription
        """
        with open(path, 'r') as f:
            rawDescription = f.read()
        description = BlobMetadata(rawDescription, None)
        return description
