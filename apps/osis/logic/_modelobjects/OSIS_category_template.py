from OpenWizzy import o

parentclass=o.core.osis.getOsisImplementationParentClass("_modelobjects")  #is the name of the namespace

class mainclass(parentclass):
    """
    """
    def getObject(self,ddict={}):
        obj=o.core.grid.zobjects.getModelObject(ddict=ddict)
        return obj
