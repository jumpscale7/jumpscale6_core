from JumpScale import j
import ujson

parentclass=j.core.osis.getOsisImplementationParentClass("system")  #is the name of the namespace

class mainclass(parentclass):
    """
    """
    def __init__(self):
        pass       

    def set(self,key,value):
        obj=self.getObject(value)
        obj.getSetGuid()
        obj.id=self.db.increment(self.dbprefix_incr)
        self.db.set(self.dbprefix,key=obj.guid,value=ujson.dumps(obj.__dict__))
        self.index(obj)
        return [obj.guid,True,True]
