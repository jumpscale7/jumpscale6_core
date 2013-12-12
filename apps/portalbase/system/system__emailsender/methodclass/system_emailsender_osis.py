from JumpScale import j

class system_emailsender_osis(j.code.classGetBase()):
    """
    Email sender
    
    """
    def __init__(self):
        self.dbmem=j.db.keyvaluestore.getMemoryStore()
        self.dbfs=j.db.keyvaluestore.getFileSystemStore(namespace="emailsender", baseDir=None,serializers=[j.db.serializers.getSerializerType('j')])
        self.db=self.dbfs
    

        pass
