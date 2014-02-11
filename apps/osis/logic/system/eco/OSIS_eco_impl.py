from JumpScale import j

parentclass=j.core.osis.getOsisImplementationParentClass("system")  #is the name of the namespace

class mainclass(parentclass):
    """
    """
    def set(self, key, value):
        obj = self.getObject(value)
        new,changed,obj=self.setObjIds(obj)
        key=obj.guid
        self.index(obj)
        value=self.json.dumps(obj.obj2dict())
        self.db.set(self.dbprefix, key=key, value=value)
