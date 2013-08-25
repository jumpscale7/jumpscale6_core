from JumpScale import j

parentclass=j.core.osis.getOsisImplementationParentClass("_coreobjects")  #is the name of the namespace

class mainclass(parentclass):
    """
    """
    def __init__(self):
        pass


    def getObject(self,ddict={}):
        obj=j.core.grid.zobjects.getZActionObject(ddict=ddict)
        return obj
