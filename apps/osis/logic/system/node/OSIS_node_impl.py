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
        new,changed,obj=self.setObjIds(obj)
        if changed:
            print "OBJECT CHANGED WRITE"
            # print obj
            self.db.set(self.dbprefix,key=obj.guid,value=ujson.dumps(obj.__dict__))
            self.index(obj)
        j.core.osis.nodeguids[obj.machineguid]=obj.id
        return [obj.guid,new,changed]