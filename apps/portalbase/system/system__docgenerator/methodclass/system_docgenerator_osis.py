from JumpScale import j

class system_docgenerator_osis(j.code.classGetBase()):
    """
    Initializes the swagger entry point for listing the available APIs
    
    """
    def __init__(self):
        self.dbmem=j.db.keyvaluestore.getMemoryStore()
        self.db=self.dbmem
    

        pass
