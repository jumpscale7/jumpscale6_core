from store import KeyValueStoreBase
from OpenWizzy import o
import os

class FileSystemKeyValueStore(KeyValueStoreBase):
    EXTENSION = ""


    def __init__(self, namespace="", baseDir=None, serializers=None):

        KeyValueStoreBase.__init__(self, serializers)

        if not baseDir:
            baseDir = o.system.fs.joinPaths(o.dirs.varDir, 'db')

        #self.id = o.application.getUniqueMachineId()
        self.dbpath = o.system.fs.joinPaths(baseDir,namespace)

        #if not o.system.fs.exists(self.dbpath):
            #o.system.fs.createDir(self.dbpath)

    def fileGetContents(self,filename):
        fp = open(filename,"r")
        data = fp.read()
        fp.close()
        return data

    def writeFile(self,filename, contents):
        """
        Open a file and write file contents, close file afterwards
        @param contents: string (file contents to be written)
        """
        fp = open(filename,"wb")
        fp.write(contents)  #@todo P1 will this also raise an error and not be catched by the finally
        fp.close()


    def get(self, category, key):
        # self._assertExists(category, key)
        storePath = self._getStorePath(category, key)
        if not os.path.exists(storePath):
            raise RuntimeError("Could not find key:'%s'"%key)

        value = self.fileGetContents(storePath)
        return self.unserialize(value)

    def set(self, category, key, value):

        storePath = self._getStorePath(category, key,True)
        self.writeFile(storePath,self.serialize(value))

    def destroy(self,category=""):
        if category<>"":
            categoryDir = self._getCategoryDir(category)
            o.system.fs.removeDirTree(categoryDir)
        else:
            o.system.fs.removeDirTree(self.dbpath)

    def delete(self, category, key):
        #self._assertExists(category, key)

        if self.exists(category, key):
            storePath = self._getStorePath(category, key)
            o.system.fs.removeFile(storePath)

            # Remove all empty directories up to the base of the store being the
            # directory with the store name (4 deep).
            # Path: /<store name>/<namespace>/<category>/<key[0:2]>/<key[2:4]/

            depth = 4
            parentDir = storePath

            while depth > 0:
                parentDir = o.system.fs.getParent(parentDir)

                if o.system.fs.isEmptyDir(parentDir):
                    o.system.fs.removeDir(parentDir)

                depth -= 1

    def exists(self, category, key):
        return os.path.exists(self._getStorePath(category, key))

    def list(self, category, prefix=None):
        if not self._categoryExists(category):
            return []
        categoryDir = self._getCategoryDir(category)
        filePaths = o.system.fs.listFilesInDir(categoryDir, recursive=True)
        fileNames = [o.system.fs.getBaseName(path) for path in filePaths]

        if prefix:
            fileNames = [name for name in fileNames if name.startswith(prefix)]

        return fileNames

    def listCategories(self):
        return o.system.fs.listDirsInDir(self.dbpath, dirNameOnly=True)

    def _categoryExists(self, category):
        categoryDir = self._getCategoryDir(category)
        return o.system.fs.exists(categoryDir)

    def _getCategoryDir(self, category):
        return o.system.fs.joinPaths(self.dbpath, category)

    def _getStorePath(self, category, key,createIfNeeded=True):
        key = str(key)
        origkey = key
        if len(key)<4:
            key = key + (4 - len(key)) * '_'

        ddir=self.dbpath+"/"+category+"/"+key[0:2]+"/"+key[2:4]

        if createIfNeeded and not os.path.exists(ddir):
            os.makedirs(ddir)

        return ddir + "/" + origkey + self.EXTENSION

