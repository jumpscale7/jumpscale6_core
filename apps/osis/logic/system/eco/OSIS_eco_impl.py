from JumpScale import j

parentclass=j.core.osis.getOsisImplementationParentClass("system")  #is the name of the namespace

class mainclass(parentclass):
    def set(self, key, value):
        obj = self.getObject(value)
        if obj.id==0 or len(obj.guid)>30:
            new,changed,obj=self.setObjIds(obj)        
        key=obj.guid
        ddict=obj.obj2dict()
        value=self.json.dumps(ddict)
        self.db.set(self.dbprefix, key=key, value=value)
        # if ddict.has_key("source"):
            # ddict.pop("source")
        self.index(ddict)
