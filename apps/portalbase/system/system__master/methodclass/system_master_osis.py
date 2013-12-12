from JumpScale import j

class system_master_osis(j.code.classGetBase()):
    """
    get dict of list of apps & actors
    
    """
    def __init__(self):
        self.dbmem=j.db.keyvaluestore.getMemoryStore()
        self.db=self.dbmem
    

        pass
