from JumpScale import j
ujson = j.db.serializers.getSerializerType('j')
parentclass=j.core.osis.getOsisImplementationParentClass("system")  #is the name of the namespace

class mainclass(parentclass):
    """
    """
    # def set(self,key,value):
    #     obj=self.getObject(value)
    #     new = False                
    #     if not obj.id:
    #         new = True
    #         obj.id = self.db.increment(1)#increment
    #     obj.getSetGuid()
    #     self.db.set(self.dbprefix,key=obj.guid,value=ujson.dumps(obj.__dict__))
    #     self.index(obj)
                        
    #     return [obj.guid,new,True]
