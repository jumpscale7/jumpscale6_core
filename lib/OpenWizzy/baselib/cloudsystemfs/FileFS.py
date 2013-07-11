from OpenWizzy import o


# maybe this could be switched to http://curlftpfs.sourceforge.net/
class FileFS(object):
    path = None
    end_type = None
    local_file = None
    is_dir = False
    recursive = False

    def __init__(self,end_type,path,is_dir=False,recursive=False,tempdir=o.dirs.tmpDir,Atype='copy'):
        """
        Initialize connection
        """
        self.Atype = Atype
        self.end_type = end_type
        self.path = path
        self.local_file =  o.system.fs.getBaseName(self.path)
        self.tmp_local_file=o.system.fs.getTempFileName(tempdir,'FileFS-')
        o.logger.log("FileFS: path [%s] file [%s]" % (self.path,self.local_file))
        self.is_dir = is_dir
        self.recursive = recursive


    def exists(self):
        """
        Checks file or directory existance
        """

        return o.system.fs.exists(self.path)


    def upload(self,uploadPath):
        """
        Store file
        """
        if self.Atype == "move":
            if self.is_dir:
                if self.recursive:
                    o.logger.log("FileFS: (directory) Copying [%s] to path [%s] (recursively)" % (uploadPath,self.path))
                    o.system.fs.moveDir(uploadPath,self.path)
                else:
                # walk tree and move
                    for file in o.system.fs.walk(uploadPath, recurse=0):
                        o.logger.log("FileFS: (directory) Copying file [%s] to path [%s]" % (file,self.path))
                        o.system.fs.moveFile(file,self.path)
            else:
                o.system.fs.moveFile(uploadPath,self.path)
        else:
            if self.Atype == "copy":
                if self.is_dir:
                    if self.recursive:
                        o.logger.log("FileFS: (directory) Copying [%s] to path [%s] (recursively)" % (uploadPath,self.path))
                        if o.system.fs.isDir(uploadPath):
                            o.system.fs.copyDirTree(uploadPath, self.path, update=True) # was copyDir !!
                        else:
                            o.system.fs.copyFile(uploadPath, self.path) # was copyDir !!
                    else:
                    # walk tree and copy
                        for file in o.system.fs.walk(uploadPath, recurse=0):
                            o.logger.log("FileFS: (directory) Copying file [%s] to path [%s]" % (file,self.path))
                            o.system.fs.copyFile(file,self.path)
                else:
                    o.system.fs.copyFile(uploadPath,self.path)


    def download(self):
        """
        Download file
        """
        return self.path

    def cleanup(self):
        """
        If needed umount and cleanup
        """
