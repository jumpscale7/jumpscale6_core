from JumpScale import j

class system_filemanager_osis(j.code.classGetBase()):
    """
    manipulate our virtual filesystem
    
    """
    def __init__(self):
        self.dbmem=j.db.keyvaluestore.getMemoryStore()
        self.dbfs=j.db.keyvaluestore.getFileSystemStore(namespace="filemanager", baseDir=None,serializers=[j.db.serializers.getSerializerType('j')])
        self.db=self.dbfs
    

        pass
