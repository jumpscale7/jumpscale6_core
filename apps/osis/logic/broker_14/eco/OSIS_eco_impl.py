from OpenWizzy import o

parentclass=o.core.osis.getOsisImplementationParentClass("_coreobjects")  #is the name of the namespace

class mainclass(parentclass):
    """
    """
    def __init__(self):
        pass       

    def getObject(self,ddict={}):
    	obj=q.errorconditionhandler.getErrorConditionObject(ddict=ddict)
        return obj

    def setObjIds(self,obj):
    	#this makes sure we store without looking for unique id
    	return [True,True,obj]