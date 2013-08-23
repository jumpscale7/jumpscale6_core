from JumpScale import j

class ClassBase(object):    
    """
    implement def _obj2dict to overrule serialization, output needs to be dict, reverse is _dict2obj
    """

    #def classCodePrint(self):
        #"""
        #print info like source code of class
        #"""               
        #j.code.classInfoPrint(self)

    #def classCodeEdit(self):
        #"""
        #edit this source code in Geany
        #"""               
        #j.code.classEditGeany(self)
        
    def obj2dict(self):
        return j.code.object2dict(self)
    
    def dict2obj(self,data):
        j.code.dict2object(self,data)    

        
    def __str__(self):
        return j.code.object2json(j.code.object2dict(self),True)
                
    __repr__=__str__

class PyModelBase(ClassBase):
    def dict2obj(self,data):
        j.code.dict2pymodelobject(self,data)    


class PyRootModelBase(PyModelBase):
    def getMetaInfo(self):
        """
        @return [appname,actorname,modelname,version] if relevant (e.g. for rootobject)
        """
        return self._P__meta 
