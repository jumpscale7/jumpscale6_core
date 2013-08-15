from OpenWizzy import o

parentclass=o.core.osis.getOsisImplementationParentClass("_coreobjects")  #is the name of the namespace

class mainclass(parentclass):
    """
    """
    def __init__(self):
        pass

    def getObject(self,ddict={}):
        obj=o.core.grid.zobjects.getZApplicationObject(ddict=ddict)
        return obj
