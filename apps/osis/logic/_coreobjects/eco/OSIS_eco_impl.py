from JumpScale import j

parentclass=j.core.osis.getOsisImplementationParentClass("_coreobjects")  #is the name of the namespace

class mainclass(parentclass):
    """
    """
    def __init__(self):
        pass       

    def getObject(self,ddict={}):
    	obj=j.errorconditionhandler.getErrorConditionObject(ddict=ddict)
        return obj

    def setObjIds(self,obj):
    	#this makes sure we store without looking for unique id
    	return [True,True,obj]